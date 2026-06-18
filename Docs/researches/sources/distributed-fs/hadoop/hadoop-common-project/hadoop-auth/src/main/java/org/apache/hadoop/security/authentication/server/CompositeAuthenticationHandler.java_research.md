# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/CompositeAuthenticationHandler.java

Purpose: extension interface for authentication handlers that can issue or accept more than one token type.

Important APIs, types, and functions: extends `AuthenticationHandler` and adds `Collection<String> getTokenTypes()`.

Control flow: `AuthenticationFilter.verifyTokenType()` checks this interface and accepts cookies whose token type matches any returned type instead of only `handler.getType()`.

State and persistence: interface has no state. Implementations define supported token type collections.

Dependencies and integration points: used by multi-scheme handlers and the filter's token validation logic.

Risks and test signals: returned collections must include every token type an implementation may issue, or valid cookies will be rejected. Test signals include filter token verification for composite vs single-type handlers.
