import requests
from bs4 import BeautifulSoup
import smtplib
import time
import sys

#Add/Change Sender Email: 
#Ask user for the email and password of the sender email and store info into a file: sender_email
def create_sender_email():

    sender_email = input(f"Please enter your '@gmail.com' email: ")
    print("")

    #Ensure user's input is a gmail
    while(sender_email[-10:] != "@gmail.com" ):
        print("ERROR: Only Gmail is supported")
        sender_email = input(f"Please enter your '@gmail.com' email: ")
        print("")

    #Ask user for password
    password = input(f"Please enter your '@gmail.com' email password: ")
    print("")

    #Write info into file: sender_email
    try:
        f = open("sender_email","w")
        f.write(f"{sender_email},{password}")
        f.close()
    except:
        sys.exit("UNEXPECTED ERROR:", sys.exc_info()[0])
    else:
        print(f"Sender email created!")


#Read sender_email file
#Return a list: [sender_email, password]
def get_sender_email():

    line = ""

    #Retrieve sender email information
    try:
        f = open("sender_email","r")
        line = f.readline().strip()
        f.close()
    except IOError:
        sys.exit(f"ERROR: No sender email has been set up. \nPlease add a sender email.\n")
    except:
        print("UNEXPECTED ERROR:", sys.exc_info()[0])
        sys.exit(f"Try adding or changing the Sender Email.\n")
    else:
        return line
    return None


#Add/change User-Agent
#Ask user for their User-Agent information and store info into a file: user_agent_info
def add_user_agent():
    
    print("Your User-Agent is required in order to identify your browser and enable the program to search for required information online." )
    print("To obtain your User-Agent, google 'get user agent' and copy paste it below.")
    print("")

    #Confirm with user about their User-Agent
    user_agent = ""
    confirmed = False
    while(confirmed == False ):
        user_agent = input(f"Please enter your User-Agent: \n")
        
        user_input = input(f"Please confirm your User-Agent: {user_agent}\nYES or NO: \n")
        if user_input.lower() == "yes":
            confirmed = True

    #Write info into file: user_agent_info
    try:
        f = open("user_agent_info","w")
        f.write(f"{user_agent}")
        f.close()
    except:
        print("UNEXPECTED ERROR:", sys.exc_info()[0])
        sys.exit(f"User-Agent is not added or changed\n")
    else:
        print(f"User agent created!\n")


#Web-scrapping the url to obtain specific information about the product
#Returns a list: [product_name, price]
def get_product_info(url):

    headers = None
    #Get information about the User-Agent
    try:
        f = open("user_agent_info","r")
        user_agent = f.readline().strip()
        f.close()
    except IOError:
        sys.exit(f"ERROR: No user-agent has been set up. \nPlease add an user-agent.\n")
    except:
        print("UNEXPECTED ERROR:", sys.exc_info()[0])
        sys.exit(f"Try adding or changing the User-Agent.\n")
    else:
        headers = {"User-Agent":user_agent}

    if headers == None:
        sys.exit(f"ERROR: No user-agent has been set up. \nPlease add an user-agent.\n")

    #Retrive website information
    try:
        page = requests.get(url, headers = headers)
    except:
        print(f"ERROR: Website does not exists")
    else:
        #check if the url exist
        if page.status_code != 200: 
            print(f"Website does not exists")
        #check if it's an amazon website
        elif "amazon.ca" in url:
            soup = BeautifulSoup(page.content, 'html.parser') #Parse and retrive information

            #Find the product name and the current product price
            try:
                product_name = soup.find(id="productTitle").get_text().strip()
                product_name = product_name.replace(',', '')

                #Get regular price or Deal price
                try:
                    price = soup.find(id="priceblock_ourprice").get_text()
                    price = price.replace(',', '')
                except AttributeError:
                    price = soup.find(id="priceblock_dealprice").get_text()
                    price = price.replace(',', '')
                
                #Convert price
                price = float(price[5:])
            except:
                print(f"ERROR: Information could not be retrieved.")
            else:
                return [product_name, price, "Amazon"]       
        elif "wishtrend.com" in url:
            soup = BeautifulSoup(page.content, 'html.parser') #Parse and retrive information

            #Find the product name and the current product price
            try:
                product_name = soup.find('div', attrs = {'class':'pdt_name'}).get_text().strip()
                product_name = product_name.replace(',', '')
                price = soup.find('div', attrs = {'class':'pdt_price'}).p.get_text().strip()
                price = price.replace(',', '')
                #Convert price
                price = float(price[1:])
            except:
                print(f"ERROR: Information could not be retrieved. {sys.exc_info()[0]}")
            else:
                return [product_name, price, "Wishtrend"]
        else:
            print(f"ERROR: Website is not compatible with the program.")
    print("")
    return None  


