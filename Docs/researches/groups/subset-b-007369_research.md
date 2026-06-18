# subset-b-007369 Research

Grouped research for `subset-b-007369`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/AbstractDelegationTokenSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/AbstractDelegationTokenSecretManager.java

Source read size: 1141 lines, 36805 bytes.

## Purpose
Base secret manager for Hadoop delegation tokens. It creates token passwords from rolling master keys, tracks live token metadata, validates/renews/cancels tokens, expires old tokens, and exposes hook methods for HDFS/RM and external persistence implementations.

## Important APIs, Types, and Functions
The class extends `SecretManager<TokenIdent>` for `AbstractDelegationTokenIdentifier` subtypes. Key APIs are `startThreads()`, `stopThreads()`, `createPassword()`, `retrievePassword()`, `verifyToken()`, `renewToken()`, `cancelToken()`, `addKey()`, `addPersistedDelegationToken()`, `rollMasterKey()`, and persistence hooks such as `storeDelegationKey()`, `storeToken()`, `updateToken()`, and `removeStoredToken()`. Nested `DelegationTokenInformation` serializes renew date, password, and optional tracking id. Nested metrics track store/update/remove latency and failures.

## Control Flow, State, and Persistence Behavior
`startThreads()` creates an initial key, marks the manager running, and launches `ExpiredTokenRemover`. Token creation assigns issue/max dates, master key id, and a sequence number under a fair read/write API lock, then stores token metadata. Renewal decodes the token, checks max lifetime, renewer, master key, and password, then extends renew time up to max date. Cancellation authorizes owner or renewer, removes the token, updates owner stats, and calls persistence hooks. The remover thread periodically rolls master keys and scans candidates for expired tokens. Default persistence is in-memory, while subclasses override hooks for edit logs, SQL, or ZK.

## Dependencies and Integration Points
Depends on Hadoop `Token`, `SecretManager`, `AbstractDelegationTokenIdentifier`, `DelegationKey`, `WritableUtils`, `HadoopKerberosName`, metrics2, IOStatistics, and daemon/thread utilities. HDFS and YARN/RM plug persistence through protected hook methods; web, SQL, and ZK managers build on the same API.

## Risks and Test Signals
Risks include lock ordering around persistence hooks, fatal JVM exit if the remover thread throws unexpectedly, sequence/key counter correctness in subclasses, and owner-stat drift when external caches are refreshed. Test signals include key rolling, recovery with missing keys, password mismatch, renewer authorization, cancel authorization, expired-token removal, persistence hook failures, metrics failure increments, and top owner stats after add/remove/sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/AbstractDelegationTokenSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/AbstractDelegationTokenSelector.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/AbstractDelegationTokenSelector.java

Source read size: 61 lines, 2113 bytes.

## Purpose
Generic selector that finds the first delegation token matching a requested service and token kind from a credentials token collection.

## Important APIs, Types, and Functions
Implements `TokenSelector<TokenIdent>`. The constructor captures the delegation token kind as a `Text`. `selectToken(Text service, Collection<Token<? extends TokenIdentifier>> tokens)` returns a cast `Token<TokenIdent>` whose `getKind()` and `getService()` both match.

## Control Flow, State, and Persistence Behavior
The selector is stateless except for the immutable intended kind name. It returns `null` immediately for a null service, then performs a linear scan over the supplied token collection. There is no persistence or caching.

## Dependencies and Integration Points
Used by Hadoop clients and services that need to locate a service-specific delegation token in `Credentials`. It integrates with `Token`, `TokenIdentifier`, `TokenSelector`, `Text`, and concrete delegation token identifier classes that define kind values.

## Risks and Test Signals
Risks are mostly API-contract issues: the unchecked cast assumes kind implies identifier type, duplicate matching tokens return the first one only, and null token collections are not tolerated. Test with null service, empty collections, kind mismatch, service mismatch, multiple matches preserving iteration order, and concrete selector subclasses for HDFS/MapReduce token kinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/AbstractDelegationTokenSelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/DelegationKey.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/DelegationKey.java

Source read size: 145 lines, 4076 bytes.

## Purpose
Writable value object for delegation-token master keys. It carries a key id, expiry date, and encoded secret key bytes used to generate or verify token passwords.

## Important APIs, Types, and Functions
Constructors accept either a `SecretKey` or encoded bytes. Accessors include `getKeyId()`, `getExpiryDate()`, `setExpiryDate()`, `getKey()`, and `getEncodedKey()`. `write()` and `readFields()` define the wire/storage form; `equals()` and `hashCode()` compare id, expiry, and key bytes. `MAX_KEY_LEN` bounds deserialized key material at 1 MiB.

## Control Flow, State, and Persistence Behavior
The object is simple mutable state. Serialization writes variable-length key id and expiry, then `-1` for null key bytes or length plus bytes. Deserialization uses `WritableUtils.readVIntInRange()` to reject oversized material before allocating.

## Dependencies and Integration Points
Delegation key maps in `AbstractDelegationTokenSecretManager`, SQL rows, and ZK znodes all serialize this type. It depends on Hadoop `WritableUtils`, Java crypto `SecretKey`, and `AbstractDelegationTokenSecretManager.createSecretKey()` to reconstruct usable secrets.

## Risks and Test Signals
Risks include exposing raw encoded key bytes through `getEncodedKey()`, equality depending on expiry as well as key id, and runtime exceptions for oversized constructor input. Test serialization round trips with null/non-null keys, max-length rejection, secret-key reconstruction, expiry mutation, hash/equals behavior, and compatibility with SQL/ZK persisted bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/DelegationKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/DelegationTokenLoadingCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/DelegationTokenLoadingCache.java

