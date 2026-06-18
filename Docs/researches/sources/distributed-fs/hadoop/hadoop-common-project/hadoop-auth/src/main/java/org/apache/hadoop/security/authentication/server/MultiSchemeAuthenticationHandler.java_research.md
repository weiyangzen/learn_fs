<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/MultiSchemeAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/MultiSchemeAuthenticationHandler.java

## Purpose
Provides a composite server authentication handler that advertises and dispatches multiple HTTP authentication schemes, such as `Negotiate` and `Basic`, while preserving the token types of the delegated handlers.

## Important APIs, types, and functions
`SCHEMES_PROPERTY` configures the comma-separated scheme list, and `AUTH_HANDLER_PROPERTY` maps each scheme to a handler type/class. `getTokenTypes()` exposes delegated token types to `AuthenticationFilter`. `init()` normalizes schemes through `AuthenticationHandlerUtil.checkAuthScheme()`, resolves handler class names, instantiates them through the context class loader, initializes them with the same config, and stores scheme-to-handler mappings. `authenticate()` matches the incoming Authorization scheme and delegates to the selected handler.

## Control flow
Initialization fails if no scheme list exists, if a scheme is duplicated, or if a scheme lacks a handler mapping. Authentication loops configured schemes only when an Authorization header is present. A matching scheme delegates the whole request/response to its handler; otherwise the response gets `401` and one `WWW-Authenticate` header for each configured scheme.

## State and persistence
State is in-memory maps/sets: `schemeToAuthHandlerMapping`, supported token `types`, and `authType`. `destroy()` cascades to all delegated handlers. No state is persisted.

## Dependencies and integration points
Uses Guava `Splitter`, servlet APIs, `AuthenticationHandlerUtil`, and the `CompositeAuthenticationHandler` contract. It is configured through `AuthenticationFilter.AUTH_TYPE=multi-scheme` and shares the same properties with all child handlers.

## Risks and test signals
The class logs all config entries at info level, which can expose secrets such as keytabs, LDAP URLs, or signer values. `authenticate()` logs `token.getType()` without guarding against a delegated null token, so in-progress multi-step handlers can trigger a null dereference. Tests should cover duplicate schemes, case normalization, missing handler mappings, invalid scheme names, multiple `WWW-Authenticate` headers, delegated null tokens, and destroy ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/MultiSchemeAuthenticationHandler.java -->
