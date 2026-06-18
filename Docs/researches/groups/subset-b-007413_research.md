# Group Research: subset-b-007413

This grouped report covers the Hadoop KMS server files assigned to `subset-b-007413`. Each section preserves the original source path and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMS.java

## Purpose
`KMS.java` is the Jersey REST resource for Hadoop KMS. It exposes the versioned KMS API rooted at `KMSRESTConstants.SERVICE_VERSION` and translates HTTP calls into `KeyProviderCryptoExtension` operations for creating, deleting, rolling, reading, generating encrypted keys, decrypting encrypted keys, and reencryption.

## Important APIs, Types, and Functions
The `KMSOp` enum names auditable server operations: key management, metadata reads, key version reads, encrypted-key generation, decryption, and reencryption. The constructor obtains the process-wide provider and audit service from `KMSWebApp`. Endpoint methods include `createKey`, `deleteKey`, `rolloverKey`, `invalidateCache`, `getKeysMetadata`, `getKeyNames`, `getMetadata`, `getCurrentVersion`, `getKeyVersion`, `generateEncryptedKeys`, `handleEncryptedKeyOp`, `reencryptEncryptedKeys`, and `getKeyVersions`.

## Control Flow
Every endpoint follows a common shape: obtain the authenticated `UserGroupInformation` through `HttpUserGroupInformation`, validate required fields using `KMSUtil.checkNotEmpty` or `checkNotNull`, assert a KMS ACL through `KMSACLs`, run provider calls inside `user.doAs`, update meters from `KMSWebApp`, audit success, and return JSON via `KMSUtil` or `KMSServerJSONUtils`. Mutations call `provider.flush()` after create, delete, roll, and cache invalidation. EEK handling branches by the `eek_op` query parameter: generate returns a list of encrypted key versions, decrypt returns a decrypted key version, and reencrypt returns an updated encrypted key version or batch list.

## State and Persistence
This class stores only references to the static webapp provider and audit service. Persistent state is held by the backing `KeyProvider`; mutation flushes are the main durability boundary. Cache invalidation delegates to the provider wrapper. The class also increments Dropwizard meters, producing process-local metric state.

## Dependencies and Integration Points
It depends on Jersey annotations, Hadoop KMS REST constants, `KeyProviderCryptoExtension`, `KMSWebApp`, `KMSACLs`, `KMSAudit`, `KMSClientProvider` JSON-compatible value types, Base64 decoding for supplied key material and EEK payloads, and `UserGroupInformation` proxy execution. Responses are serialized by `KMSJSONWriter`.

## Risks
Security correctness depends on both the coarse KMS ACL checks here and the optional per-key wrapper configured in `KMSWebApp`. `getKeyVersion` checks only the global GET ACL before provider access, relying on `KeyAuthorizationKeyProvider` for per-key READ enforcement. `reencryptEncryptedKeys` warns but does not reject payloads larger than `MAX_NUM_PER_BATCH`, so protection is observational rather than limiting. User-provided key material is decoded without explicit length validation in this layer. Audit calls generally occur after successful provider operations; failures are handled by `KMSExceptionsProvider`.

## Test Signals
Relevant tests should cover ACL denial, key-material gating with `SET_KEY_MATERIAL`, provider flush after mutation, JSON shape compatibility, EEK op validation, batch reencryption input validation, and interaction with `KeyAuthorizationKeyProvider`. `MiniKMS` exercises this resource through an embedded server, and `KMSBenchmark` stresses generate/decrypt operations through provider APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSACLs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSACLs.java

## Purpose
`KMSACLs.java` owns KMS authorization policy. It loads global KMS operation ACLs, optional operation blacklists, per-key ACLs, default key ACLs, and whitelist key ACLs from `kms-acls.xml`, and can hot-reload them while the server is running.

## Important APIs, Types, and Functions
The `Type` enum defines global ACL categories: `CREATE`, `DELETE`, `ROLLOVER`, `GET`, `GET_KEYS`, `GET_METADATA`, `SET_KEY_MATERIAL`, `GENERATE_EEK`, and `DECRYPT_EEK`. `INVALIDATE_CACHE_TYPES` allows either `ROLLOVER` or `DELETE` privilege to invalidate cache. Public authorization methods are `hasAccess`, `assertAccess` for a single type or an `EnumSet`, `hasAccessToKey`, and `isACLPresent`. It implements both `Runnable` and `KeyAuthorizationKeyProvider.KeyACLs`.

## Control Flow
Construction loads ACL configuration, then `setKMSACLs` builds volatile maps of global ACLs and blacklists. `setKeyACLs` parses keys matching `key.acl.<name>.<op>`, plus `default.key.acl.<op>` and `whitelist.key.acl.<op>`. `startReloader` schedules `run` every second; `run` checks `KMSConfiguration.isACLsFileNewer(lastReload)` and replaces maps if the ACL file changed. Denial paths mark the unauthorized meter, audit the unauthorized action, and throw `AuthorizationException`.