#Add a price alert to the price_alert file
def add_price_alert():

    product_info = ""
    alert_price = -1
    email = ""

    #Ask user for an URL and confirm that the info retrieved is correct
    confirmation = False
    while(confirmation == False ):

        #reset variables
        product_info = ""
        alert_price = -1
        email = ""

        #Ask user for an url
        url = input("Please enter the url of the product page: ")
        print("")
        
        product_info = get_product_info(url)

        if product_info == None:
            continue
        else:
            product_confirmed = product_confirmation(product_info)
            
            if product_confirmed == True:
                alert_price = alert_price_confirmation() #user's ideal price

            if alert_price >= 0:
                email = email_confirmation()
                confirmation = True
        print("")
    
    #Write price alert onto a file
    try:
        f = open("price_alert.csv","a")
        f.write(f"{product_info[0]},{product_info[2]},{alert_price},{email},{url}\n")
        f.close()
    except:
        sys.exit("UNEXPECTED ERROR:", sys.exc_info()[0])
    else:
        print(f"Price alert created! You will be notified when price drops below: {alert_price}\n")


#Confirm with the user for the product
#Return True, if it's the user's product
#Return False, otherwise
def product_confirmation(product_info):   
    
    #Display production information to user
    print("Product:", product_info[0])
    print("Current price:", product_info[1])
    
    #Ask user to confirm information
    user_input = ""
    while(user_input != "yes" and user_input != "no"):
        user_input = input("Is this your product? YES or NO: ")
        user_input = user_input.lower()
        print("")
    if user_input == "yes":
        return True
    else:
        return False


#Ask user for their alert price
#Return user's alert price
def alert_price_confirmation():
    alert_price = -1
    while alert_price < 0:
        try:
            alert_price = float(input("Enter your desired price: "))
        except:
            print("ERROR: This is not a number.")
        else:
            if alert_price < 0:
                print("It needs to be a positive number.")
        print("")   
    return alert_price


#Ask user for their alert email
def email_confirmation():
    email = ""
    email_confirmed = False
    while (email_confirmed == False):
        email = input("Please enter your email where you wish to receive notification: ")
        user_input = input(f"Is this your email: {email}? YES or NO: ")
        user_input = user_input.lower()
        if user_input == "yes":
            email_confirmed = True
        print("")
    return email


#Remove a price alert from the price-alert file
def remove_price_alert():

    num_alert = view_price_alerts()
    alert_remove = -1

    confirmation = False
    while (not confirmation):
        try:
            user_input = int(input(f"Please enter the corresponding number of the alert you want to remove. Otherwise to CANCEL, enter -1: "))
        except:
            print("Please enter a valid number.")
        else:
            if(user_input == -1):
                sys.exit(f"Thank you for using pricecheck.py!\n")
            elif (user_input > 0 and user_input <= num_alert):
                confirmation = True
                alert_remove = user_input
    
    if alert_remove == -1:
        sys.exit("UNEXPECTED ERROR!")

    product_removed_line = ""
    try:
        with open("price_alert.csv", "r") as f:
            lines = f.readlines()
        with open("price_alert.csv", "w") as f:
            number = 1
            for line in lines:
                if(number == alert_remove):
                    product_removed_line = line
                else:
                    f.write(line)
                number += 1               
    except IOError:
        sys.exit(f"ERROR: No price alert has been set up yet. \n")
    except:
        sys.exit("UNEXPECTED ERROR:", sys.exc_info()[0])
    else:
        product_removed = product_removed_line.split(',')
        print(f"Alert: {alert_remove}. Product: <<{product_removed[0]}>> has been removed from the list.\n")


#View all previously created price alerts
#Return the number of price alerts
def view_price_alerts():

    number = 0
    try:
        f = open("price_alert.csv","r")
        line = f.readline().strip()
        while line != '':
            number += 1
            alert = line.split(',')
            print(f"ALERT #{number}: \nProduct: {alert[0]} \nFrom {alert[1]} \nAlert price: {alert[2]}\n")
            line = f.readline().strip()
        f.close()
    except IOError:
        sys.exit(f"ERROR: No price alert has been set up yet. \n")
    except:
        sys.exit("UNEXPECTED ERROR:", sys.exc_info()[0])
    else:
        if number == 0:
            sys.exit(f"ERROR: No price alert has been set up yet. \n")
        print(f"Total price alerts: {number}.\n")
    return number


