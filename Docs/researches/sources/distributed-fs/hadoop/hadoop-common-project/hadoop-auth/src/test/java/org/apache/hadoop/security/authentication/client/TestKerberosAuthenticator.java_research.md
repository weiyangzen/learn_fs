<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestKerberosAuthenticator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestKerberosAuthenticator.java

## Purpose
Integration and unit tests for the client-side Kerberos/SPNEGO authenticator, including fallback to pseudo auth and multi-scheme handler operation.

## Important APIs, types, and functions
`setup()` creates client and server principals in the MiniKDC keytab. Helper methods build Kerberos and multi-scheme filter configs. Tests cover pseudo fallback with and without anonymous access, unauthenticated `401` Negotiate challenge, Kerberos GET/POST through `AuthenticatedURL`, Apache HttpClient SPNEGO GET/POST, multi-scheme Negotiate configuration, exception wrapping, and private `isNegotiate()`/`readToken()` handling for normal and lower-case headers.

## Control flow
Kerberos integration tests run client operations inside `KerberosTestUtils.doAsClient()`. The embedded Jetty filter is configured for Kerberos or multi-scheme auth and expected to issue/accept signed auth cookies after SPNEGO negotiation.

## State and persistence
State includes MiniKDC principals and the shared keytab file. Test configuration is static through `AuthenticatorTestCase`.

## Dependencies and integration points
Depends on MiniKDC, Kerberos test utilities, `AuthenticationFilter`, `KerberosAuthenticationHandler`, `MultiSchemeAuthenticationHandler`, `PseudoAuthenticationHandler`, Apache Commons reflection utilities, Mockito, and JUnit timeouts.

## Risks and test signals
Signals cover end-to-end SPNEGO, cookie reuse for POST, multi-scheme challenge handling, and lower-case header compatibility. Gaps include malformed SPNEGO server tokens, expired Kerberos credentials, proxy/redirect behavior, and multiple `WWW-Authenticate` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestKerberosAuthenticator.java -->