## State and Persistence
Authorization state lives in volatile map references that are atomically swapped on reload. There is no persistence written by this class; the persisted authority is `kms-acls.xml`. The scheduled executor is lifecycle-managed by `KMSWebApp`.

## Dependencies and Integration Points
It uses Hadoop `AccessControlList`, `Configuration`, `UserGroupInformation`, KMS operation enums, and per-key operation types from `KeyAuthorizationKeyProvider`. It is called directly by `KMS` for global operations and by `KeyAuthorizationKeyProvider` for metadata-driven per-key authorization.

## Risks
Default global ACLs use wildcard `*` when no property is set, so deployment safety depends on `kms-acls.xml` being explicitly configured. Per-key access denies when no matching ACL/default/whitelist is present, but global KMS ACLs may be broad. The reload checks call `loadACLs()` twice in one update path, so a changing file could theoretically produce mixed global/key views. Invalid per-key ACL names or operations are logged and ignored.

## Test Signals
Tests should verify wildcard defaults, blacklist override, hot reload, malformed key ACL logging/ignore behavior, `ALL` handling, default and whitelist precedence, and unauthorized audit/meter side effects. Existing visible-for-testing methods expose maps and `forceNextReloadForTesting`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSACLs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSAudit.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSAudit.java

## Purpose
`KMSAudit.java` centralizes audit event creation, aggregation, logger plugin initialization, and shutdown for Hadoop KMS.

## Important APIs, Types, and Functions
`AGGREGATE_OPS_WHITELIST` identifies high-volume operations eligible for aggregation: key version/current key reads and EEK decrypt/generate/reencrypt. Public methods include `ok`, `unauthorized` for KMS and key operations, `error`, `unauthenticated`, `shutdown`, and `evictCacheForTesting`. Logger classes are loaded from `hadoop.kms.audit.logger`, defaulting to `SimpleKMSAuditLogger`.

## Control Flow
Construction reads the aggregation window, builds a Guava cache with `expireAfterWrite`, schedules periodic cleanup, and instantiates configured `KMSAuditLogger` implementations. `op` either logs immediately or aggregates by `(user, key, op)`. Unauthorized events invalidate any aggregate cache entry and are logged immediately. Expired aggregate events with positive access count are logged and reinserted to continue the aggregation window.

## State and Persistence
Runtime state consists of the aggregation cache, scheduled executor, and audit logger list. Persistence is indirect through the configured logging backend. `shutdown` stops the executor and calls each logger's cleanup.

## Dependencies and Integration Points
It depends on Hadoop `Configuration`, UGI, reflection utilities, Guava cache, and `KMSAuditLogger`. `KMS`, `KMSACLs`, `KMSAuthenticationFilter`, and `KMSExceptionsProvider` call into it for success, authorization, unauthenticated, and error events.

## Risks
Audit format compatibility is critical because downstream parsers depend on it. Aggregation changes event timing and count semantics for whitelisted operations. Logger initialization failures abort startup by throwing runtime exceptions. The remote host passed by most operation paths is `"Unknown"`, while unauthenticated and exception paths include request context.

## Test Signals
Tests should verify first-event logging, aggregation eviction and count, immediate unauthorized logging, configured logger loading and failure behavior, shutdown cleanup, and that non-whitelisted or incomplete events bypass aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSAudit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSAuditLogger.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSAuditLogger.java

## Purpose
`KMSAuditLogger.java` defines the private extension interface for KMS audit loggers and the immutable-per-event data object passed to them.

## Important APIs, Types, and Functions
`OpStatus` enumerates `OK`, `UNAUTHORIZED`, `UNAUTHENTICATED`, and `ERROR`. Nested `AuditEvent` records operation object, key name, user, impersonator, remote host, extra message, start and end times, and an `AtomicLong` access count for aggregate events. Implementations must provide `initialize`, `logAuditEvent`, and `cleanup`.

## Control Flow
`AuditEvent` construction derives user and impersonator from `UserGroupInformation`, detecting proxy authentication through `AuthenticationMethod.PROXY`. `KMSAudit` mutates only the event end time and access count before dispatching to logger implementations.

## State and Persistence
The interface has no static state. `AuditEvent` carries event-local state and aggregate counters. Persistence is delegated entirely to implementations.

## Dependencies and Integration Points
It is consumed by `KMSAudit` and implemented by `SimpleKMSAuditLogger` or configured custom classes. The warning in the source documents that audit log format must remain backward-compatible.

## Risks
Because the event accepts `Object op`, loggers must handle both `KMS.KMSOp` and `KeyAuthorizationKeyProvider.KeyOpType` values, plus null for some error paths. Changing event string format or field semantics can break external audit consumers.

## Test Signals
Tests should cover proxy-user impersonator extraction, null UGI handling, access count initialization at `-1`, end-time mutation, and compatibility of custom logger invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSAuditLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSAuthenticationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSAuthenticationFilter.java