#View the current price of products with a price alert
def view_current_price():

    try:
        #Read file
        f = open("price_alert.csv","r")
        line = f.readline().strip()
        number = 1
        while line != '':
            line = line.split(',')

            product_info = get_product_info(line[4])

            print(f"ALERT {number}:")
            if product_info == None:
                print(f"UNEXPECTED ERROR. Information could not be retrieved.")
            else:
                print(f"Product: {product_info[0]}. \nFrom {product_info[2]}. \nCurrent price: {product_info[1]}\nAlert price: {line[2]}\n")                        

            line = f.readline().strip()
            number += 1
        f.close()
    except IOError:
        sys.exit(f"ERROR: No price alert has been set up yet. \n")
    except:
        sys.exit("UNEXPECTED ERROR:", sys.exc_info()[0])
    else:
        print("All price alerts has been shown.")


#Check the price of each product in the price alert file
def check_price():

    try:
        #Read file
        f = open("price_alert.csv","r")
        line = f.readline().strip()
        number = 1
        while line != '':
            line = line.split(',')
            
            product_info = get_product_info(line[4])
            product_name = product_info[0]
            price = product_info[1]
            
            if(price < float(line[2])):
                send_mail(product_name, product_info[2], line[2], price, line[3], line[4])                  

            line = f.readline().strip()
            number += 1
        f.close()
    except IOError:
        sys.exit(f"ERROR: No price alert has been set up yet. \n")
    except:
        sys.exit("UNEXPECTED ERROR:", sys.exc_info()[0])
        

#Sending an email
def send_mail(product, store, alert_price, current_price, alert_email, url):  
   
    #secure email account with Google 2-Step Verification and Google App Password
    #Establish a connection between our connection and gmail's connection
    server=smtplib.SMTP('smtp.gmail.com', 587 ) #Gmail's smtp
    server.ehlo() #email server to identify itself when connecting to another mail server 
    server.starttls() #encrypts connection
    server.ehlo()

    #Take information about sender in the sender_email file and login into server
    sender_info = get_sender_email()
    
    sender_data = sender_info.split(',')
    server.login(sender_data[0],sender_data[1]) #set up email

    #Write email message
    subject = f"The Price of '{product}' Dropped!"
    body = f"Hi, \n\nThe price of {product} dropped below {alert_price}. \nIt is now at {current_price}. \nStore: {store} \n\nCheck the link: {url}"

    message = f"Subject: {subject}\n\n{body}"

    
    

    try:
        server.sendmail(sender_data[0], alert_email, message)       
    except:
        print("UNEXPECTED ERROR: ", sys.exc_info()[0])
        print("unable to send email")
    #Enable if you want a print that the email was send
    #else:
        #print('Hey, an alert email has been sent!')


#main function
def main():
    print(f"\nWelcome to the pricealert.py program!\n")
    print("This program allows you to add and remove price alerts. ")
    print("An email is sent when the price of your product drops below the price alert.")
    print("There are a few options so feel free to explore them.")
    print(f"Make sure to add a sender email and your User-Agent.\n")
    

    #Prompt user to choose a correct option
    options = ["1","2","3","4","5","6","7","8","9"]
    user_option = ""
    msg = "Please choose one of the options below by entering the corresponding number."
    op1 = "1: Add/change sender email"
    op2 = "2: Add/change User-Agent"
    op3 = "3: Add a price alert"
    op4 = "4: Remove a price alert"
    op5 = "5: View all products in the price alert list"
    op6 = "6: View the current price of all products in the price alert"
    op7 = "7: Send email if price drops below the alert price (Perform once)"
    op8 = "8: Send email if price drops below the alert price (Perform once a day)"
    op9 = "9: Quit program"

    user_option = input(f"{msg}\n{op1}\n{op2}\n{op3}\n{op4}\n{op5}\n{op6}\n{op7}\n{op8}\n{op9}\nOption: ")
    print("")
    while(user_option not in options):
        print("This option is not available")
        user_option = input(f"{msg}\n{op1}\n{op2}\n{op3}\n{op4}\n{op5}\n{op6}\n{op7}\n{op8}\n{op9}\nOption: ")
        print("")

    #Option 1: Add/Change sender email
    if user_option == "1":
        create_sender_email()
    #Option 2: Add/change User-Agent
    elif user_option == "2":
        add_user_agent()    
    #Option 3: Add a price alert
    elif user_option == "3":
        add_price_alert()
    #Option 4: Remove a price alert
    elif user_option == "4":
        remove_price_alert()
    #Option 5: View all price alert
    elif user_option == "5":
        view_price_alerts()
    #Option 6: View current price of all product with an price alert
    elif user_option == "6":
        view_current_price()
    #Option 7: Send email if price drops below alert price (Perform once)
    elif user_option == "7":
        check_price()
    #Option 8: Send email if price drops below alert price (Perform once a day, nonstop)
    elif user_option == "8":
        while(True):
            check_price()
            time.sleep(60*60*24)
    #Option 9: Quit program
    elif user_option == "9":
        sys.exit(f"Thank you for using pricecheck.py!\n")


if __name__ == "__main__":
    main()


