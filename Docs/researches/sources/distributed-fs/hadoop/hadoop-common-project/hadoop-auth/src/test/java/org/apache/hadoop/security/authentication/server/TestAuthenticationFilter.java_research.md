<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAuthenticationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAuthenticationFilter.java

## Purpose
Unit-tests the core server `AuthenticationFilter` lifecycle, configuration parsing, signer-provider selection, cookie token validation, request wrapping, expiration/inactivity behavior, and management-operation short circuiting.

## Important APIs, types, and functions
`DummyAuthenticationHandler` simulates success, failure, expiration, and management operation outcomes. Tests cover config-prefix stripping, missing auth type, random/file/custom signer providers, empty secret-file fallback, cookie domain/path, case-insensitive auth type, request URL reconstruction, signed token parsing, expired/invalid token rejection, unauthenticated responses, successful authentication cookie issuance, invalid cookie replacement, wrapped remote user/principal, failure clearing cookies, max-inactive interval renewal, and management operations.

## Control flow
Most tests initialize a filter with mocked `FilterConfig`/`ServletContext`, build mocked servlet requests/responses, and verify response headers/status or filter-chain invocation. Signed cookies are produced with `Signer` and parsed back through `AuthenticationToken`.

## State and persistence
State is mocked servlet context attributes, temporary secret files, generated cookies, and filter fields. Cookies represent externally persisted auth state for the duration of requests.

## Dependencies and integration points
Exercises `AuthenticationFilter`, `AuthenticationHandler`, `AuthenticationToken`, `AuthenticatedURL.AUTH_COOKIE`, `Signer`, `SignerSecretProvider`, and `StringSignerSecretProviderCreator`. Depends on Mockito, AssertJ, and JUnit.

## Risks and test signals
Signals are strong for cookie signing, expiry, inactivity renewal, and lifecycle behavior. Gaps include real servlet-container header casing, concurrent requests during secret rollover, malformed cookie parsing beyond simple invalid strings, SameSite/Secure/HttpOnly attributes, and custom provider failure modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAuthenticationFilter.java -->