## Purpose
`KMSAuthenticationFilter.java` adapts Hadoop delegation-token authentication to KMS-specific configuration, proxy-user settings, metrics, and audit behavior.

## Important APIs, Types, and Functions
It extends `DelegationTokenAuthenticationFilter`. `CONFIG_PREFIX` is `hadoop.kms.authentication.`. `getKMSConfiguration` maps simple and kerberos auth types to delegation-token authentication handlers and sets the KMS delegation token kind. `getProxyuserConfiguration` strips `hadoop.kms.` from proxyuser properties. Inner `KMSResponse` captures status and error message.

## Control Flow
For initialization, the filter copies KMS authentication-prefixed config from `KMSWebApp.getConfiguration()`. During `doFilter`, it wraps the response, delegates to the parent filter, then increments invalid-call metrics for non-OK/non-CREATED/non-UNAUTHORIZED statuses. Unauthorized responses increment unauthenticated metrics and audit unauthenticated requests except for OPTIONS, which is part of SPNEGO negotiation.

## State and Persistence
The filter keeps no persistent state. Request-local response status and message are held in the wrapper. Authentication cookies/tokens are handled by the parent Hadoop auth framework.

## Dependencies and Integration Points
It integrates with `KMSWebApp` configuration, `KMSDelegationToken`, Hadoop authentication handlers, Jetty response status reason support, and `KMSAudit`. It is registered in `web.xml` before `KMSMDCFilter`.

## Risks
`getKMSConfiguration` assumes `AUTH_TYPE` is present; a missing property would produce a null dereference. `sendError` must account for Jetty behavior after 9.4.21 by using `setStatusWithReason`. Metrics classification depends on captured status codes; code paths that do not set status may be invisible.

## Test Signals
Tests should validate auth type rewriting, token kind setting, proxyuser config key transformation, unauthorized audit suppression for OPTIONS, HTML quoting in errors, and invalid/unauthenticated meter increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSAuthenticationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSConfiguration.java

## Purpose
`KMSConfiguration.java` defines KMS configuration keys, defaults, resource loading, ACL-file freshness checks, and startup validation for required system properties.

## Important APIs, Types, and Functions
Constants cover config file names, prefixes, HTTP host/port/admin ACLs, SSL enablement, provider URI, cache toggles and timeouts, audit aggregation, metrics naming, audit logger classes, and per-key authorization enablement. `getKMSConf`, `getACLsConf`, `getConfiguration`, `isACLsFileNewer`, and `validateSystemProps` are the operational methods.

## Control Flow
Static initialization adds `kms-default.xml` and `kms-site.xml` as Hadoop default resources. `getConfiguration` builds a `Configuration`, optionally using absolute `kms.config.dir` to add file URLs for named resources. `isACLsFileNewer` only checks filesystem modification time when `kms.config.dir` is set and requires a 100 ms freshness margin. `validateSystemProps` aborts if `kms.config.dir` or `log4j.configuration` is missing.

## State and Persistence
The class writes no state. It controls how persisted XML resources are loaded and how `kms-acls.xml` freshness is detected for reload.

## Dependencies and Integration Points
It is used by nearly every KMS server class: `KMSWebServer` for network and SSL config, `KMSWebApp` for provider/cache/audit setup, `KMSACLs` for ACL loading, and shell scripts that set system properties.

## Risks
When `kms.config.dir` is absent, ACL freshness checking always returns false, so classpath ACLs are not hot-reloaded. Absolute-path validation is strict and fails startup for relative config dirs. Default provider URI points to a user-home JCEKS file, which is suitable for defaults/tests but deployment-specific.

## Test Signals
Tests should cover classpath and file URL resource loading, relative config-dir rejection, ACL freshness margin, default values matching `kms-default.xml`, and `validateSystemProps` failure messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSExceptionsProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSExceptionsProvider.java

## Purpose
`KMSExceptionsProvider.java` is the Jersey `ExceptionMapper` that converts server exceptions into HTTP responses and audit/error logs.

## Important APIs, Types, and Functions
`toResponse` performs status mapping. `createResponse` delegates to `HttpExceptionUtils.createJerseyExceptionResponse`. `getOneLineMessage` strips multiline exception messages at the platform line separator. `log` emits detailed warnings including UGI, method, URL, remote address, status, and message from `KMSMDCFilter`.

## Control Flow
The mapper unwraps Jersey `ContainerException` to its cause for classification. Security, authentication, authorization, and access-control failures map to 403; unsupported operations and illegal arguments map to 400; I/O and unknown exceptions map to 500. Authentication and authorization exceptions skip duplicate audit because access checks already audited them. Other exceptions produce KMS audit `ERROR` events.

## State and Persistence
No mutable state is kept. Persistence is through audit logging and HTTP response payloads.

