# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/PseudoAuthenticator.java

Purpose: client-side Hadoop simple/pseudo authenticator that sends the local Java `user.name` as a query parameter.

Important APIs, types, and functions: constant `USER_NAME` is `user.name`. `setConnectionConfigurator()` stores optional connection setup. `authenticate()` appends `user.name=<getUserName()>` to the URL, sends an OPTIONS request, and calls `AuthenticatedURL.extractToken()`. `getUserName()` returns `System.getProperty("user.name")` and can be overridden.

Control flow: every call constructs a URL with the username parameter, opens a configured connection through the token, connects, and extracts the issued auth cookie.

State and persistence: only stores the optional configurator. Token state remains in `AuthenticatedURL.Token`.

Dependencies and integration points: integrates with server-side `PseudoAuthenticationHandler`, `AuthenticatedURL`, and `ConnectionConfigurator`. Covered by `TestPseudoAuthenticator`.

Risks and test signals: username is appended without URL encoding, so unusual usernames can break the query string. It trusts a local system property and is not strong authentication. Test signals include URLs with and without existing query strings, overridden usernames, configurator propagation, and error response handling.