Source read size: 118 lines, 3478 bytes.

## Purpose
Map-like wrapper around a Guava `LoadingCache` for delegation-token metadata. It lets SQL-backed secret managers avoid loading every token into memory while preserving the `currentTokens` map contract expected by the base manager.

## Important APIs, Types, and Functions
The constructor configures `expireAfterWrite`, `maximumSize`, and a `CacheLoader` backed by a `Function<K,V>`. Implemented `Map` methods include `size()`, `isEmpty()`, `containsKey()`, `get()`, `put()`, `remove()`, `putAll()`, `clear()`, `keySet()`, `values()`, and `entrySet()`. `containsValue()` is intentionally unsupported.

## Control Flow, State, and Persistence Behavior
`get()` invokes the loader on a miss and returns null on any loader exception. `containsKey()` only checks present cache entries and does not trigger loading. `entrySet()` and related views expose only cached entries, not the entire persistent store. Persistent data remains in the backing store used by the supplied function.

## Dependencies and Integration Points
Used by `SQLDelegationTokenSecretManager` as its `currentTokens` implementation. Depends on Hadoop's shaded Guava cache and Java functional interfaces.

## Risks and Test Signals
Risks include subtle differences from a full `Map`: cleanup scans only cached entries unless SQL overrides candidate cleanup, `get()` hides loader failures, and `size()` is approximate/cast to int. Test cache miss loading, expiry eviction, max-size eviction, put/remove invalidation, `containsKey()` no-load behavior, unsupported `containsValue()`, and SQL manager cancellation loading a token before base validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/DelegationTokenLoadingCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/SQLDelegationTokenSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/SQLDelegationTokenSecretManager.java

Source read size: 483 lines, 19271 bytes.

## Purpose
SQL-backed delegation token secret manager for HA services that share tokens, keys, and sequence counters through an external relational database.

## Important APIs, Types, and Functions
Extends `AbstractDelegationTokenSecretManager`. It overrides token, key, and counter accessors and declares abstract SQL operations: `selectTokenInfo()`, `selectStaleTokenInfos()`, `insertToken()`, `updateToken()`, `deleteToken()`, `selectDelegationKey()`, `insertDelegationKey()`, `updateDelegationKey()`, `deleteDelegationKey()`, `selectSequenceNum()`, `updateSequenceNum()`, `incrementSequenceNum()`, `selectKeyId()`, `updateKeyId()`, and `incrementKeyId()`.

## Control Flow, State, and Persistence Behavior
Construction derives timing from delegation-token config and replaces `currentTokens` with `DelegationTokenLoadingCache`. Token store/update serializes `DelegationTokenInformation`, writes SQL first, then updates the local cache. Cancellation decodes and loads the token so the base manager can validate it. Cleanup asks SQL for stale rows by modification time, deserializes candidates, and double-checks renew date before deleting expired rows. Sequence numbers are locally batched from SQL; unused numbers in a batch are intentionally not reusable. Keys are cached locally but lazily fetched from SQL on miss.

## Dependencies and Integration Points
Requires concrete subclasses to implement database-specific SQL semantics and concurrency-safe counter increments. Integrates with `DelegationTokenManager` timing config, `DelegationKey`, `Token`, `Writable` serialization, and base manager metrics/hook flow.

## Risks and Test Signals
Risks include SQL transaction isolation around counter increments, duplicate insert handling, cache staleness, swallowed delete failures, and cleanup races with renewal by another router. Test concurrent managers allocating sequence/key ids, token store/update/cancel round trips, cache miss loading, stale cleanup with renewed token preservation, missing token `NoSuchElementException`, key lazy load, SQL exception conversion, and batch-boundary sequence allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/SQLDelegationTokenSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/ZKDelegationTokenSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/ZKDelegationTokenSecretManager.java

Source read size: 881 lines, 33114 bytes.

## Purpose
ZooKeeper-backed delegation token secret manager for HA services. It stores master keys and token records in znodes, uses Curator shared counters for id allocation, and optionally watches token/key znode changes into local caches.

## Important APIs, Types, and Functions
Key APIs are `createCuratorClient()`, `startThreads()`, `stopThreads()`, `incrementDelegationTokenSeqNum()`, `incrementCurrentKeyId()`, `getDelegationKey()`, `getTokenInfo()`, `storeDelegationKey()`, `updateDelegationKey()`, `storeToken()`, `updateToken()`, `removeStoredToken()`, `cancelToken()`, and `isTokenWatcherEnabled()`. Static config constants cover ZK connection/auth/SSL, znode path, retry/session timeouts, sequence batch size, and token watcher behavior.

## Control Flow, State, and Persistence Behavior
Construction either uses a thread-local external Curator client or creates one. `startThreads()` starts Curator, shared counters, persistent roots, key cache, optional token cache, loads cache contents, then starts base key-rolling/removal threads. Token sequence numbers are reserved in batches from `SharedCount`; key ids increment one at a time. Key/token znodes are named with `DK_` and `DT_` prefixes and contain writable-serialized data. Reads check local maps first, then ZK. Deletion uses guaranteed deletes and can double-check renew date to avoid removing a token renewed by a peer.

## Dependencies and Integration Points
Depends on Apache Curator caches/shared counters, Hadoop ZK client/auth helpers, Kerberos/SSL configuration, `DelegationTokenManager` timing keys, and the base secret manager. Web filters can inject the same Curator used by `ZKSignerSecretProvider`.