## Dependencies and Integration Points
It relies on `KMSMDCFilter` request context, `KMSWebApp.getKMSAudit()`, Jersey exception mapping, Hadoop security exceptions, and `HttpExceptionUtils`. It is discovered by Jersey because `web.xml` scans the server package.

## Risks
The code checks `exception instanceof IOException` rather than `throwable instanceof IOException` after unwrapping, so an `IOException` inside `ContainerException` may be classified as generic 500 without the specific branch. Audit context can be null if the MDC filter did not run. Error payloads expose exception-derived messages, so callers may see provider details.

## Test Signals
Tests should cover every exception category, `ContainerException` unwrapping, duplicate-audit suppression for authorization failures, one-line message truncation, and response body compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSExceptionsProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSJSONReader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSJSONReader.java

## Purpose
`KMSJSONReader.java` is a Jersey JSON request body reader for KMS endpoints that accept untyped `Map` or `List` payloads.

## Important APIs, Types, and Functions
It implements `MessageBodyReader<Object>`, is annotated with `@Provider` and `@Consumes(MediaType.APPLICATION_JSON)`, and uses a static Jackson `ObjectMapper`. `isReadable` allows payload binding when the requested type is assignable from `Map` or `List`. `readFrom` deserializes the entity stream into the requested class.

## Control Flow
Jersey invokes this provider for JSON requests targeting raw `Map` or `List` endpoint parameters such as key creation material and reencryption batches. Deserialization errors propagate as `IOException` or `WebApplicationException` and are later mapped by the exception provider.

## State and Persistence
The only state is the shared mapper. It writes no persistent state.

## Dependencies and Integration Points
It integrates with Jersey provider discovery and the raw JSON payloads consumed by `KMS.java`. It depends on Jackson databind.

## Risks
The reader targets raw collections, so type validation is deferred to endpoint code and utility parsers. Numeric values are deserialized according to Jackson defaults, which matters for fields cast to `Integer` in `KMS.createKey`.

## Test Signals
Tests should verify Map/List binding, invalid JSON propagation, numeric field type behavior, and that unrelated types are not claimed by this provider.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSJSONReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSJSONWriter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSJSONWriter.java

## Purpose
`KMSJSONWriter.java` is the Jersey JSON response writer for KMS responses represented as `Map` or `List`.

## Important APIs, Types, and Functions
It implements `MessageBodyWriter<Object>`, is annotated as a JSON UTF-8 provider, and declares writeability for `Map` and `List` classes. `getSize` returns `-1`, and `writeTo` serializes with Hadoop `JsonSerialization.writer()` through a UTF-8 `OutputStreamWriter`.

## Control Flow
Endpoint methods in `KMS.java` return maps and lists generated by `KMSUtil` or `KMSServerJSONUtils`; Jersey selects this writer and writes UTF-8 JSON to the response stream.

## State and Persistence
The writer is stateless and writes only HTTP response bytes.

## Dependencies and Integration Points
It depends on Jersey, Hadoop `JettyUtils.UTF_8`, and `JsonSerialization`. Its media type must match endpoint `@Produces` declarations.

## Risks
Only `Map` and `List` are handled; returning another object type would need another provider. The writer does not explicitly close or flush the `Writer`, relying on Jersey/container lifecycle.

## Test Signals
Tests should verify UTF-8 output, map/list selection, JSON compatibility for KMS REST constants, and behavior for unsupported response classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSJSONWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSMDCFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSMDCFilter.java

## Purpose
`KMSMDCFilter.java` captures request context for the current KMS request and exposes it through static thread-local accessors used by exception and audit code.

## Important APIs, Types, and Functions
The private `Data` holder stores UGI, HTTP method, full URL, and remote client address. Static methods `getUgi`, `getMethod`, `getURL`, and `getRemoteClientAddress` read the current thread context. `setContext` is visible for testing.

## Control Flow
`doFilter` clears any stale context, obtains the request UGI from `HttpUserGroupInformation`, builds a URL including query string, stores context, invokes the next filter/servlet, and clears context in `finally`.

## State and Persistence
State is request-scoped in a `ThreadLocal`. It is explicitly removed before and after chain execution to prevent leakage across reused servlet threads.

## Dependencies and Integration Points
It depends on Servlet APIs, `HttpUserGroupInformation`, and Hadoop UGI. `KMSExceptionsProvider` uses its context for audit and warning logs.

## Risks
If this filter is not invoked, exception logs lose request context. It casts to `HttpServletRequest`, so it assumes HTTP traffic. Filter ordering matters: authentication should run first so `HttpUserGroupInformation.get()` is populated.

## Test Signals
Tests should verify context population with query strings, remote address capture, cleanup after success and exception, null accessors outside a request, and filter ordering assumptions with authentication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSMDCFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSServerJSONUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSServerJSONUtils.java

## Purpose
`KMSServerJSONUtils.java` converts server-side `KeyProvider` metadata and key-version collections into REST-compatible JSON maps/lists.

