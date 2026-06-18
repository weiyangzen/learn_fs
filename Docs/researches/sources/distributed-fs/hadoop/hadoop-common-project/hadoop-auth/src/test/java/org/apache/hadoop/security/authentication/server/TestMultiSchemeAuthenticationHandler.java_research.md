# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestMultiSchemeAuthenticationHandler.java

Purpose: Tests `MultiSchemeAuthenticationHandler`, which advertises and dispatches multiple HTTP authentication schemes, configured here as `Basic` backed by LDAP and `Negotiate` backed by Kerberos.

Important APIs and control flow: the test creates an embedded LDAP server through ApacheDS annotations and manually starts a `KerberosSecurityTestcase` MiniKDC in `setUp()`. `getDefaultProperties()` sets `SCHEMES_PROPERTY`, per-scheme `AUTH_HANDLER_PROPERTY` values, Kerberos principal/keytab/name rules, and LDAP base/provider URL. Tests call `handler.authenticate` for missing authorization, malformed authorization, valid LDAP Basic credentials, and invalid Kerberos Negotiate data.

State and dependencies: state spans two external test services: ApacheDS and MiniKDC, plus a generated keytab and handler sub-handlers. Dependencies include Hadoop Kerberos and LDAP handlers, servlet mocks, `HttpConstants`, Apache Directory, and Commons Codec.

Integration points: verifies that missing or unusable authorization adds both `WWW-Authenticate` challenges (`Basic` and `Negotiate`) and returns 401. The valid Basic path confirms dispatch to LDAP and token type `ldap`; the invalid Negotiate path confirms dispatch to Kerberos and propagation of `AuthenticationException`.

Risks and test signals: the test does not exercise a fully valid Kerberos SPNEGO success through the multi-scheme wrapper, only invalid Kerberos dispatch and valid LDAP dispatch. It also starts/stops MiniKDC separately from the ApacheDS extension, so teardown ordering is significant. Exact scheme strings and property keys are strong compatibility signals for production configuration.