## Risks and Test Signals
Risks include watcher lag or missed events, znode ACL mistakes when namespace parents are implicit, sequence gaps from batching, infinite retry loops in shared-count updates, runtime exceptions on ZK write failures, and local owner stats needing sync after cache reload. Test external and owned Curator modes, SSL/Kerberos config, cache load with corrupt nodes, watcher create/update/delete events, sequence batch boundaries, key lookup fallback, token renewal/delete races, watcher disabled mode, and shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/ZKDelegationTokenSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/package-info.java

Source read size: 26 lines, 1151 bytes.

## Purpose
Package metadata for `org.apache.hadoop.security.token.delegation`, marking the delegation-token framework as public and evolving.

## Important APIs, Types, and Functions
The file contains package annotations only: `@InterfaceAudience.Public` and `@InterfaceStability.Evolving`.

## Control Flow, State, and Persistence Behavior
There is no executable control flow or state. The annotations describe the compatibility contract for classes in the package, including secret managers, selectors, keys, and persistence variants.

## Dependencies and Integration Points
Depends only on Hadoop classification annotations. Downstream users rely on these annotations to understand that the package is intended for public use but may still evolve.

## Risks and Test Signals
Risks are documentation/API-contract drift if classes in the package become less stable than the package annotation implies. Test signal is primarily build/javadoc/package annotation validation rather than runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticatedURL.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticatedURL.java

Source read size: 486 lines, 19328 bytes.

## Purpose
Client-side `AuthenticatedURL` extension that automatically uses Hadoop delegation tokens for HTTP/S connections and exposes helper methods to get, renew, and cancel delegation tokens.

## Important APIs, Types, and Functions
Nested `Token` extends `AuthenticatedURL.Token` with a Hadoop delegation token field. Constructors install a `DelegationTokenAuthenticator` defaulting to `KerberosDelegationTokenAuthenticator`. Important methods are `openConnection()`, `selectDelegationToken()`, `getDelegationToken()`, `renewDelegationToken()`, `cancelDelegationToken()`, `setDefaultDelegationTokenAuthenticator()`, and deprecated `setUseQueryStringForDelegationToken()`.

## Control Flow, State, and Persistence Behavior
When no authenticated cookie token is set, `openConnection()` searches current UGI credentials for a token whose service matches the URL host/port. It sends that token in `X-Hadoop-Delegation-Token` by default or in the `delegation` query parameter for WebHDFS compatibility. Optional `doAs` is appended to the query string. Management helpers delegate to the configured authenticator and keep the nested token's delegation-token field in sync.

## Dependencies and Integration Points
Integrates Hadoop `Credentials`, `SecurityUtil`, `UserGroupInformation`, `AuthenticatedURL`, `DelegationTokenAuthenticator`, and web delegation-token server handlers.

## Risks and Test Signals
Risks include non-thread-safe token state, URL parameter construction that assumes values are already correctly encoded except `doAs`, service matching sensitivity to URL ports, and clearing cached delegation tokens after renewal failures. Test token selection by service, header vs query-string transport, proxy-user parameter, fallback authentication when no token exists, get/renew/cancel flows, and behavior with existing auth cookies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticatedURL.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticationHandler.java

Source read size: 423 lines, 16844 bytes.

## Purpose
Server-side authentication handler decorator that adds delegation-token management and token-based authentication to an underlying HTTP auth mechanism such as Kerberos or pseudo auth.

## Important APIs, Types, and Functions
Implements `AuthenticationHandler`. Key methods are `init()`, `initTokenManager()`, `initJsonFactory()`, `managementOperation()`, `authenticate()`, `isManagementOperation()`, `destroy()`, and `setExternalDelegationTokenSecretManager()`. It recognizes token ops from `KerberosDelegationTokenAuthenticator`: get, renew, and cancel.

## Control Flow, State, and Persistence Behavior
Initialization starts the wrapped handler, creates a `DelegationTokenManager` for configured token kind, and optionally configures Jackson generator features. Management operations validate HTTP method, authenticate with the wrapped handler when Kerberos credentials are required, build proxy UGI for `doAs`, and execute create/renew/cancel through the token manager. Successful get/renew responses are JSON. Normal authentication first checks delegation token header or query parameter, verifies the token, creates an ephemeral `AuthenticationToken`, and stores the token UGI on the request; otherwise it falls back to the wrapped handler.

## Dependencies and Integration Points
Depends on Hadoop Auth server interfaces, `DelegationTokenManager`, `ProxyUsers`, servlet APIs, Jackson, `HttpExceptionUtils`, and client-side operation names shared with `DelegationTokenAuthenticator`.

## Risks and Test Signals
Risks include management-op method mismatches, exposing cancel without Kerberos credentials by design, JSON feature misconfiguration, broad `Throwable` catch during token auth becoming 403, and proxy authorization failures. Test all three operations, missing token parameter errors, bad token decode, method mismatch, doAs success/failure, JSON response shape, header vs query token auth, and fallback handler invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticator.java

Source read size: 358 lines, 14344 bytes.

## Purpose
Client-side `Authenticator` wrapper that skips normal HTTP authentication when a delegation token is present and implements REST operations for obtaining, renewing, and canceling delegation tokens.

## Important APIs, Types, and Functions
Important constants define query/header names and JSON fields: `op`, `delegation`, `token`, `renewer`, `service`, `X-Hadoop-Delegation-Token`, `Token`, `urlString`, and `long`. The `DelegationTokenOperation` enum maps operations to HTTP methods and whether Kerberos credentials are required. Public methods are `authenticate()`, `getDelegationToken()`, `renewDelegationToken()`, `cancelDelegationToken()`, and `setConnectionConfigurator()`.

