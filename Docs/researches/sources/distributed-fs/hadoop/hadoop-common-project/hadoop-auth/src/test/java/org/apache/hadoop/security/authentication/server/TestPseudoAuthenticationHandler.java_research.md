# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestPseudoAuthenticationHandler.java

Purpose: Unit tests for simple pseudo authentication, where a username can be supplied through the pseudo-auth query parameter and anonymous access may be enabled or disabled.

Important APIs and control flow: tests instantiate `PseudoAuthenticationHandler`, initialize it with `ANONYMOUS_ALLOWED`, inspect `getAcceptAnonymous` and `getType`, and call `authenticate(request, response)`. `_testUserName` parameterizes the username path for anonymous enabled and disabled modes by mocking `request.getQueryString()` as `user.name=user` via `PseudoAuthenticator.USER_NAME`.

State and dependencies: state is confined to the handler instance and mocked servlet request/response. Dependencies are JUnit, Mockito, servlet APIs, `PseudoAuthenticator`, and `AuthenticationToken`.

Integration points: verifies anonymous mode returns `AuthenticationToken.ANONYMOUS`, non-anonymous mode without a username returns null, and a query-string username always produces a token with name/user `user` and handler type `simple`.

Risks and test signals: tests do not assert response headers/status for missing credentials, focusing only on token return values. The query parsing assertion is a direct signal for compatibility between client-side `PseudoAuthenticator.USER_NAME` and server handler parsing.
