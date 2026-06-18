<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestAuthenticatedURL.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestAuthenticatedURL.java

## Purpose
Unit-tests client-side `AuthenticatedURL` token handling, connection configuration, and cookie extraction behavior.

## Important APIs, types, and functions
Tests cover `AuthenticatedURL.Token` set/unset state, `injectToken()` adding a Cookie request property, `extractToken()` on successful and unauthorized responses, lower-case `set-cookie` response headers, connection configurator invocation, and `getAuthenticator()`.

## Control flow
Mockito mocks `HttpURLConnection` headers and response codes. Successful extraction reads `Set-Cookie`; unauthorized extraction clears the existing token and throws `AuthenticationException`.

## State and persistence
State is confined to test `Token` objects and mocked header maps. No external state is used.

## Dependencies and integration points
Exercises client code that interacts with server `AuthenticationFilter` cookies. Depends on JUnit 5 and Mockito.

## Risks and test signals
Signals include case-insensitive cookie header handling and token clearing on auth failure. Gaps include multiple cookies in one header, cookie attributes, malformed cookie values, null header maps, and redirect behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/client/TestAuthenticatedURL.java -->