## Important APIs, Types, and Functions
`toJSON(List<KeyProvider.KeyVersion>)` maps each key version through `KMSUtil.toJSON`. `toJSON(String, Metadata)` emits name, cipher, length, description, attributes, created timestamp, and version count. `toJSON(String[], Metadata[])` pairs names with metadata arrays.

## Control Flow
`KMS.java` calls these helpers for metadata, metadata batches, and key version lists. Null metadata returns an empty map for that key rather than an error.

## State and Persistence
The class is stateless and creates new list/map objects for responses.

## Dependencies and Integration Points
It depends on `KMSRESTConstants`, `KMSUtil`, and `KeyProvider`. Output is serialized by `KMSJSONWriter`.

## Risks
The batch converter assumes `keyNames` and `metas` have matching lengths. Null metadata producing `{}` may be a compatibility contract clients rely on, but it can also hide missing keys if callers do not validate.

## Test Signals
Tests should verify field names and types, null metadata behavior, ordering in batch responses, and key version conversion compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSServerJSONUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSWebApp.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSWebApp.java

## Purpose
`KMSWebApp.java` is the servlet context listener that initializes and tears down the KMS runtime object graph: configuration, UGI, ACLs, metrics, audit, key provider, caching, eager EEK generation, and per-key authorization.

## Important APIs, Types, and Functions
`contextInitialized` performs startup. `contextDestroyed` closes provider, audit, ACL reloader, JMX reporter, and metrics. Static getters expose configuration, ACLs, meters, provider, and audit service to resource/filter classes.

## Control Flow
Startup loads KMS config, sets UGI configuration, starts ACL reloading, creates Dropwizard meters and JMX reporter, initializes audit, resolves the backing key provider from `hadoop.kms.key.provider.uri`, optionally wraps it in `CachingKeyProvider`, wraps it in `KeyProviderCryptoExtension`, then `EagerKeyGeneratorKeyProviderCryptoExtension`, and finally optionally `KeyAuthorizationKeyProvider`. Any startup failure prints a detailed message and exits the JVM.

## State and Persistence
Most server runtime state is static in this class. Persistent key state lives in the backing provider; this class controls cache wrappers and flush exposure indirectly. Metrics are process-local and exposed through JMX.

## Dependencies and Integration Points
It integrates with Servlet context lifecycle from `web.xml`, Hadoop configuration and key provider factories, Dropwizard metrics, SLF4J bridge handling, `KMSACLs`, `KMSAudit`, and all REST/filter classes that use its static getters.

## Risks
Static global state simplifies access but makes embedded tests and multiple webapp instances sensitive to lifecycle order. `System.exit(1)` on initialization failure is appropriate for daemon startup but harsh in embedding contexts. Correct wrapper order is security-sensitive: per-key authorization must wrap the crypto extension after caching/eager generation. `getConfiguration` returns a defensive copy.

## Test Signals
Tests should verify missing provider failure, cache enable/disable behavior, per-key authorization enable/disable, meter registration, ACL reloader lifecycle, teardown cleanup, and wrapper ordering with authorization checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSWebApp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSWebServer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSWebServer.java

## Purpose
`KMSWebServer.java` builds and runs the Hadoop `HttpServer2` instance that hosts the KMS web application.

## Important APIs, Types, and Functions
The constructor configures HTTP/HTTPS endpoint, admin ACL, SSL config, auth filter prefix, deprecated environment-variable overrides, metrics identity, and JVM pause monitoring. Lifecycle methods are `start`, `isRunning`, `join`, `stop`, and `getKMSUrl`. `main` validates required system properties and runs the daemon.

## Control Flow
Construction maps deprecated `KMS_*` environment variables into configuration with warnings, chooses scheme from SSL enablement, initializes `JvmPauseMonitor`, removes generic Hadoop auth/proxy filter initializers to avoid duplication, and builds `HttpServer2`. `start` starts HTTP, initializes the default metrics system and JVM metrics, and starts pause monitoring. `stop` reverses these resources.

## State and Persistence
State is the running HTTP server, scheme, metrics process/session identifiers, and pause monitor. It writes no persistent data.

## Dependencies and Integration Points
It depends on Hadoop `HttpServer2`, metrics2, `SSLFactory`, admin `AccessControlList`, `KMSAuthenticationFilter`, and `KMSConfiguration`. Shell scripts launch this class with required system properties.

## Risks
Environment variables still override configuration even though deprecated, which can surprise deployments. The constructor receives `sslConf`; non-SSL embedded paths may pass null, so behavior depends on `HttpServer2.Builder` tolerance. Removing filter initializers relies on exact class names.

## Test Signals
Tests should verify endpoint URL construction, SSL and non-SSL startup, deprecated env override precedence, filter initializer pruning, admin ACL propagation, metrics/pause monitor lifecycle, and `main` property validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSWebServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KeyAuthorizationKeyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KeyAuthorizationKeyProvider.java

