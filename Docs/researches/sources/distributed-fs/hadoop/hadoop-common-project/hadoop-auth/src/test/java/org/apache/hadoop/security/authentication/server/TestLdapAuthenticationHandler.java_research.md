# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestLdapAuthenticationHandler.java

Purpose: Integration-style unit tests for `LdapAuthenticationHandler`, verifying HTTP Basic authentication against an embedded Apache Directory LDAP server populated with one user entry.

Important APIs and control flow: class-level ApacheDS annotations create an LDAP server, partition, base DN, and LDIF entry `uid=bjones` with password `p@ssw0rd`. `setup()` initializes `LdapAuthenticationHandler` using `BASE_DN` and `PROVIDER_URL`. Tests call `authenticate(request, response)` with missing, malformed, valid, invalid, and wrong credentials. Credentials are base64-encoded and prefixed with `Basic` only on complete cases.

State and dependencies: runtime state is the in-process LDAP directory, handler instance, and mocked servlet request/response. Dependencies include Apache Directory test extensions, Commons Codec `Base64`, servlet APIs, Hadoop LDAP constants, and `AuthenticationException`.

Integration points: confirms unauthenticated requests receive `WWW-Authenticate: Basic` and `401`, valid LDAP bind yields an `AuthenticationToken` of handler `TYPE` with username/name `bjones` and HTTP 200, incomplete auth returns null, and wrong password raises `AuthenticationException`.

Risks and test signals: because it spins up ApacheDS, failures can reflect embedded server startup or port binding rather than handler logic. Timeouts limit hangs. The invalid-authorization test supplies base64 credentials without the `Basic` scheme, intentionally asserting that malformed headers are challenged rather than bound.
