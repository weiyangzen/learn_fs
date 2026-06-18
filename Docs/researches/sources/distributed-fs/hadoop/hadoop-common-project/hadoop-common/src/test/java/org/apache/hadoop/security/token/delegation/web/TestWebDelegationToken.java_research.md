<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestWebDelegationToken.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestWebDelegationToken.java

## Purpose
End-to-end Jetty tests for HTTP delegation-token authentication filters and clients, covering raw HTTP operations, `DelegationTokenAuthenticatedURL`, pseudo and Kerberos auth, external secret managers, proxy users, UGI propagation, header vs query-string token transport, and IP-based proxy host checks.

## Important APIs, Types, And Functions
Defines multiple test handlers/filters/servlets: `DummyAuthenticationHandler`, `DummyDelegationTokenAuthenticationHandler`, `AFilter`, `PingServlet`, `NoDTFilter`, `NoDTHandlerDTAFilter`, `PseudoDTAFilter`, `KDTAFilter`, `UserServlet`, `UGIServlet`, and `IpAddressBasedPseudoDTAFilter`. It uses `DelegationTokenAuthenticationFilter`, `DelegationTokenAuthenticatedURL`, `MiniKdc`, `LoginContext`, and `HttpUserGroupInformation`.

## Control Flow
Tests start an embedded Jetty server on localhost, install a filter and servlet, then perform HTTP calls. Raw-call tests verify unauthenticated/authenticated access, get/renew/cancel delegation-token operations, renewer authorization, repeated cancel behavior, and delegation-token access. Client tests use `DelegationTokenAuthenticatedURL` with either header or query transport and verify UGI token pickup. Kerberos tests start `MiniKdc`, create keytabs, login through JAAS, request tokens with optional doAs, inspect token owner/real user, renew/cancel, and verify unauthorized renewal. Proxy tests validate allowed/forbidden doAs and UGI response content.

## State And Persistence
State includes an embedded Jetty server per test, UGI global security configuration reset in setup/cleanup, optional `MiniKdc` work directories and keytabs, in-memory token secret managers, and tokens attached to the current UGI.

## Dependencies And Integration Points
Depends on Jetty, Hadoop auth filters/handlers, Jackson, MiniKdc/Kerberos utilities, servlet APIs, UGI, delegation token secret managers, and HTTP URL connections. It is the broadest integration coverage for Hadoop web delegation-token auth.

## Risks
These tests are environment- and timing-sensitive due to Jetty ports, Kerberos setup, localhost/IP proxy matching, and global UGI state. URL query construction is manual in places, so encoding edge cases are not deeply covered. Token-in-UGI behavior can leak if the current UGI is shared across tests.

## Test Signals
Signals include HTTP 200/401/403/404 responses, JSON token URL strings, expected token kind, header/query marker response headers, external secret-manager token kind, fallback behavior when a filter lacks delegation-token support, Kerberos GSS failure before login and success after login, owner/real-user fields for doAs, proxy authorization outcomes, UGI response strings, and IP-based proxy success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestWebDelegationToken.java -->