## Control Flow, State, and Persistence Behavior
`authenticate()` detects a delegation token either in the nested URL token object or in the query string. Without one it checks/relogs in the current UGI TGT and delegates to the wrapped authenticator. Management operations build a URL with encoded parameters, temporarily clear delegation token state when real credentials are required, open an `AuthenticatedURL`, set the required method, validate HTTP 200, and parse JSON if a response is expected. No persistent state is owned beyond the wrapped authenticator/configurator references.

## Dependencies and Integration Points
Wraps Hadoop Auth client authenticators, normally Kerberos or pseudo. Integrates with `DelegationTokenAuthenticatedURL`, `SecurityUtil`, `JsonSerialization`, `HttpExceptionUtils`, and the server handler's REST contract.

## Risks and Test Signals
Risks include substring-based query detection for `delegation=`, unchecked JSON casts, URL assembly with parameter order from `HashMap`, clearing/restoring token state around Kerberos-required ops, and cancellation converting unexpected auth exceptions to IOExceptions. Test each operation URL/method, JSON content-type validation, non-JSON response, delegation-token bypass, TGT relogin path, doAs encoding, and restoration of token state after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenIdentifier.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenIdentifier.java

Source read size: 64 lines, 2117 bytes.

## Purpose
Concrete web delegation-token identifier whose token kind is supplied at construction time by `DelegationTokenManager`.

## Important APIs, Types, and Functions
Extends `AbstractDelegationTokenIdentifier`. Constructors accept a token kind alone or kind plus owner, renewer, and real user. The only override is `getKind()`, returning the configured `Text`.

## Control Flow, State, and Persistence Behavior
The class stores token kind and inherits all identifier serialization fields and behavior from the abstract parent. There is no persistence logic here; instances are serialized inside Hadoop `Token` identifiers and decoded by the manager.

## Dependencies and Integration Points
Used by `DelegationTokenManager`, web authentication handlers, and filters. Integrates with `Text` token kinds configured through `delegation-token.token-kind`.

## Risks and Test Signals
Risks are limited: null or inconsistent token kind can break token selection and verification, and inherited serialization must remain compatible. Test `getKind()`, constructor field propagation, token encode/decode through the manager, and behavior with multiple token kinds in one process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenIdentifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenManager.java

Source read size: 233 lines, 8442 bytes.

## Purpose
Facade used by HTTP authentication handlers to create, renew, cancel, and verify web delegation tokens while hiding whether the underlying secret manager is local in-memory or ZooKeeper-backed.

## Important APIs, Types, and Functions
Important config keys are `zk-dt-secret-manager.enable` and timing keys under `delegation-token.*`. Nested `DelegationTokenSecretManager` and `ZKSecretManager` create `DelegationTokenIdentifier` instances and decode tokens with the configured kind. Public APIs are `setExternalDelegationTokenSecretManager()`, `init()`, `destroy()`, `createToken()`, `renewToken()`, `cancelToken()`, `verifyToken()`, and `getDelegationTokenSecretManager()`.

## Control Flow, State, and Persistence Behavior
Construction chooses ZK or local secret manager and marks it managed. `init()` starts managed secret-manager threads; `destroy()` stops them. External secret-manager injection stops the initially created manager and transfers lifecycle ownership to the caller. Token creation derives owner/real user from UGI, defaults renewer to the caller short name, creates a Hadoop `Token`, and optionally sets its service. Cancel uses the verifier to infer canceller when none is supplied.

## Dependencies and Integration Points
Integrates web handlers with `AbstractDelegationTokenSecretManager`, `ZKDelegationTokenSecretManager`, `DelegationTokenIdentifier`, `UserGroupInformation`, and Hadoop `Token`.

## Risks and Test Signals
Risks include raw generic casts, lifecycle confusion when replacing secret managers, token kind mismatch during decode, and default renewer behavior affecting authorization. Test local vs ZK construction, managed lifecycle, external manager replacement, create with service/real user, renew authorization, cancel with explicit and inferred canceller, verify password failure, and token kind mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/HttpUserGroupInformation.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/HttpUserGroupInformation.java

Source read size: 41 lines, 1544 bytes.

## Purpose
Small public utility for code running inside Hadoop HTTP request handling to retrieve the current request's `UserGroupInformation`.

## Important APIs, Types, and Functions
The only API is static `get()`, which delegates to `DelegationTokenAuthenticationFilter.getHttpUserGroupInformationInContext()`.

## Control Flow, State, and Persistence Behavior
No state is owned by this class. It reads the filter-managed thread-local UGI and returns null when the current thread is not processing an authenticated request through the delegation-token filter.

## Dependencies and Integration Points
Depends on `UserGroupInformation` and the filter's thread-local context. It is a bridge for servlets and HTTP endpoints that need Hadoop identity rather than only servlet principals.

## Risks and Test Signals
Risks include callers assuming non-null outside filter scope or after asynchronous thread handoff. Test within authenticated requests, delegation-token-authenticated requests, proxy-user requests, unauthenticated requests, and worker threads that do not inherit the filter context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/HttpUserGroupInformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/KerberosDelegationTokenAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/KerberosDelegationTokenAuthenticationHandler.java

Source read size: 54 lines, 2410 bytes.

## Purpose
Concrete delegation-token HTTP authentication handler that wraps Kerberos/SPNEGO authentication.

## Important APIs, Types, and Functions
Extends `DelegationTokenAuthenticationHandler`. The constructor supplies a `KerberosAuthenticationHandler` whose type is suffixed with `-dt`. `getType()` is inherited from the wrapped handler.

## Control Flow, State, and Persistence Behavior
There is no custom runtime flow beyond the parent class. All token management, token verification, JSON responses, and fallback authentication are handled by `DelegationTokenAuthenticationHandler`; Kerberos/SPNEGO supplies the real credential checks for operations that require credentials.

