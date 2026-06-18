# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/webapp/WEB-INF/web.xml

Purpose: deployment descriptor for the Hadoop Auth example web application.

Important APIs, types, and functions: declares `WhoServlet` and maps it to `/anonymous/who`, `/simple/who`, and `/kerberos/who`. Declares `RequestLoggerFilter` plus three `AuthenticationFilter` instances: anonymous simple auth, non-anonymous simple auth, and Kerberos auth. Init params configure auth type, anonymous allowance, token validity, Kerberos principal, and keytab.

Control flow: all requests pass through `requestLoggerFilter`; `/anonymous/*`, `/simple/*`, and `/kerberos/*` then pass through their respective auth filters before reaching the servlet.

State and persistence: no persistent application state. Auth filters issue signed cookies according to their configured token validity.

Dependencies and integration points: integrates servlet container deployment with Hadoop auth server filter and the example servlet/filter classes.

Risks and test signals: Kerberos principal/keytab are hard-coded sample values and must be changed for real deployment. Token validity is short at 30 seconds for examples. Test signals are successful deployment and distinct behavior across anonymous, simple, and Kerberos paths.