## Purpose
`KeyAuthorizationKeyProvider.java` is a security wrapper around `KeyProviderCryptoExtension` that enforces per-key ACLs based on the current Hadoop user and metadata-stored ACL names.

## Important APIs, Types, and Functions
`KeyOpType` defines `ALL`, `READ`, `MANAGEMENT`, `GENERATE_EEK`, and `DECRYPT_EEK`. `KeyACLs` abstracts ACL lookup and authorization. Key methods override create, roll, delete, invalidate cache, warm-up, generate EEK, decrypt EEK, reencrypt EEK, batch reencrypt, read key versions/metadata/current key, and provider plumbing. `KEY_ACL_NAME` is the metadata attribute `key.acl.name`.

## Control Flow
Create operations take a write lock, derive or validate an ACL name, persist it into key metadata when absent and a matching key ACL exists, and require MANAGEMENT or ALL. Management mutations take the write lock and call `doAccessCheck`. EEK and read operations take the read lock. Decrypt and reencrypt first verify that the supplied encrypted key version belongs to its named key by reading the provider key version. Batch reencrypt validates every item, checks access for the first key name, and delegates.

## State and Persistence
The wrapper holds delegate provider and ACL references plus fair read/write locks. Persistent state is the `key.acl.name` metadata attribute written during key creation, which allows multiple keys to share an ACL name distinct from the key name.

## Dependencies and Integration Points
It integrates with `KMSACLs` through `KeyACLs`, `UserGroupInformation.getCurrentUser`, `KeyProviderCryptoExtension`, and KMS metadata. `KMSWebApp` installs this wrapper when `hadoop.kms.key.authorization.enable` is true.

## Risks
Authorization only occurs when metadata exists; `doAccessCheck` silently allows operations for missing metadata because it cannot resolve an ACL name. Batch reencrypt validates all items but checks `GENERATE_EEK` access only against the first key name; upstream `KMS.reencryptEncryptedKeys` enforces same key name before calling it. Create authorization mutates the caller's `Options` attributes. The source comment says some read operations are not checked, but the implementation does check them.

## Test Signals
Tests should cover create with implicit and explicit ACL names, default and whitelist ACL behavior through `KMSACLs`, missing metadata behavior, read/write lock concurrency, encrypted-key version/key mismatch rejection, batch same-key expectations, and disabled wrapper behavior in `KMSWebApp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KeyAuthorizationKeyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/SimpleKMSAuditLogger.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/SimpleKMSAuditLogger.java

## Purpose
`SimpleKMSAuditLogger.java` is the default text-format KMS audit logger implementation.

## Important APIs, Types, and Functions
It implements `KMSAuditLogger`. `logAuditEvent` chooses an aggregate-aware format for whitelisted successful events and a simple key-value format otherwise. `initialize` and `cleanup` are no-ops. Logs are written to the logger named `kms-audit`.

## Control Flow
For aggregate-eligible events with user, key, and op, OK status is logged as status plus op/key/user/accessCount/interval. Unauthorized and other statuses fall back to `logAuditSimpleFormat`. The simple format includes non-empty op, key, and user fields, or only status plus extra message when no fields are present.

## State and Persistence
No mutable state is held beyond the logger reference. Persistence depends on the configured logging backend.

## Dependencies and Integration Points
It is instantiated by `KMSAudit` by default or via `hadoop.kms.audit.logger`. It uses Guava `Strings` and `Joiner` for output formatting.

## Risks
The class carries a strong compatibility warning: audit log text format should not change because external tools parse it. Aggregated and non-aggregated formats differ, which consumers must handle.

## Test Signals
Tests should snapshot log output for OK aggregate events, unauthorized fallback, empty-field events, extra message preservation, and default selection by `KMSAudit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/SimpleKMSAuditLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/libexec/shellprofile.d/hadoop-kms.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/libexec/shellprofile.d/hadoop-kms.sh

## Purpose
`hadoop-kms.sh` registers and configures the `hadoop kms` subcommand in Hadoop's shell framework.

## Important APIs, Types, and Functions
When the shell executable is `hadoop`, it adds a `kms` daemon subcommand. `hadoop_subcommand_kms` sources `kms-env.sh` if present, declares deprecated and active environment variables, enables daemonization, sets `HADOOP_CLASSNAME` to `KMSWebServer`, and appends required Java system properties for config dir, log dir, and log4j configuration.

## Control Flow
At command execution, it loads environment overrides, registers deprecation notices for old variables, declares KMS-specific variables as used, and creates the KMS temp directory when running or starting the daemon.

## State and Persistence
It mutates shell variables and ensures a temp directory exists. It does not directly start Java; the Hadoop shell framework does that after the handler returns.

## Dependencies and Integration Points
It depends on Hadoop shell helper functions such as `hadoop_add_subcommand`, `hadoop_add_param`, `hadoop_deprecate_envvar`, and `hadoop_mkdir`. It integrates with `KMSConfiguration.validateSystemProps` by setting `-Dkms.config.dir` and `-Dlog4j.configuration`.

