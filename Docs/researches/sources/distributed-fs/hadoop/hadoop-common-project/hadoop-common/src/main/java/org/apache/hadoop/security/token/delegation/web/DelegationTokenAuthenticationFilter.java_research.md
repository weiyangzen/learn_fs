<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticationFilter.java

Source read size: 309 lines, 12843 bytes.

## Purpose
Servlet authentication filter that wires Hadoop HTTP authentication to delegation-token-aware handlers and exposes the authenticated request as a Hadoop `UserGroupInformation`.

## Important APIs, Types, and Functions
Extends `AuthenticationFilter`. Important members include `DELEGATION_TOKEN_SECRET_MANAGER_ATTR`, `getConfiguration()`, `setAuthHandlerClass()`, `getProxyuserConfiguration()`, `init()`, `initializeAuthHandler()`, static `getDoAs()`, static `getHttpUserGroupInformationInContext()`, and overridden `doFilter()`.

## Control Flow, State, and Persistence Behavior
Initialization rewrites configured auth type from pseudo/kerberos/multi-scheme to the corresponding delegation-token handler, injects an external secret manager from the servlet context when present, establishes SIMPLE or KERBEROS auth method metadata, and refreshes proxy-user config. During handler initialization it temporarily exposes a shared Curator client to the ZK secret manager. `doFilter()` builds UGI from the authenticated principal, applies `doAs` proxy authorization unless the request was authenticated by delegation token, stores UGI in a thread local, wraps servlet principal/auth methods, and clears the thread local in finally.

## Dependencies and Integration Points
Integrates Hadoop Auth `AuthenticationFilter`, pseudo/Kerberos/multi-scheme handlers, `ProxyUsers`, `ZKSignerSecretProvider`, `ZKDelegationTokenSecretManager`, servlet APIs, and X-Hadoop delegation-token server handlers.

## Risks and Test Signals
Risks include thread-local leaks if wrapping changes bypass finally, proxy-user parsing from raw query strings, handler type detection for subclasses, and external secret-manager lifecycle ownership. Test handler class rewriting, external secret-manager injection, Curator handoff, proxy authorization success/failure, delegation-token UGI bypassing proxy rewrite, wrapped principal values, and cleanup of `UGI_TL` after exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticationFilter.java -->
