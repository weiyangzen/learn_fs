<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAuthenticationToken.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAuthenticationToken.java

## Purpose
Tests the server-facing `AuthenticationToken.ANONYMOUS` singleton.

## Important APIs, types, and functions
`testAnonymous()` asserts that the anonymous token exists, has null user/principal/type, has expiration `-1`, and is not expired.

## Control flow
Single assertion-only unit test; no setup or teardown.

## State and persistence
Reads static anonymous token state only. No persistence exists.

## Dependencies and integration points
Depends on `AuthenticationToken` and JUnit assertions. Covers behavior inherited from `AuthToken` anonymous construction.

## Risks and test signals
Signal is narrow but protects anonymous-token contract relied on by pseudo and whitelist authentication paths. Gaps include normal token serialization/parsing, max-inactive behavior, equality, and mutation of anonymous token state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAuthenticationToken.java -->
