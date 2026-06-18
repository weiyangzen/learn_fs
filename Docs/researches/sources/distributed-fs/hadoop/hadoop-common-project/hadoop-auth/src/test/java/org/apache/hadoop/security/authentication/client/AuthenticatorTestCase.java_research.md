<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/AuthenticatorTestCase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/AuthenticatorTestCase.java

## Purpose
Provides an embedded Jetty test harness for client authenticator integration tests against `AuthenticationFilter`.

## Important APIs, types, and functions
`setAuthenticationHandlerConfig()` supplies filter configuration to `TestFilter`. `startJetty()` creates a Jetty server under `/foo`, installs the authentication filter, and serves `/bar` with `TestServlet`. `_testAuthentication()` verifies `AuthenticatedURL` behavior for GET/POST, connection configurator invocation, cookie token reuse, and echo POSTs. `_testAuthenticationHttpClient()` configures Apache HttpClient with SPNEGO support and validates GET plus optional non-repeatable POST entity behavior.

## Control flow
Each test starts Jetty on a free local port, performs authenticated client operations, and stops/destroys the server in a finally block. The POST path writes request bytes and expects the servlet to echo them.

## State and persistence
State is test-local Jetty server, host/port, servlet context, and static authenticator properties. No durable state is written.

## Dependencies and integration points
Used by pseudo and Kerberos client tests. Depends on Jetty, servlet APIs, Apache HttpClient/SPNEGO, `AuthenticationFilter`, `AuthenticatedURL`, and test connection configurators.

## Risks and test signals
Static configuration can bleed between tests if not reset. Free-port selection has a bind race. Signals include successful cookie reuse, no renegotiation for non-repeatable POST entities, configurator invocation, and proper server teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/AuthenticatorTestCase.java -->
