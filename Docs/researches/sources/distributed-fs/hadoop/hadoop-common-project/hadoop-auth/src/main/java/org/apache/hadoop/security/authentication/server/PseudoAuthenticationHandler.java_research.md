<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/PseudoAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/PseudoAuthenticationHandler.java

## Purpose
Implements Hadoop "simple" pseudo-authentication for HTTP by trusting a `user.name` query parameter, with optional anonymous access.

## Important APIs, types, and functions
`TYPE` is `simple`; `ANONYMOUS_ALLOWED` controls anonymous fallback. `init()` reads the boolean flag. `getUserName()` parses the raw query string with `URLEncodedUtils` and UTF-8, returning the first `PseudoAuthenticator.USER_NAME` value. `authenticate()` returns anonymous, null with a forbidden response/challenge, or a new `AuthenticationToken` with user and principal set to the query value.

## Control flow
For each request, the handler parses the query string. Missing username returns `AuthenticationToken.ANONYMOUS` when anonymous mode is enabled; otherwise it sets `403` and `WWW-Authenticate: PseudoAuth` and returns null. Present username is accepted without external verification.

## State and persistence
Only `acceptAnonymous` and token `type` are kept in memory. There is no persistence and no external credential state.

## Dependencies and integration points
Used by `AuthenticationFilter` for simple auth and by client-side `PseudoAuthenticator`, including Kerberos client fallback paths. It relies on Apache HttpComponents query parsing.

## Risks and test signals
The mechanism intentionally trusts caller-supplied identity and should be limited to trusted environments. Risks include duplicate `user.name` parameters, empty values, URL encoding edge cases, and inconsistent status mapping through the filter. Tests should cover anonymous allowed/disallowed paths, GET/POST behavior, query decoding, multiple usernames, empty username values, and interaction with signed auth cookies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/PseudoAuthenticationHandler.java -->
