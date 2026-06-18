<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/MultiSchemeDelegationTokenAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/MultiSchemeDelegationTokenAuthenticationHandler.java

Source read size: 183 lines, 7911 bytes.

## Purpose
Delegation-token authentication handler for servers that advertise multiple HTTP authentication schemes and want only selected schemes to be allowed for delegation-token management operations.

## Important APIs, Types, and Functions
Extends `DelegationTokenAuthenticationHandler` and implements `CompositeAuthenticationHandler`. Important APIs are `getTokenTypes()`, `init(Properties)`, and overridden `authenticate()`. Config key `multi-scheme-auth-handler.delegation.schemes` lists schemes accepted for token management.

## Control Flow, State, and Persistence Behavior
Initialization parses the underlying multi-scheme auth list and the delegation-token scheme list, normalizes scheme names, and asserts delegation schemes are a subset of configured auth schemes. During authentication, management operations without an Authorization header for an allowed scheme receive 401 with `WWW-Authenticate` headers for the allowed delegation schemes. Valid management auth and all non-management requests fall through to the parent handler.

## Dependencies and Integration Points
Wraps `MultiSchemeAuthenticationHandler`, Hadoop Auth scheme utilities, servlet auth headers, and the shared delegation-token manager. Used by the filter when `auth.type=multi-scheme`.

## Risks and Test Signals
Risks include config nulls causing initialization failure, scheme normalization mismatches, preemptive auth with a disallowed scheme, and management-op detection sharing query parsing with other handlers. Test allowed/disallowed schemes, missing auth header challenge, delegation scheme not in configured schemes, normal non-management auth, token-authenticated requests, and all management operation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/MultiSchemeDelegationTokenAuthenticationHandler.java -->
