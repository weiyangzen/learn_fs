<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestPseudoAuthenticator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestPseudoAuthenticator.java

## Purpose
Tests client-side pseudo authentication against the server pseudo handler, including anonymous access behavior and POST handling.

## Important APIs, types, and functions
`getAuthenticationHandlerConfiguration()` sets `AUTH_TYPE=simple` and anonymous mode. Tests cover `PseudoAuthenticator.getUserName()`, raw server behavior with anonymous allowed/disallowed, and full `AuthenticatorTestCase._testAuthentication()` for GET and POST with anonymous allowed/disallowed.

## Control flow
The tests configure the embedded filter for simple auth, start Jetty through the shared harness, and assert expected HTTP codes or authenticated request success.

## State and persistence
Only static test filter properties and JVM `user.name` are used. No durable state exists.

## Dependencies and integration points
Depends on `AuthenticatorTestCase`, `AuthenticationFilter`, `PseudoAuthenticationHandler`, `PseudoAuthenticator`, and JUnit assertions.

## Risks and test signals
Signals include anonymous disallowed producing unauthorized filter behavior and pseudo client adding username for successful auth. Gaps include URL encoding of usernames, duplicate `user.name` query parameters, empty username values, and non-default system user names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestPseudoAuthenticator.java -->