## Risks
Incorrect `HADOOP_CONF_DIR` or `HADOOP_LOG_DIR` produces invalid system properties and startup failure. Deprecated environment variables are still recognized by Java server code, so shell and Java override behavior must stay aligned.

## Test Signals
Shell tests should verify subcommand registration, optional `kms-env.sh` sourcing, system property construction, daemonization support flag, temp directory creation, and deprecation messaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/libexec/shellprofile.d/hadoop-kms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/resources/kms-default.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/resources/kms-default.xml

## Purpose
`kms-default.xml` documents and supplies default KMS configuration values.

## Important APIs, Types, and Functions
Properties define HTTP port/host/admin ACLs, SSL enablement, HTTP thread/header/temp/backlog/idle settings, backing key provider URI, Java keystore password file, KMS cache enablement and TTLs, audit aggregation window, simple or Kerberos authentication, signer secret provider options including ZooKeeper, audit logger class, per-key authorization enablement, and encrypted-key cache sizing/fill/expiry settings.

## Control Flow
`KMSConfiguration` adds this resource as a default resource, and `getKMSConf` combines it with core-site and kms-site. Operators should copy changed properties to `kms-site.xml` rather than editing this file.

## State and Persistence
This is persisted default configuration. It does not store runtime state, but defaults directly influence provider persistence location, cache behavior, auth mode, and logging behavior.

## Dependencies and Integration Points
Keys mirror constants in `KMSConfiguration`, Hadoop HTTP server keys, Hadoop authentication keys, and Eager EEK cache keys. `KMSWebServer`, `KMSWebApp`, `KMSAudit`, and `KMSAuthenticationFilter` consume these values.

## Risks
Defaults favor local/simple operation: HTTP binds to all interfaces on port 9600, SSL is disabled, authentication is simple, and provider URI points to `${user.home}/kms.keystore`. Production deployments must override these. Typos in descriptions such as "maxmimum" are harmless but documentation-facing.

## Test Signals
Tests should verify defaults load, constants match property names, production overrides in `kms-site.xml` take precedence, auth defaults are usable in MiniKMS, and cache/audit defaults match Java constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/resources/kms-default.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/resources/webapps/kms/WEB-INF/web.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/resources/webapps/kms/WEB-INF/web.xml

## Purpose
`web.xml` declares the KMS web application components for the servlet container.

## Important APIs, Types, and Functions
It registers `KMSWebApp` as a listener, Jersey `ServletContainer` as `webservices-driver` scanning `org.apache.hadoop.crypto.key.kms.server`, Hadoop `JMXJsonServlet`, servlet mappings for `/kms/*` and `/kms/jmx`, and filters `KMSAuthenticationFilter` and `KMSMDCFilter` on all paths.

## Control Flow
Container startup invokes `KMSWebApp.contextInitialized`, eagerly loads Jersey, and routes `/kms/*` REST calls through auth and MDC filters into Jersey resources. `/kms/jmx` exposes JMX JSON through the same filter mappings.

## State and Persistence
The descriptor is static deployment metadata. Runtime state is created by the listener and filters it declares.

## Dependencies and Integration Points
It ties together `KMSWebApp`, `KMS`, Jersey providers and exception mappers in the server package, the authentication filter, request context filter, and JMX servlet.

## Risks
Filter order is important: authentication is declared before MDC so request UGI is available. Package scanning must include all providers; moving classes out of the package would require descriptor changes. JMX exposure is protected only by the configured filter/admin behavior.

## Test Signals
Integration tests should verify REST and JMX mappings, listener startup, provider discovery, filter order, authentication enforcement, and that `/kms/*` paths match client expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/resources/webapps/kms/WEB-INF/web.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/sbin/kms.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/sbin/kms.sh

## Purpose
`kms.sh` is a deprecated compatibility wrapper for controlling KMS.

## Important APIs, Types, and Functions
It supports `run`, `start`, `status`, and `stop`, prints usage, warns that users should call `hadoop [--daemon start|status|stop] kms`, locates `bin/hadoop` from `HADOOP_HOME` or relative to the script, and execs the Hadoop command with translated arguments.

## Control Flow
No arguments prints usage and exits. `run` maps to `hadoop kms`; daemon commands map to `hadoop --daemon <cmd> kms`; unknown commands print usage and exit 1. The final `exec` replaces the shell process.

## State and Persistence
It holds only transient shell variables and writes no persistent state.

## Dependencies and Integration Points
It depends on the Hadoop command-line launcher and the `hadoop-kms.sh` shell profile that implements the actual `kms` subcommand.

## Risks
As a deprecated wrapper, behavior can diverge from the main Hadoop launcher if argument semantics change. Relative path discovery assumes the standard Hadoop layout.