## Dependencies and Integration Points
Used by `DelegationTokenAuthenticationFilter` when `auth.type=kerberos`. Integrates with Hadoop Auth's `KerberosAuthenticationHandler`, web token manager, servlet filter, and Kerberos client authenticator.

## Risks and Test Signals
Risks are configuration-level: Kerberos principal/keytab setup must be correct, and the suffixed type must still align with filter/client expectations. Test filter auth-type rewrite, SPNEGO-protected get/renew operations, cancel behavior, fallback authentication, and token-authenticated request bypass after a token is issued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/KerberosDelegationTokenAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/KerberosDelegationTokenAuthenticator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/KerberosDelegationTokenAuthenticator.java

Source read size: 46 lines, 1852 bytes.

## Purpose
Client-side delegation-token authenticator for Kerberos/SPNEGO-backed Hadoop HTTP endpoints.

## Important APIs, Types, and Functions
Extends `DelegationTokenAuthenticator` and constructs it with a `KerberosAuthenticator`.

## Control Flow, State, and Persistence Behavior
All behavior is inherited from `DelegationTokenAuthenticator`: perform SPNEGO only when no delegation token is present, and use Kerberos credentials for get/renew operations. The class owns no additional state.

## Dependencies and Integration Points
Used as the default authenticator by `DelegationTokenAuthenticatedURL`. Integrates with Hadoop Auth `KerberosAuthenticator` and server-side `KerberosDelegationTokenAuthenticationHandler`.

## Risks and Test Signals
Risks are inherited from the generic authenticator plus Kerberos environment sensitivity. Test default authenticator instantiation, SPNEGO handshake on token acquisition, no-handshake data requests when a token exists, renew requiring credentials, cancel not requiring credentials, and propagation of Kerberos IO/auth failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/KerberosDelegationTokenAuthenticator.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/PseudoDelegationTokenAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/PseudoDelegationTokenAuthenticationHandler.java

Source read size: 55 lines, 2477 bytes.

## Purpose
Delegation-token HTTP authentication handler for Hadoop simple/pseudo authentication deployments.

## Important APIs, Types, and Functions
Extends `DelegationTokenAuthenticationHandler` by wrapping a `PseudoAuthenticationHandler` with type suffix `-dt`.

## Control Flow, State, and Persistence Behavior
The parent handler implements all token management and token verification. The wrapped pseudo handler supplies simple user-name based authentication for management operations and fallback requests. No additional state or persistence is introduced here.

## Dependencies and Integration Points
Selected by `DelegationTokenAuthenticationFilter` when the configured auth type is pseudo/simple. Integrates with `PseudoDelegationTokenAuthenticator` clients and the same `DelegationTokenManager` used for Kerberos mode.

## Risks and Test Signals
Risks are mostly security posture: pseudo auth trusts request user identity, so token issuance is only appropriate where simple auth is acceptable. Test filter rewrite, simple user token issuance, renew/cancel authorization, token-authenticated request identity, and doAs proxy authorization in pseudo mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/PseudoDelegationTokenAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/PseudoDelegationTokenAuthenticator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/PseudoDelegationTokenAuthenticator.java

Source read size: 54 lines, 2018 bytes.

## Purpose
Client-side delegation-token authenticator for Hadoop simple/pseudo HTTP authentication.

## Important APIs, Types, and Functions
Extends `DelegationTokenAuthenticator` and constructs it with a `PseudoAuthenticator`.

## Control Flow, State, and Persistence Behavior
All operational flow is inherited. Without a delegation token it authenticates using the pseudo authenticator, typically by sending the user name expected by Hadoop Auth; with a token it bypasses normal auth and uses the token header or query parameter.

## Dependencies and Integration Points
Pairs with `PseudoDelegationTokenAuthenticationHandler` and can be installed in `DelegationTokenAuthenticatedURL` where simple auth is desired.

## Risks and Test Signals
Risks are inherited from pseudo authentication and delegation-token URL construction. Test pseudo-auth token acquisition, delegation-token bypass on subsequent requests, renew and cancel calls, doAs handling, and failure propagation from non-200 or non-JSON server responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/PseudoDelegationTokenAuthenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/ServletUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/ServletUtils.java

Source read size: 61 lines, 2111 bytes.

## Purpose
Servlet helper for robust request parameter lookup in delegation-token HTTP handlers.

## Important APIs, Types, and Functions
The single public API is `getParameter(HttpServletRequest request, String name)`. It wraps `request.getParameter(name)` and only treats `IllegalArgumentException` specially.

## Control Flow, State, and Persistence Behavior
The method returns the request parameter value normally. If the servlet container throws `IllegalArgumentException`, usually due to invalid query-string encoding, it converts that into an `IOException` carrying the parameter name. No state is stored.

## Dependencies and Integration Points
Used by token authentication handlers when reading `op`, `delegation`, `token`, `renewer`, `service`, and related query parameters. Depends only on servlet request APIs.

## Risks and Test Signals
Risks include losing the original exception type and only covering `IllegalArgumentException`, not other container parsing failures. Test valid parameters, missing parameters, malformed encodings that trigger `IllegalArgumentException`, repeated parameters according to servlet container behavior, and callers converting the IOException to proper HTTP errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/ServletUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/package-info.java

Source read size: 26 lines, 1065 bytes.

## Purpose
Package metadata for Hadoop security token APIs, declaring the package public and evolving.

## Important APIs, Types, and Functions
The file contains `@InterfaceAudience.Public` and `@InterfaceStability.Evolving` annotations for `org.apache.hadoop.security.token`.

## Control Flow, State, and Persistence Behavior
There is no executable logic. The annotations describe the intended API audience/stability for token classes such as `Token`, `TokenIdentifier`, `TokenSelector`, and `SecretManager`.

