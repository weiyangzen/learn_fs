# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/java/org/apache/hadoop/security/authentication/examples/WhoClient.java

Purpose: command-line example client that uses `AuthenticatedURL` to call a Hadoop Auth-protected endpoint and print the token, status, and body.

Important APIs, types, and functions: `main(String[] args)` validates one URL argument, creates `AuthenticatedURL.Token`, opens an authenticated connection through `new AuthenticatedURL().openConnection(url, token)`, prints token and HTTP status, and streams response lines on HTTP 200.

Control flow: execution is linear; authentication happens inside `AuthenticatedURL`, then the code reads only successful responses. Exceptions print an error and exit nonzero.

State and persistence: token state lives in memory for this single process invocation. No token is persisted.

Dependencies and integration points: depends on Hadoop auth client classes, `HttpURLConnection`, URL parsing, and UTF-8 input reading. Configured as the exec plugin main class in the examples POM.

Risks and test signals: prints the auth token to stdout, which is acceptable for an example but not safe for real clients. It does not URL-encode or retry itself. Test signal is running it against `/anonymous/who`, `/simple/who`, and `/kerberos/who` endpoints in the example WAR.