## Test Signals
Shell tests should verify command translation, deprecation warning, usage text, unknown-command exit status, `HADOOP_HOME` path selection, and relative path fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/sbin/kms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/site/site.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/site/site.xml

## Purpose
`site.xml` is the Maven site descriptor for Hadoop KMS documentation.

## Important APIs, Types, and Functions
It declares project name `Hadoop KMS`, uses `maven-stylus-skin` with version from `${maven-stylus-skin.version}`, and adds a body link to Apache Hadoop.

## Control Flow
Maven site generation reads this descriptor to choose skin and navigation links.

## State and Persistence
This is static documentation build metadata and contains no runtime state.

## Dependencies and Integration Points
It integrates with Maven site tooling and the Hadoop documentation build.

## Risks
HTTP link uses `http://hadoop.apache.org/` rather than HTTPS. Missing skin version property would break site generation.

## Test Signals
Build validation should run the Maven site phase or descriptor validation to ensure the skin artifact and property resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/site/site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/KMSBenchmark.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/KMSBenchmark.java

## Purpose
`KMSBenchmark.java` is a command-line benchmark tool for measuring KMS encrypted-key generation and decryption throughput/latency through `KeyProviderCryptoExtension`.

## Important APIs, Types, and Functions
The class implements `Tool`. `OperationStatsBase` owns common benchmark parameters, thread scheduling, timing, and result printing. `StatsDaemon` executes operations in subject-inheriting threads. `EncryptKeyStats` benchmarks `generateEncryptedKey`; `DecryptKeyStats` benchmarks `decryptEncryptedKey`. Static helpers include `createKeyProviderCryptoExtension`, `runBenchmark`, `printUsage`, and `main`.

## Control Flow
Construction creates a key provider extension from `hadoop.security.key.provider.path`, attempts to pre-generate an EEK for key `systest`, and parses selected setup flags. `run` parses `-op encrypt`, `-op decrypt`, or `-op all`, constructs operation stats, runs each benchmark, then prints stats. `benchmark` divides requested operations across threads, starts daemons, waits for completion, aggregates local counts and cumulative times, and reports elapsed wall time and average call time.

## State and Persistence
State includes shared provider, one shared `eek` field, selected key name, setup flags, and benchmark counters. Optional key creation would persist through the configured key provider, but `createEncryptionKey` is never set to true in the observed parser despite parsing `-createkey` into `encryptionKeyName`.

## Dependencies and Integration Points
It uses Hadoop `ToolRunner`, `GenericOptionsParser`, `KMSUtil.createKeyProvider`, `SubjectInheritingThread`, `Time`, and `KeyProviderCryptoExtension`. It is test/benchmark code rather than server runtime.

## Risks
The `-createkey` flag appears to set only the key name, not `createEncryptionKey`, so requested key creation may not happen. Decrypt benchmark shares a mutable `eek` across threads; encrypt benchmark updates that same field concurrently. Exceptions during operations are logged but do not fail the benchmark, so results can include failed attempts as executed operations. `isInProgress` busy-waits with sleep and relies on local counters.

## Test Signals
Tests should verify CLI parsing, operation division across threads, provider-path requirement, `-op all`, warmup behavior, failure handling semantics, and the apparent `-createkey` flag bug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/KMSBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/MiniKMS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/MiniKMS.java

## Purpose
`MiniKMS.java` is a test utility that starts an embedded KMS web server with generated/default configuration for integration tests.

## Important APIs, Types, and Functions
`MiniKMS.Builder` configures KMS conf directory, log4j file, port, and optional SSL keystore/password. `MiniKMS.start` creates missing `kms-acls.xml`, `core-site.xml`, and `kms-site.xml`, sets required system properties, configures host/port and optional SSL, starts `KMSWebServer`, and records the resulting URL. `getKMSUrl` and `stop` expose lifecycle control.

## Control Flow
Builder validation ensures required directories/files exist. `start` sets `kms.config.dir`, copies `mini-kms-acls-default.xml` if needed, writes minimal core-site and kms-site files when absent, sets simple authentication and a JCEKS provider under the conf dir, then starts the server on localhost at the requested port.

## State and Persistence
MiniKMS writes test configuration XML files and a provider URI pointing to `kms.keystore` under the chosen conf directory. Runtime state includes the embedded `KMSWebServer` and URL.

## Dependencies and Integration Points
It depends on `KMSWebServer`, `KMSConfiguration`, Hadoop `Configuration`, `Path`, `SSLFactory`, resource loading via `ThreadUtil`, and Commons IO. Tests can use it to exercise the same servlet/server stack as production.

## Risks
It mutates JVM-wide system properties, which can leak between tests if not isolated. Existing config files are respected rather than overwritten, so tests depend on directory cleanliness. `stop` wraps server stop failures in runtime exceptions.

## Test Signals
Tests should cover default file generation, custom config dir validation, custom port, SSL setup, URL availability, cleanup/stop behavior, and isolation of global system properties across test cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/MiniKMS.java -->