## Dependencies and Integration Points
Depends on Hadoop classification annotations and informs generated docs, API compatibility review, and downstream use of token APIs.

## Risks and Test Signals
Risk is only API-contract drift between package annotation and concrete classes. Test signal is build/javadoc/package annotation presence rather than runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/AbstractService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/AbstractService.java

Source read size: 490 lines, 13995 bytes.

## Purpose
Base implementation of Hadoop's `Service` lifecycle. It provides synchronized state transitions, configuration storage, listener notifications, lifecycle history, failure recording, stop waiting, and blocker tracking.

## Important APIs, Types, and Functions
Implements `Service`. Public/final lifecycle APIs are `init()`, `start()`, `stop()`, `close()`, `waitForServiceToStop()`, state/failure/config accessors, listener registration, `isInState()`, and blocker getters. Subclass hooks are `serviceInit()`, `serviceStart()`, and `serviceStop()`.

## Control Flow, State, and Persistence Behavior
`init()` requires non-null config, enters `INITED`, sets config, invokes `serviceInit()`, and notifies listeners if still in `INITED`. `start()` enters `STARTED`, records start time, invokes `serviceStart()`, and notifies. `stop()` enters `STOPPED`, invokes `serviceStop()`, sets termination notification, wakes waiters, and notifies. Failures record first cause/state, call quiet stop for init/start failures, and convert exceptions to `ServiceStateException`. State is in `ServiceStateModel`; lifecycle events and blockers are in-memory only.

## Dependencies and Integration Points
Used throughout Hadoop services and by `CompositeService`, `ServiceLauncher`, and shutdown hooks. Depends on `Configuration`, `ServiceOperations.ServiceListeners`, `LifecycleEvent`, and `ServiceStateModel`.

## Risks and Test Signals
Risks include listener exceptions being swallowed, wait timeout semantics that return after one wait cycle, hooks that change state during callbacks, and static global listeners affecting tests. Test valid/invalid transitions, null config, hook failure cleanup, listener ordering/local/global notification, lifecycle history, wait/notify behavior, blocker map snapshots, and idempotent init/start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/AbstractService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/CompositeService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/CompositeService.java

Source read size: 190 lines, 6173 bytes.

## Purpose
Service implementation that owns a list of child services and initializes, starts, and stops them as a unit.

## Important APIs, Types, and Functions
Extends `AbstractService`. Key methods are `getServices()`, protected `addService()`, `addIfService()`, `removeService()`, `serviceInit()`, `serviceStart()`, `serviceStop()`, private `stop()`, and nested `CompositeServiceShutdownHook`.

## Control Flow, State, and Persistence Behavior
Child services are stored in a synchronized list. Initialization iterates a snapshot in insertion order and calls `init(conf)`. Start likewise starts in insertion order. Stop walks services in reverse order and, by default, stops both `STARTED` and `INITED` children. It records the first stop exception but continues stopping remaining children, then rethrows a converted exception. No persistent state is owned.

## Dependencies and Integration Points
Used by Hadoop daemons and compound subsystems. Integrates with `AbstractService` hooks, `ServiceOperations.stopQuietly()`, and JVM shutdown hooks.

## Risks and Test Signals
Risks include services added after init/start not being included in current snapshot, policy choice to stop `INITED` children, and first-exception-only reporting. Test ordering, reverse stop, partial start failure cleanup, remove behavior, addIfService with non-service objects, shutdown hook invocation, and stop continuing after child failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/CompositeService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/LifecycleEvent.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/LifecycleEvent.java

Source read size: 43 lines, 1412 bytes.

## Purpose
Serializable data holder recording a service lifecycle transition time and resulting state.

## Important APIs, Types, and Functions
The class exposes public fields `time` and `state` and implements `Serializable`.

## Control Flow, State, and Persistence Behavior
There is no behavior beyond holding values. `AbstractService` creates one event after each real state transition and stores it in an in-memory history list.

## Dependencies and Integration Points
Depends on `Service.STATE`. Used by `Service.getLifecycleHistory()` for diagnostics and tests.

## Risks and Test Signals
Risks include public mutable fields and no serialVersionUID-specific compatibility guarantees beyond the declared id. Test signals are history entries after init/start/stop, timestamp ordering, state values, and defensive copying by `AbstractService.getLifecycleHistory()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/LifecycleEvent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/LoggingStateChangeListener.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/LoggingStateChangeListener.java

Source read size: 64 lines, 1982 bytes.

## Purpose
Simple `ServiceStateChangeListener` implementation that logs service state changes.

## Important APIs, Types, and Functions
Constructors accept default logging or custom `Logger` and `Level`. `stateChanged(Service service)` logs service name and new state at the configured level.

## Control Flow, State, and Persistence Behavior
The listener is stateless except for logger and level references. It is called synchronously by `ServiceOperations.ServiceListeners` during service notifications and has no persistence.

## Dependencies and Integration Points
Integrates with `AbstractService` local/global listener registration and SLF4J logging. It is useful for daemon diagnostics and tests that need visible lifecycle transitions.

## Risks and Test Signals
Risks are low: logging at an unavailable level or expensive service `toString()`/name access during notification. Test constructor defaults, custom level behavior, registration as local and global listener, and resilience when multiple services emit state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/LoggingStateChangeListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/Service.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/Service.java

Source read size: 225 lines, 6953 bytes.

## Purpose
Public lifecycle contract for Hadoop services. It defines legal states, lifecycle operations, configuration access, listener registration, failure diagnostics, lifecycle history, and blocker reporting.

## Important APIs, Types, and Functions
The `STATE` enum is `NOTINITED`, `INITED`, `STARTED`, and `STOPPED`. Methods include `init()`, `start()`, `stop()`, `close()`, `waitForServiceToStop()`, `getServiceState()`, `getName()`, `getConfig()`, `getStartTime()`, listener registration, `isInState()`, `getFailureCause()`, `getFailureState()`, `getLifecycleHistory()`, and `getBlockers()`.

## Control Flow, State, and Persistence Behavior
This interface defines behavior but owns no implementation. The documented lifecycle is initialize once, start once, stop once, with idempotent calls in existing states. Implementations such as `AbstractService` enforce transitions and maintain in-memory diagnostics.

## Dependencies and Integration Points
Core contract used by Hadoop daemons, composite services, launchers, shutdown hooks, and test utilities. Depends on `Configuration`, `LifecycleEvent`, and listener interfaces.

## Risks and Test Signals
Risks are implementer compliance: wrong transition handling, non-idempotent stop, blocking waits, or inconsistent failure metadata. Test any implementation against state transitions, listener callbacks, config availability, close delegating to stop, wait semantics, and immutable history/blocker snapshots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/Service.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceOperations.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceOperations.java

Source read size: 173 lines, 5725 bytes.

## Purpose
Utility methods and listener container for working with `Service` instances, mainly safe stopping and robust listener notification.

## Important APIs, Types, and Functions
Static APIs are `stop(Service)`, `stopQuietly(Service)`, deprecated `stopQuietly(Log, Service)`, and `stopQuietly(Logger, Service)`. Nested `ServiceListeners` supports `add()`, `remove()`, `reset()`, and `notifyListeners(Service)`.

## Control Flow, State, and Persistence Behavior
`stop()` simply calls `service.stop()` if non-null. Quiet variants catch `Exception`, log a warning, and return the exception. `ServiceListeners` maintains a synchronized list, ignores duplicate registrations, snapshots listeners before notification, and invokes callbacks outside the synchronized block so listeners may register/unregister during callbacks. No persistent state exists.

## Dependencies and Integration Points
Used by `AbstractService`, `CompositeService`, shutdown hooks, and cleanup paths. Integrates with SLF4J and legacy commons logging.

## Risks and Test Signals
Risks include `stopQuietly(Logger, null)` being safe but logging paths assuming service non-null only after an exception, listener callback exceptions propagating to callers of `notifyListeners()`, and no Throwable catching in stop utilities. Test null stop, exception return/logging, duplicate listeners, mutation during notification, reset, callback ordering, and interaction with `AbstractService` listener exception handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateChangeListener.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateChangeListener.java

Source read size: 50 lines, 1819 bytes.

## Purpose
Callback interface for receiving service lifecycle state changes.

## Important APIs, Types, and Functions
The single method is `stateChanged(Service service)`.

## Control Flow, State, and Persistence Behavior
Implementations are invoked synchronously by service listener containers after state transitions. The interface owns no state or persistence.

## Dependencies and Integration Points
Used by `AbstractService`, `ServiceOperations.ServiceListeners`, and `LoggingStateChangeListener`. Enables daemon diagnostics, testing hooks, and cross-service coordination.

## Risks and Test Signals
Risks are implementation-side: slow or throwing listeners can delay or disrupt notification unless the caller catches exceptions. Test callback invocation on init/start/stop, removal before notification, duplicate registration handling, and exception handling in the service that owns the listener list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateChangeListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateException.java

Source read size: 127 lines, 4046 bytes.

## Purpose
Runtime exception used when service lifecycle operations fail or invalid state transitions are attempted. It can also carry launcher exit-code semantics.

## Important APIs, Types, and Functions
Constructors accept message, cause, and optional exit code. `getExitCode()` exposes the exit status. Static `convert(Throwable)` and `convert(String, Throwable)` wrap checked exceptions unless the fault is already a runtime exception.

## Control Flow, State, and Persistence Behavior
The class stores an integer exit code, defaulting to a service-specific launcher failure code. Conversion methods preserve existing runtime exceptions and wrap other throwables with message/cause. No persistence is involved.

## Dependencies and Integration Points
Used by `AbstractService`, `CompositeService`, and `ServiceStateModel` when lifecycle transitions or hooks fail. Integrates with launcher exit-code interfaces.

## Risks and Test Signals
Risks include runtime exceptions bypassing wrapping and therefore not gaining a service exit code, and callers losing checked-exception type information. Test constructors, exit-code propagation, conversion of IOException/Exception, pass-through of RuntimeException, and messages from invalid service transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateModel.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateModel.java

Source read size: 165 lines, 5021 bytes.

## Purpose
Small synchronized state machine that enforces legal Hadoop `Service` lifecycle transitions.

## Important APIs, Types, and Functions
Important methods are `getState()`, `isInState()`, `ensureCurrentState()`, `enterState()`, `checkStateTransition()`, `isValidStateTransition()`, and `toString()`. It stores the service name and current `Service.STATE`.

## Control Flow, State, and Persistence Behavior
Initial state is `NOTINITED`. `enterState()` validates transition unless the proposed state equals current, then updates state and returns the old state. Valid transitions include `NOTINITED -> INITED/STOPPED`, `INITED -> STARTED/STOPPED`, and `STARTED -> STOPPED`; `STOPPED` is terminal except re-entry. State is in-memory only.

## Dependencies and Integration Points
Used by `AbstractService` to implement lifecycle methods and by tests that directly validate state transition rules. Throws `ServiceStateException` for invalid states.

## Risks and Test Signals
Risks include transition-matrix drift from `Service` documentation and direct callers treating re-entry as a real transition. Test every valid/invalid transition, re-entry behavior, `ensureCurrentState()`, concurrent `enterState()` calls, and exception messages including service names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateModel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/AbstractLaunchableService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/AbstractLaunchableService.java

Source read size: 80 lines, 2396 bytes.

## Purpose
Convenience base class for services that can be launched by Hadoop's service launcher. It combines `AbstractService` lifecycle support with default `LaunchableService` methods.

## Important APIs, Types, and Functions
Extends `AbstractService` and implements `LaunchableService`. Provides default `bindArgs(Configuration, List<String>)` and `execute()`.

## Control Flow, State, and Persistence Behavior
`bindArgs()` logs command-line arguments at debug level and returns the configuration unchanged. `execute()` returns `LauncherExitCodes.EXIT_SUCCESS`. The class owns no persistent state beyond the inherited service state.

## Dependencies and Integration Points
Used by launchable Hadoop daemons and tools that want lifecycle plus command execution. Integrates with `ServiceLauncher`, `LaunchableService`, `Configuration`, and launcher exit codes.

## Risks and Test Signals
Risks include subclasses forgetting to override `execute()` for real work or leaking sensitive arguments in debug logs. Test default bind/execute behavior, subclass overrides, lifecycle inherited behavior, and launcher handling of the success code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/AbstractLaunchableService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/HadoopUncaughtExceptionHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/HadoopUncaughtExceptionHandler.java

Source read size: 129 lines, 4390 bytes.

## Purpose
Default JVM uncaught exception handler for Hadoop service launchers. It logs uncaught failures and terminates or halts the process for serious `Error` conditions.

## Important APIs, Types, and Functions
Implements `Thread.UncaughtExceptionHandler`. Constructors optionally accept a delegate handler. The main API is `uncaughtException(Thread, Throwable)`.

## Control Flow, State, and Persistence Behavior
During JVM shutdown it only logs. Outside shutdown, `Error` triggers process termination: `OutOfMemoryError` prints to stderr and calls `ExitUtil.haltOnOutOfMemory()`, while other errors are converted to an `ExitException` through `ServiceLauncher` and terminated. Non-`Error` exceptions are logged and optionally delegated. No persistent state is owned.

## Dependencies and Integration Points
Intended for installation by launcher main methods. Integrates with `ShutdownHookManager`, `ExitUtil`, `ServiceLauncher.convertToExitException()`, and optional external exception handlers.

## Risks and Test Signals
Risks include abrupt termination bypassing cleanup, logging failures during fatal errors, and policy choice not to terminate on ordinary exceptions. Test shutdown-in-progress branch, OOM halt branch with exit utilities intercepted, generic Error conversion, simple Exception delegation, null delegate behavior, and logging resilience.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/HadoopUncaughtExceptionHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/InterruptEscalator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/InterruptEscalator.java

Source read size: 217 lines, 7191 bytes.

## Purpose
Signal-interrupt coordinator for launched services. It handles the first interrupt by asking the service launcher to shut down and escalates repeated interrupts or shutdown timeouts to forced halt.

## Important APIs, Types, and Functions
Implements `IrqHandler.Interrupted`. Important methods are `interrupted()`, `register(String)`, `lookup(String)`, `isForcedShutdownTimedOut()`, and `isSignalAlreadyReceived()`. Nested `ServiceForcedShutdown` waits for a service to stop and flags timeout.

## Control Flow, State, and Persistence Behavior
Registered signal names create `IrqHandler` instances stored in a list. On first signal, an atomic flag is set, a forced-shutdown monitor thread is started, and the owning `ServiceLauncher` is asked to exit with `EXIT_INTERRUPTED`. If another signal arrives while shutdown is already underway, it halts the JVM immediately. State is process-local: weak owner reference, registered handlers, atomic flags, and timeout indicator.

## Dependencies and Integration Points
Works with `ServiceLauncher`, `Service`, `IrqHandler`, `SubjectInheritingThread`, `ExitUtil`, and launcher exit codes. It is part of daemon process shutdown behavior.

## Risks and Test Signals
Risks include owner weak reference becoming null, forced halt making cleanup impossible, signal registration unsupported under `-Xrs`, and timeout tuning too short for slow services. Test first vs second signal behavior, registered handler lookup, service stop wait timeout, null owner/service paths, forced halt interception, and multiple signal names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/InterruptEscalator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/IrqHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/IrqHandler.java

Source read size: 176 lines, 4582 bytes.

## Purpose
Wrapper around JVM signal handling that binds a named signal to a Hadoop callback and records how many times it has fired.

## Important APIs, Types, and Functions
Implements `SignalUtil.Handler`. Important methods are `bind()`, `raise()`, `handle()`, `getName()`, `getSignalCount()`, and `toString()`. Nested `Interrupted` is the callback interface, and nested `InterruptData` carries signal name and number.

## Control Flow, State, and Persistence Behavior
Construction validates signal name and callback. `bind()` creates a `SignalUtil.Signal` and registers this handler, rejecting double binding and wrapping unsupported signal setup with an explanatory `IllegalArgumentException`. `handle()` increments an atomic count, creates `InterruptData`, logs, and calls the callback. `raise()` triggers the bound signal. State is in-memory only.

## Dependencies and Integration Points
Used by `InterruptEscalator` to wire signals such as TERM/INT into launcher shutdown logic. Depends on Hadoop `SignalUtil`, `Preconditions`, and SLF4J.

## Risks and Test Signals
Risks include JVM/platform signal portability, unsupported signal handling with `-Xrs`, callback exceptions propagating from signal handling, and `raise()` before successful bind. Test constructor validation, bind once, unsupported signal errors, callback data content, signal count increments, raise behavior, and integration with `InterruptEscalator`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/IrqHandler.java -->
