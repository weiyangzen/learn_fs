# subset-b-008096 Research

Grouped research for Apache Ozone Ozone Manager support classes in `subset-b-008096`. Each source file section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/PendingKeysDeletion.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/PendingKeysDeletion.java

Purpose: `PendingKeysDeletion` is a small data carrier used by OM deletion flows to describe keys whose deleted-table entries are ready to be purged or modified after block reclamation decisions. It separates fully purged keys from `RepeatedOmKeyInfo` records that must remain because not every block or key version is reclaimable.

Important APIs and types: The top-level getters expose `Map<String, PurgedKey> getPurgedKeys()`, `Map<String, RepeatedOmKeyInfo> getKeysToModify()`, and `getNotReclaimableKeyCount()`. Nested `PurgedKey` records the volume, bucket, bucket object ID, `BlockGroup`, delete-table key name, purged bytes, and whether the purged entry represented a committed key.

Control flow: There is no active algorithm in this class. Callers construct it after scanning deletion candidates, then downstream response or cleanup code reads the maps and applies table mutations and accounting updates.

State and persistence behavior: The object itself is transient. Its fields describe persistent OM DB effects: removal from deleted-key tables, modification of repeated deleted-key metadata, and bucket-space accounting through `purgedBytes` and bucket ID. The maps are not defensively copied, so caller ownership matters.

Dependencies and integration points: It depends on `BlockGroup` for SCM block-delete handoff and `RepeatedOmKeyInfo` for OM deleted-key table values. It is part of the bridge between OM metadata cleanup and block reclaim services.

Risks and test signals: Risks are mostly data-contract risks: mutable map aliasing, mismatch between `deleteKeyName` and the map key, and incorrect `isCommittedKey` or bucket ID causing wrong quota updates. Tests should assert mixed reclaimable/non-reclaimable deleted entries, purged-byte accounting, and that not-reclaimable counts preserve remaining repeated-key versions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/PendingKeysDeletion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/PrefixManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/PrefixManager.java

Purpose: `PrefixManager` defines the OM service contract for prefix ACL management and lookup. It extends `IOzoneAcl`, so prefix objects can participate in the same ACL read/check APIs used by volumes, buckets, and keys.

Important APIs and types: It exposes `getMetadataManager()` and `getLongestPrefixPath(String path)`. Implementations return `OmPrefixInfo` values representing the prefix nodes along the longest matching path and inherit `getAcl` and `checkAccess` from `IOzoneAcl`.

Control flow: The interface does not implement flow. `PrefixManagerImpl` supplies the real behavior by validating `OzoneObj` values, resolving bucket links, traversing a radix tree, and consulting OM metadata.

State and persistence behavior: The interface holds no state. Implementations are expected to read and write `prefixTable` entries and maintain an in-memory prefix index for efficient ACL checks.

Dependencies and integration points: It depends on `OMMetadataManager`, `OmPrefixInfo`, and the OM ACL subsystem. Prefix ACL request handlers use this contract to add, remove, set, list, and evaluate ACLs.

Risks and test signals: API risk is ambiguity around path normalization and trailing slash requirements, which the implementation enforces. Tests should cover longest-prefix lookup, empty path behavior, invalid resource types, and inheritance from parent prefixes or buckets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/PrefixManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/PrefixManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/PrefixManagerImpl.java

Purpose: `PrefixManagerImpl` implements prefix ACL storage, lookup, inheritance, and access checks. It keeps an in-memory `RadixTree<OmPrefixInfo>` synchronized with `prefixTable` so OM can evaluate prefix ACLs without scanning RocksDB on every request.

Important APIs and types: Public entry points include `getAcl`, `checkAccess`, `getLongestPrefixPath`, `getPrefixInfo`, `addAcl`, `removeAcl`, `setAcl`, and `getResolvedPrefixObj`. `OMPrefixAclOpResult` returns the updated `OmPrefixInfo` plus a boolean indicating whether the ACL set materially changed. It uses `OzoneObj`, `RequestContext`, `OzoneAcl`, `OmBucketInfo`, `OmPrefixInfo`, and `OzoneAclUtil`.

Control flow: Construction calls `loadPrefixTree`, iterating `prefixTable` and inserting every persisted prefix. Read paths validate that the object is a prefix, resolve link buckets through `OzoneManager.resolveBucketLink`, acquire `PREFIX_LOCK`, find the longest radix-tree match, and only return ACLs when the requested prefix exactly equals the longest prefix. Mutation helpers build or modify `OmPrefixInfo`, inherit default ACLs from the direct parent prefix or bucket when creating a new prefix, update the radix tree, and write `prefixTable` directly only when Ratis is disabled.

State and persistence behavior: Persistent state is `prefixTable`; runtime state is the radix tree. Under HA/Ratis, request/response code owns DB persistence while this class updates the in-memory tree. New prefixes may get object and update IDs derived from the OM epoch and transaction log index.

Dependencies and integration points: It integrates with OM ACL request classes, bucket-link resolution, `OzoneManagerLock.PREFIX_LOCK`, bucket metadata for default ACL inheritance, and `OmPrefixInfo` codecs in the OM DB definition.

Risks and test signals: Load failures log but leave a partial or empty tree, making startup consistency important. `EMPTY_ACL_LIST` is mutable because it is an `ArrayList`. Exact-match behavior means parent prefix ACLs are used for access only through `getLongestPrefixPath`-style callers, not `getAcl` for arbitrary descendants. Tests should cover Ratis and non-Ratis persistence, link bucket resolution, inherited default ACL conversion to access ACLs, trailing slash validation, empty ACL removal deleting the prefix, and concurrent lock discipline.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/PrefixManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ResolvedBucket.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ResolvedBucket.java

Purpose: `ResolvedBucket` bundles the bucket requested by a client and the real bucket reached after resolving a bucket link. It lets request handlers preserve audit context while rewriting operations to the target volume and bucket.

Important APIs and types: Constructors accept requested names plus `OmBucketInfo`, explicit real names, or `Pair` values. Accessors expose requested and real volume/bucket names, owner, and `BucketLayout`. `update(OmKeyArgs)`, `update(KeyArgs)`, and `update(OzoneObj)` return rewritten objects when the bucket is a link. `isLink`, `isDangling`, and `audit` describe resolution state.

Control flow: The update methods are simple branch points: if requested and real names differ, clone the supplied argument through its builder and set real names; otherwise return the original object. Audit always records requested volume/bucket and adds source volume/bucket for links.

State and persistence behavior: The class is immutable after construction and persists nothing. It carries persistent metadata read from bucket records, including owner and layout, and can represent dangling links by storing null real names.

Dependencies and integration points: OM bucket-link resolution returns this type to key, ACL, prefix, and audit paths. It depends on `OmBucketInfo`, protobuf `KeyArgs`, `OmKeyArgs`, and `OzoneObjInfo`.

Risks and test signals: Callers must handle dangling links before invoking update methods that can set null real names. Tests should check regular buckets return the same object, links rewrite only volume/bucket fields, audit maps retain requested names, and dangling links are detectable without corrupting audit output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ResolvedBucket.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3Batcher.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3Batcher.java

Purpose: `S3Batcher` abstracts batched persistence operations for S3 secrets. It allows callers that already hold a DB batch object to add or delete S3 secret rows without depending on a concrete store implementation.

Important APIs and types: `addWithBatch(AutoCloseable batchOperator, String id, S3SecretValue value)` and `deleteWithBatch(AutoCloseable batchOperator, String id)` are the only operations. The loose `AutoCloseable` type permits store-specific batch handles.

Control flow: The interface contains no logic. Implementations should cast or adapt the batch handle, then enqueue table put/delete operations. Callers usually discover availability through `S3SecretManager.isBatchSupported()`.

State and persistence behavior: Batch operations target the `s3SecretTable` or equivalent store. The interface itself has no state; persistence is atomic only to the extent the provided batch operator is committed by the caller.

Dependencies and integration points: It is returned by `S3SecretStore.batcher()` and exposed by `S3SecretManager.batcher()`. Tenant and S3 secret request paths can use it during OM DB batch writes.

Risks and test signals: The weak batch type makes runtime type mismatches possible. Tests should cover implementations rejecting incompatible batches, preserving atomicity when combined with other table writes, and correctly updating cache state outside the batch path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3Batcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3InMemoryCache.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3InMemoryCache.java

Purpose: `S3InMemoryCache` is the default Guava-cache-backed implementation of `S3SecretCache`. It provides fast local lookups for S3 secrets and tombstone-like invalidation semantics for revoked secrets before double-buffer flushes make DB state authoritative.

Important APIs and types: `put`, `invalidate`, `clearCache`, and `get` implement `S3SecretCache`. It stores `S3SecretValue` by access ID or Kerberos ID in an unbounded Guava `Cache`.

Control flow: `put` directly inserts. `invalidate` uses `computeIfPresent` to replace an existing value with `secret.deleted()`, preserving a deleted marker rather than removing immediately. `clearCache` builds a transaction-log-index to cache-key map from current entries and invalidates entries whose indexes appear in the flushed transaction list. `get` returns `getIfPresent`.

State and persistence behavior: State is process-local and non-durable. Deleted entries remain visible to callers until a flush clears them, allowing `S3SecretManagerImpl.getSecret` to avoid falling back to the DB after an intentional revocation.

Dependencies and integration points: It is injected into `S3SecretManagerImpl` and controlled by double-buffer flush callbacks through `clearS3Cache`.

Risks and test signals: The cache is unbounded and `clearCache` is O(cache size + flushed IDs). Duplicate transaction log indexes would overwrite mappings. Tests should cover revoke tombstones, DB fallback suppression for deleted entries, transaction-index-based clearing, and cache consistency across store, revoke, and flush sequences.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3InMemoryCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretCache.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretCache.java

Purpose: `S3SecretCache` defines the cache contract for S3 secret values used by OM. It decouples `S3SecretManager` from the concrete in-memory cache and from double-buffer flush cleanup details.

Important APIs and types: The interface exposes `put`, `invalidate`, `clearCache(List<Long> transactionIds)`, and `get`. Values are `S3SecretValue` instances.

Control flow: No logic is implemented here. Implementations decide whether invalidation removes an entry or marks it deleted, and how transaction IDs are mapped to entries during clearing.

State and persistence behavior: Cache state is transient and should mirror or temporarily mask persistent `s3SecretTable` state. The transaction-ID clearing hook is designed for OM's double-buffered persistence path.

Dependencies and integration points: `S3SecretManager` default methods call this cache, `S3SecretManagerImpl` consults it before the store, and `S3SecretLockedManager` serializes cache clearing under `S3_SECRET_LOCK`.

Risks and test signals: Semantics of `invalidate` are important because the manager treats deleted cached values specially. Tests should verify each implementation's behavior for missing entries, deleted entries, flush clearing, and null cache handling through manager defaults.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretFunction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretFunction.java

Purpose: `S3SecretFunction` is a checked-exception-capable functional interface used to execute custom operations against an `S3SecretManager` while a caller-selected secret lock is held.

Important APIs and types: Its single method is `T accept(S3SecretManager s3SecretManager) throws IOException`. It is parameterized by return type.

Control flow: It does not implement flow directly. `S3SecretLockedManager.doUnderLock` acquires `S3_SECRET_LOCK`, invokes the function with the wrapped manager, and releases the lock in a finally block.

State and persistence behavior: The function carries no state itself, but implementations can call store, revoke, cache, or batch operations under a shared lock and thereby affect `s3SecretTable` and the secret cache.

Dependencies and integration points: This is a small adapter for Java lambdas in S3 secret and tenant workflows where multiple manager calls must be serialized.

Risks and test signals: Risks are callback misuse: long-running actions hold the write lock, and invoking a locked wrapper from inside the callback could deadlock depending on lock reentrancy. Tests should cover exception propagation and lock release on thrown `IOException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretLockedManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretLockedManager.java

Purpose: `S3SecretLockedManager` decorates an `S3SecretManager` with OM lock acquisition. It centralizes lock use for S3 secret get/store/revoke/cache-clear and custom compound operations.

Important APIs and types: It implements all `S3SecretManager` methods and uses `IOzoneManagerLock` with `S3_SECRET_LOCK`. `getSecret`, `storeSecret`, `revokeSecret`, and `clearS3Cache` acquire write locks; `getSecretString` acquires a read lock; `doUnderLock` acquires a write lock and invokes `S3SecretFunction`.

Control flow: Each method acquires the relevant lock key, delegates to the wrapped manager, and releases the lock in a finally block. `clearS3Cache` uses a synthetic `"cache"` lock key. `batcher` and `cache` are simple pass-throughs.

State and persistence behavior: The wrapper has no durable state. It protects the underlying store and cache state from concurrent access within the OM process.

Dependencies and integration points: It integrates the S3 secret subsystem with `OzoneManagerLock` and request handlers that require serialized secret operations.

Risks and test signals: `getSecret` uses a write lock even though it is read-mostly, likely because cache population can mutate state. The `"cache"` lock key does not block per-secret locks, so global cache clearing relies on lock hierarchy rather than identical keys. Tests should verify lock pairing on exceptions, concurrent reads/writes, and custom callback execution under lock.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretLockedManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretManager.java

Purpose: `S3SecretManager` is the primary OM contract for managing S3 access secrets associated with Kerberos principals or access IDs. It combines lookup, persistence, revocation, cache management, lock-scoped callbacks, and optional batch support.

Important APIs and types: Core methods are `getSecret`, `getSecretString`, `storeSecret`, `revokeSecret`, `clearS3Cache`, `doUnderLock`, `batcher`, and `cache`. Defaults include `hasS3Secret`, `isBatchSupported`, `updateCache`, `invalidateCacheEntry`, and `clearCache`.

Control flow: The interface supplies null-safe cache default methods. Concrete implementations decide store semantics, exception mapping, and whether `doUnderLock` is supported directly or only through `S3SecretLockedManager`.

State and persistence behavior: Implementations persist to `s3SecretTable` via `S3SecretStore` and maintain transient cache state through `S3SecretCache`. Batch support allows secrets to participate in atomic OM metadata writes.

Dependencies and integration points: S3 gateway authentication, tenant assignment, secret revocation requests, OM double-buffer flush handling, and audit paths all interact with this manager.

Risks and test signals: Cache defaults log access IDs and rely on implementations to avoid caching stale or deleted values. Tests should cover null cache and null batcher cases, `hasS3Secret` after revoke, secret string lookup failures, and cache clearing after transaction flushes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretManagerImpl.java

Purpose: `S3SecretManagerImpl` is the store-and-cache implementation of `S3SecretManager`. It validates access IDs, reads through the cache, writes through to the configured `S3SecretStore`, and exposes the store's batcher.

Important APIs and types: Methods include `getSecret`, `getSecretString`, `storeSecret`, `revokeSecret`, `clearS3Cache`, `batcher`, `cache`, and `updateCache`. It uses `S3SecretValue`, `S3SecretStore`, `S3SecretCache`, Guava `Preconditions`, and `OzoneSecurityException` with `S3_SECRET_NOT_FOUND`.

Control flow: `getSecret` rejects blank IDs, checks cache, returns null for cached deleted markers, otherwise loads from the store and caches non-null results. `getSecretString` follows similar cache-first logic but throws `OzoneSecurityException` if the store has no entry. `storeSecret` writes to the store and then cache; `revokeSecret` deletes from the store and invalidates the cache. Direct `doUnderLock` throws because locking is provided by the wrapper.

State and persistence behavior: Persistent state lives in the store. Runtime state is the injected cache. Store writes happen before cache updates; revocation writes happen before cache invalidation.

Dependencies and integration points: It is used by OM S3 and tenant request handlers and is commonly wrapped by `S3SecretLockedManager` for concurrency control.

Risks and test signals: Cache and store can diverge if store writes succeed and cache mutation fails only partially, or if callers use the unlocked manager concurrently. `getSecretString` does not special-case deleted cached values, so deleted markers must return an appropriate secret value or be absent for this path. Tests should cover blank IDs, missing secrets, deleted cache markers, store/cache order, and unsupported direct lock callbacks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretStore.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretStore.java

Purpose: `S3SecretStore` abstracts the durable storage backend for S3 secret values. It keeps `S3SecretManagerImpl` independent of the exact OM DB table or test store implementation.

Important APIs and types: The interface exposes `storeSecret`, `getSecret`, `revokeSecret`, and `batcher`. It stores and returns `S3SecretValue` by Kerberos/access ID string.

Control flow: Implementations perform table operations and may return null for missing secrets. `batcher` returns an `S3Batcher` when the store can participate in external batch operations, otherwise null.

State and persistence behavior: Durable state is the secret table, usually OM `s3SecretTable`. The interface itself holds no state.

Dependencies and integration points: It is injected into `S3SecretManagerImpl`, included in tenant and S3 request persistence, and represented in `OMDBDefinition`.

Risks and test signals: Store implementations must define whether `revokeSecret` is idempotent and how IO failures propagate. Tests should verify table key selection, null-on-missing behavior, batcher availability, and compatibility with cache invalidation after revocation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ScmClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ScmClient.java

Purpose: `ScmClient` wraps OM's SCM block and container-location protocol clients and adds cache layers for container pipelines and datanode details. It reduces repeated SCM lookups while avoiding reuse of invalid empty or incomplete EC pipelines.

Important APIs and types: Constructor inputs are `ScmBlockLocationProtocol`, `StorageContainerLocationProtocol`, and `OzoneConfiguration`. Public methods include `getBlockClient`, `getContainerClient`, `getContainerLocations`, and `close`. Static helpers create the container location `LoadingCache`, create the datanode cache, and rebuild a pipeline using canonical cached `DatanodeDetails`.

Control flow: `getContainerLocations` optionally invalidates requested IDs, calls `containerLocationCache.getAll`, filters returned pipelines that are empty or EC pipelines missing any data replica index, invalidates those bad entries, and returns the result. Cache loading calls SCM single or batch APIs and normalizes datanode objects through `newPipelineWithDNCache`. Missing containers from `InvalidCacheLoadException` return only already cached present pipelines.

State and persistence behavior: State is transient Guava cache state plus metrics registered through `CacheMetrics`. No disk state is written. Cache expiry and size are controlled by OM config keys.

Dependencies and integration points: OM key lookup and block-location response paths use this wrapper to resolve container pipelines. It depends on SCM protocols, `Pipeline`, `DatanodeDetails`, replication configs, and Ozone cache metrics.

Risks and test signals: Returning invalid pipelines while also invalidating them means callers must tolerate the current result containing unusable entries. EC completeness checks only verify data indexes, not parity indexes. Tests should cover force refresh, batch load partial misses, datanode detail reuse after hostname/IP changes, empty pipeline invalidation, insufficient EC pipeline invalidation, and metrics unregister on close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ScmClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ServiceInfoProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ServiceInfoProvider.java

Purpose: `ServiceInfoProvider` assembles `ServiceInfoEx` responses for OM clients by combining the OM service list with cached CA certificate PEM strings in secure clusters. It also refreshes certificate cache state on root CA rotation.

Important APIs and types: Construction receives `SecurityConfig`, `OzoneManagerProtocol`, `CertificateClient`, and an optional testing skip flag. `provide()` returns `ServiceInfoEx`. Private helpers choose root CA certificates, select the newest certificate by `notAfter`, convert to PEM, and build a root-CA-rotation listener.

Control flow: In secure mode, the constructor reads root CA certs, falls back to all CA certs if root certs are empty, stores a newest PEM and a list of all PEMs, and registers a listener. The listener synchronizes on the provider, refreshes both fields, and completes a `CompletableFuture`. `provide` copies the cached fields under the same monitor and combines them with `om.getServiceList()`.

State and persistence behavior: Cached PEM strings are in-memory only. Persistent certificate material is owned by the certificate client and SCM/OM security subsystem.

Dependencies and integration points: It backs OM service-list RPCs used by clients that need service endpoints and trust roots. It depends on `CertificateClient`, `CertificateCodec`, and `ServiceInfoEx`.

Risks and test signals: Certificate conversion exceptions are wrapped as runtime exceptions during construction or listener execution. If there are no certs, the newest PEM is null and list may be empty. Tests should cover security disabled, skipped initialization, root-vs-all CA fallback, rotation listener refresh, defensive copy from `provide`, and PEM conversion failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ServiceInfoProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ServiceListJSONServlet.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ServiceListJSONServlet.java

Purpose: `ServiceListJSONServlet` exposes OM's service list as pretty-printed JSON over the OM HTTP server, typically under `/serviceList`.

Important APIs and types: It extends `HttpServlet`, reads the `OzoneManager` from `OzoneConsts.OM_CONTEXT_ATTRIBUTE` in `init`, and implements `doGet`. It uses Jackson `ObjectMapper` with `SerializationFeature.INDENT_OUTPUT`.

Control flow: `doGet` sets the JSON content type, obtains the response writer, serializes `om.getServiceList()`, writes it, and closes the writer in a finally block. IO exceptions are logged and mapped to HTTP 500.

State and persistence behavior: The servlet keeps a transient reference to `OzoneManager` and persists nothing. Response content reflects live OM service metadata.

Dependencies and integration points: It integrates with OM's embedded HTTP server and the service discovery data used by clients and diagnostics.

Risks and test signals: Null OM context would cause failures on request. Closing the writer is acceptable but makes further servlet filters unable to append. Tests should cover JSON content type, successful serialization, missing/failed OM service list handling, and HTTP 500 on writer or serialization errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ServiceListJSONServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SnapshotChainInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SnapshotChainInfo.java

Purpose: `SnapshotChainInfo` is the node model for OM's in-memory snapshot chains. Each node stores its own snapshot UUID and links to previous and next snapshot UUIDs.

Important APIs and types: It exposes setters for previous and next IDs, getters for all three UUIDs, boolean `hasNextSnapshotId` and `hasPreviousSnapshotId`, plus `equals` and `hashCode`.

Control flow: There is no complex control flow; `SnapshotChainManager` mutates these nodes when adding or deleting snapshots from global and path-specific linked lists.

State and persistence behavior: State is mutable in memory. The durable source of truth is `SnapshotInfo` in `snapshotInfoTable`, where previous IDs are persisted and used to rebuild chains on startup.

Dependencies and integration points: It is used exclusively by `SnapshotChainManager` and test inspection helpers.

Risks and test signals: The class allows arbitrary mutation, so manager invariants must be enforced outside it. Tests should compare node equality before and after link rewrites and verify add/delete operations update both neighboring nodes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SnapshotChainInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SnapshotChainManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SnapshotChainManager.java

Purpose: `SnapshotChainManager` builds and maintains in-memory linked chains of snapshots: one global chronological chain and one chain per snapshot path. It provides navigation APIs used by snapshot diff, deletion, and snapshot metadata services.

Important APIs and types: It stores `globalSnapshotChain`, `snapshotChainByPath`, `latestSnapshotIdByPath`, `snapshotIdToTableKey`, `latestGlobalSnapshotId`, and `oldestGlobalSnapshotId`. Public methods include `addSnapshot`, `updateSnapshot`, `deleteSnapshot`, `removeFromSnapshotIdToTable`, global/path latest getters, global iterator, next/previous queries, `getTableKey`, and test accessors.

Control flow: Construction loads `snapshotInfoTable`, builds a map of snapshot IDs to `SnapshotInfo`, builds a previous-to-next map for global links, identifies the head, then walks forward calling `addSnapshot`. Adds validate non-duplication, head placement, known predecessors, and linear next-link constraints before updating neighbor nodes and latest pointers. Deletes validate neighboring links, remove the node, stitch previous and next nodes together, and update latest/oldest path/global pointers. All mutating public methods are synchronized and first validate that startup loading did not mark the chain corrupted.

State and persistence behavior: In-memory maps are rebuilt from `SnapshotInfo` persisted in RocksDB. This class does not itself persist chain changes; callers must update `snapshotInfoTable` consistently. `snapshotIdToTableKey` tracks table keys for snapshot lookup and rename updates.

Dependencies and integration points: It depends on `OMMetadataManager`, `SnapshotInfo`, `TableIterator`, and snapshot services. Snapshot deletion, diff iteration, purge, and snapshot rename code rely on its navigation and table-key mapping.

Risks and test signals: Startup load expects exactly one global head and a complete linear chain; branching, cycles, duplicate heads, or missing links mark the manager corrupted and all validation-gated APIs fail. Some getters return internal maps directly for tests. Tests should cover load corruption cases, add/delete in head/middle/tail positions, path-specific latest maintenance, iterator forward/reverse behavior, renamed snapshot table-key updates, and concurrent readers during synchronized mutation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SnapshotChainManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SnapshotListJSONServlet.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SnapshotListJSONServlet.java

Purpose: `SnapshotListJSONServlet` exposes a JSON snapshot listing endpoint for a given volume and bucket through the OM HTTP server.

Important APIs and types: It extends `HttpServlet`, loads `OzoneManager` from servlet context, defines a Jackson mix-in to ignore protobuf and transaction-info getters on `SnapshotInfo`, and implements `doGet`.

Control flow: `doGet` validates required `volume` and `bucket` request parameters, reads optional `prefix`, then repeatedly calls `om.listSnapshot(volume, bucket, prefix, lastSnapshot, 1000)` until the response has no next marker. Each page's snapshot info list is serialized to the same writer.

State and persistence behavior: The servlet persists nothing. It streams live snapshot metadata from OM's snapshot listing API.

Dependencies and integration points: It integrates with OM HTTP diagnostics and snapshot metadata management. It depends on `ListSnapshotResponse`, `SnapshotInfo`, and Jackson serialization.

Risks and test signals: Writing each page as a separate JSON array produces concatenated arrays rather than one enclosing JSON document when multiple pages exist. Parameter errors return 400 with text, while all other exceptions return 500. Tests should cover missing parameters, mix-in serialization, paginated output shape, and exceptions from `om.listSnapshot`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SnapshotListJSONServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SstFilteringService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SstFilteringService.java

Purpose: `SstFilteringService` is a single-threaded background service that removes irrelevant RocksDB SST files from snapshot directories. It reduces snapshot footprint by deleting files whose prefixes do not correspond to the snapshotted bucket, and marks snapshots as filtered.

Important APIs and types: It extends `BackgroundService` and implements `BootstrapStateHandler`. Key public elements are `SST_FILTERED_FILE`, `isSstFiltered`, `start`, test-only `pause` and `resume`, `getTasks`, `getSnapshotFilteredCount`, `getBootstrapStateLock`, and `shutdown`. The inner `SstFilteringTask` performs the actual iteration.

Control flow: Each task scans `snapshotInfoTable` from the beginning while the per-task limit remains and the service is running. It skips already-filtered snapshots and snapshots whose local data version indicates defrag already handled filtering. For each eligible snapshot, it computes the bucket table-prefix set, acquires the bootstrap read lock, opens the active snapshot, calls `RocksDatabase.deleteFilesNotMatchingPrefix`, writes an `sstFiltered` marker file under the snapshot directory while holding `SNAPSHOT_DB_LOCK` read lock, decrements the limit, and increments the filtered count. Deleted snapshots and missing active snapshots are handled specially to avoid noisy failures.

State and persistence behavior: Durable effects are deletion of SST files from snapshot RocksDB directories and creation of the marker file. SnapshotInfo's own `isSstFiltered` field may also be consulted if updated elsewhere. Runtime state includes `running`, `snapshotFilteredCount`, and bootstrap lock wrapper state.

Dependencies and integration points: It integrates with `OmSnapshotManager`, `OmSnapshotLocalDataManager`, OM metadata tables, RocksDB prefix filtering, `SNAPSHOT_DB_LOCK`, and bootstrap state locking.

Risks and test signals: Incorrect prefix computation or lock ordering could delete needed snapshot SST files or race with snapshot deletion/defrag. The task scans from the start each cycle, so many already-filtered snapshots can create repeated iteration cost. Tests should cover marker detection, defrag skip, deleted-midway handling, batch limit enforcement, pause/resume, bootstrap lock use, and that filtered snapshot DBs still serve relevant bucket metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SstFilteringService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/TenantOp.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/TenantOp.java

Purpose: `TenantOp` defines the private, unstable interface for authorizer-side multi-tenant operations, primarily Ranger role and policy management plus tenant user/admin assignment.

Important APIs and types: Methods are `createTenant`, `deleteTenant`, `assignUserToTenant`, `revokeUserAccessId`, `assignTenantAdmin`, and `revokeTenantAdmin`. It depends on the multi-tenant `Tenant` model and throws `IOException`.

Control flow: The interface has no implementation. Concrete authorizer integrations perform external side effects such as creating or deleting Ranger roles and policies and updating privileges for access IDs.

State and persistence behavior: State is external to OM DB and typically held in Ranger or another authorizer. OM request handlers must coordinate this external state with OM's tenant tables.

Dependencies and integration points: It is the bridge from OM tenant metadata operations to the authorization backend.

Risks and test signals: Distributed consistency is the central risk: Ranger updates and OM DB updates may fail independently. Tests should cover idempotent create/delete, rollback or retry behavior, missing access IDs, delegated admin semantics, and exception mapping from the authorizer.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/TenantOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/TrashOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/TrashOzoneFileSystem.java

Purpose: `TrashOzoneFileSystem` is a minimal `FileSystem` implementation used by the OM trash emptier. It implements only the filesystem operations the trash policy needs and converts them into OM requests submitted through Ratis.

Important APIs and types: Implemented operations include `getUri`, `rename`, `delete`, `listStatus`, `getFileStatus`, `getTrashRoots`, `exists`, `mkdirs`, and working-directory methods. Unsupported file IO methods throw `UnsupportedOperationException`. Internal helpers build `RenameKey`, `DeleteKey`, and `DeleteKeys` `OMRequest` messages and submit them after `preExecute`.

Control flow: For FSO buckets, `rename` and `delete` send one recursive/atomic OM request for the path. For non-FSO buckets, `RenameIterator` and `DeleteIterator` list all keys under the path in batches, convert each key to an `OFSPath`, build per-key requests, and submit them. Listing uses OM metadata manager list APIs and batches with `OZONE_FS_ITERATE_BATCH_SIZE` and `OZONE_MAX_LIST_KEYS_SIZE`. `getTrashRoots` enumerates user trash roots from bucket/key metadata and filters existence.

State and persistence behavior: The class persists nothing directly. It mutates OM metadata through Ratis-submitted requests and increments OM trash metrics. `runCount` supplies monotonically increasing call IDs per instance, and `CLIENT_ID` is static.

Dependencies and integration points: It connects `TrashPolicyOzone` with `OzoneManager`, `OFSPath`, OM request classes, Ratis submission utilities, OM metadata list/status APIs, and user info from `UserGroupInformation`.

Risks and test signals: Non-FSO rename/delete is multi-request and can be partially applied if a later key request fails; errors inside iterators are logged but do not necessarily abort. Path parsing and trash-root equality checks are critical. Tests should cover FSO atomic rename/delete, OBS recursive iteration, batch boundaries, non-empty delete behavior, missing paths, trash root enumeration across users, metrics increments, and Ratis failure handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/TrashOzoneFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/TrashPolicyOzone.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/TrashPolicyOzone.java

Purpose: `TrashPolicyOzone` specializes Hadoop trash behavior for OM. It uses an Ozone-aware filesystem and a multithreaded emptier to checkpoint current trash directories and delete expired checkpoints.

Important APIs and types: It extends `OzoneTrashPolicy`, overrides `initialize` and `getEmptier`, and defines an inner `Emptier`. Private methods `createCheckpoint`, `deleteCheckpoint`, and `getTimeFromCheckpoint` implement checkpoint lifecycle. It uses `OMClientConfig` for trash emptier pool size and OM metrics for activity/failure counters.

Control flow: Initialization chooses an Ozone-specific checkpoint interval with fallback to Hadoop's config and clamps negative deletion interval to zero. The emptier sleeps until the next interval boundary, skips work unless OM leader is ready, lists all trash roots, creates a new `TrashPolicyOzone` per root, and submits a task that deletes expired checkpoints then renames `Current` to a timestamped checkpoint. Checkpoint creation retries suffixes up to 1000 times on name collision.

State and persistence behavior: Durable state is trash checkpoint directories under each trash root. Runtime state includes the configured intervals and a fixed-size executor. Date formats are static and synchronized for thread safety.

Dependencies and integration points: It integrates with `TrashOzoneFileSystem`, OM leadership, OM metrics, Hadoop `TrashPolicy`, and Ozone client configuration.

Risks and test signals: It only runs on a leader-ready OM, so leadership transitions affect cleanup latency. The executor queue can run tasks in the caller when saturated. Tests should cover interval fallback, disabled trash, checkpoint collision retries, old-format checkpoint parsing, deletion cutoff boundaries, leader skip behavior, executor shutdown on interrupt, and metrics on success/failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/TrashPolicyOzone.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/VolumeManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/VolumeManager.java

Purpose: `VolumeManager` defines read-side volume operations for OM and inherits volume ACL behavior through `IOzoneAcl`.

Important APIs and types: It declares `getVolumeInfo(String volume)` and `listVolumes(String userName, String prefix, String startKey, int maxKeys)`, returning `OmVolumeArgs` records.

Control flow: The interface has no implementation. `VolumeManagerImpl` performs metadata lookups under locks and maps missing volumes to `OMException`.

State and persistence behavior: Implementations read persistent `volumeTable` and user-volume metadata. The interface owns no state.

Dependencies and integration points: OM RPC handlers use this contract to serve volume info/list/ACL requests. It depends on `OmVolumeArgs` and the ACL subsystem.

Risks and test signals: Listing semantics around `startKey`, prefix, maxKeys, and user-null global listing must be consistent with client expectations. Tests should cover missing volumes, ACL access checks, user-filtered lists, and pagination.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/VolumeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/VolumeManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/VolumeManagerImpl.java

Purpose: `VolumeManagerImpl` implements read-only volume metadata and ACL checks over `OMMetadataManager`.

Important APIs and types: It implements `getVolumeInfo`, `listVolumes`, `getAcl`, and `checkAccess`. It uses `VOLUME_LOCK`, `USER_LOCK`, `OmVolumeArgs`, `OzoneObj`, `RequestContext`, `OzoneAclUtil`, and `OMException.ResultCodes`.

Control flow: `getVolumeInfo` requires a non-null volume, acquires `VOLUME_LOCK`, reads `volumeTable`, and throws `VOLUME_NOT_FOUND` if absent. `listVolumes` acquires `USER_LOCK` only for user-filtered listings and delegates to `metadataManager.listVolumes`. `getAcl` validates the resource type is volume, reads the volume under lock, and returns its ACL list. `checkAccess` reads the same volume and delegates ACL evaluation to `OzoneAclUtil.checkAclRights`, wrapping unexpected IO in an internal-error `OMException`.

State and persistence behavior: The class is stateless except for its metadata manager reference. It reads persistent volume metadata and does not write tables.

Dependencies and integration points: OM volume request handlers and ACL authorizer paths call this implementation. It relies on lock ordering enforced by OM lock trackers.

Risks and test signals: Returning the underlying ACL list may expose mutable metadata depending on `OmVolumeArgs` implementation. `listVolumes` only locks the user table, not all volume rows. Tests should cover missing volumes, invalid resource type, lock release on exceptions, ACL true/false results, and user-specific listing under concurrent volume changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/VolumeManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/codec/OMDBDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/codec/OMDBDefinition.java

Purpose: `OMDBDefinition` is the authoritative column-family and codec definition for the OM RocksDB database. It maps every logical OM table to a `DBColumnFamilyDefinition` with key and value codecs.

Important APIs and types: It defines constants and definitions for user, delegation token, S3 secret, volume, bucket, prefix, transaction info, meta, key, deleted, open key, multipart, FSO file/open file/directory/deleted directory, tenant state/access/principal, snapshot info, snapshot renamed, and compaction log tables. `get()` returns a singleton, `getName()` returns the OM DB name, `getLocationConfigKey()` returns the OM DB directory config, and `getAllColumnFamilies()` lists defined CF names.

Control flow: Static initialization constructs each typed column-family definition, builds an unmodifiable map, and initializes the singleton. There is no runtime mutation.

State and persistence behavior: This class defines persistent schema shape, names, and serialization for OM metadata. Changing table names or codecs affects upgrade compatibility and snapshot DB compatibility.

Dependencies and integration points: It is used by OM metadata manager/store initialization, DB tooling, snapshots, compaction logs, and codec validation. It ties to many helper model codecs, `TokenIdentifierCodec`, protobuf codecs, and transaction info codecs.

Risks and test signals: Schema drift is high-risk: missing a new table from `COLUMN_FAMILIES`, changing order-sensitive consumers, or changing codecs can break upgrades and snapshots. Tests should verify all metadata manager table names are represented, `getAllColumnFamilies` contains expected names, old DBs decode correctly, and token/secret/snapshot/tenant tables use compatible codecs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/codec/OMDBDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/codec/TokenIdentifierCodec.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/codec/TokenIdentifierCodec.java

Purpose: `TokenIdentifierCodec` serializes and deserializes `OzoneTokenIdentifier` keys for OM's delegation token table.

Important APIs and types: It is a singleton `Codec<OzoneTokenIdentifier>` exposed by `get()`. It implements `getTypeClass`, `toPersistedFormat`, `fromPersistedFormatImpl`, and `copyObject`.

Control flow: Serialization requires a non-null token and writes its protobuf bytes. Deserialization first tries `OzoneTokenIdentifier.readProtoBuf`; if that fails, it tries the legacy `fromUniqueSerializedKey` format and suppresses the first exception on the second if both fail.

State and persistence behavior: The codec is stateless. It defines persistent encoding for delegation token table keys and preserves backward compatibility with older unique-key serialization.

Dependencies and integration points: `OMDBDefinition.DELEGATION_TOKEN_TABLE_DEF` uses this codec. Token managers depend on it to read existing tokens after upgrade.

Risks and test signals: `copyObject` returns the same mutable object if `OzoneTokenIdentifier` is mutable. Tests should cover protobuf round trips, legacy bytes fallback, double-failure suppressed exceptions, null serialization rejection, and compatibility with existing token DB entries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/codec/TokenIdentifierCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/codec/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/codec/package-info.java

Purpose: This package descriptor documents `org.apache.hadoop.ozone.om.codec` as containing byte-array encoders/decoders and OM DB definitions.

Important APIs and types: It exports no runtime type directly. Key package classes are `OMDBDefinition` and `TokenIdentifierCodec`.

Control flow: No executable control flow is present.

State and persistence behavior: No state is held here. The package's concrete classes define persistent OM DB encodings.

Dependencies and integration points: JavaDoc and package ownership only; runtime integration belongs to the package classes.

Risks and test signals: The only risk is documentation drift if codec responsibilities move. No direct tests are needed beyond package class tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/codec/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/OMExecutionFlow.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/OMExecutionFlow.java

Purpose: `OMExecutionFlow` is the entry point for submitting external OM requests into the current execution pipeline. Today it primarily wraps write request pre-execution and Ratis submission, leaving room for future non-Ratis flow control.

Important APIs and types: Constructor accepts `OzoneManager`. `submit(OMRequest omRequest, boolean isWrite)` returns `OMResponse` or throws `ServiceException`. Internally it uses `OMClientRequest`, `OzoneManagerRatisUtils`, `OMPerformanceMetrics`, and `OMAuditLogger`.

Control flow: `submit` delegates to `submitExecutionToRatis`. For writes, it creates an `OMClientRequest`, records preExecute latency, calls `preExecute`, and on preExecute failure logs existing audit state, invokes `handleRequestFailure`, and returns an error response. Then it submits to `ozoneManager.getOmRatisServer().submitRequest(requestToSubmit, isWrite)`. If the response is unsuccessful, it invokes request failure handling.

State and persistence behavior: This class has no durable state. It triggers durable state changes by submitting write requests to OM Ratis and updates performance metrics.

Dependencies and integration points: It sits between RPC handlers and the OM Ratis server, integrating request construction, pre-execute mutation, audit cleanup, metrics, and Ratis submission.

Risks and test signals: Write preExecute exceptions must not leak partial side effects; non-write requests bypass preExecute. Tests should cover write success, preExecute failure audit/failure handling, unsuccessful Ratis response handling, read submission bypassing preExecute, and latency metric updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/OMExecutionFlow.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/flowcontrol/ExecutionContext.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/flowcontrol/ExecutionContext.java

Purpose: `ExecutionContext` is an immutable holder for the log index and Ratis `TermIndex` associated with request execution.

Important APIs and types: `of(long index, TermIndex termIndex)` constructs an instance. `getIndex` and `getTermIndex` expose fields. If termIndex is null, construction synthesizes `TermIndex.valueOf(-1, index)`.

Control flow: The only branch normalizes null term indexes to a sentinel term of -1.

State and persistence behavior: It is in-memory only and carries persisted-log coordinates from Ratis or test paths.

Dependencies and integration points: Request application and audit code can use it to pass transaction index and term information without carrying raw Ratis types everywhere.

Risks and test signals: The sentinel term may be misinterpreted if callers require a real term. Tests should cover null and non-null termIndex construction and index preservation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/flowcontrol/ExecutionContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/flowcontrol/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/flowcontrol/package-info.java

Purpose: This package descriptor identifies the package for OM execution flow-control classes.

Important APIs and types: It exports no code directly. `ExecutionContext` is the visible class in this package.

Control flow: No runtime flow exists in the descriptor.

State and persistence behavior: No state is held or persisted.

Dependencies and integration points: It provides JavaDoc/package metadata for future request execution flow-control utilities.

Risks and test signals: Documentation drift is the only meaningful concern. Behavioral tests belong to concrete classes in the package.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/flowcontrol/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/package-info.java

Purpose: This package descriptor documents the OM execution implementation package.

Important APIs and types: It exports no members directly. `OMExecutionFlow` is the package's primary class in this subset.

Control flow: No runtime control flow exists here.

State and persistence behavior: No state is held or persisted.

Dependencies and integration points: The descriptor supports generated JavaDocs and package ownership around OM request execution.

Risks and test signals: Only documentation drift matters. Tests should target `OMExecutionFlow` and future concrete execution classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/fs/OzoneManagerFS.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/fs/OzoneManagerFS.java

Purpose: `OzoneManagerFS` is the OM filesystem-view interface for file and directory status, lookup, and listing operations. It extends `IOzoneAcl`, so filesystem objects can also be checked through the common ACL layer.

Important APIs and types: It declares `getFileStatus`, `lookupFile`, and three `listStatus` overloads, with optional client address and `allowPartialPrefixes`. It uses `OmKeyArgs`, `OmKeyInfo`, and `OzoneFileStatus`.

Control flow: The interface defines no implementation. Concrete key managers perform path resolution, bucket layout handling, metadata lookup, and datanode pipeline ordering.

State and persistence behavior: Implementations read from key/file/directory tables and may shape returned key info with block locations. The interface owns no state.

Dependencies and integration points: OFS/Ozone filesystem clients and OM RPC handlers depend on this contract for filesystem-optimized and object-store listings.

Risks and test signals: Listing semantics are subtle across recursive mode, start keys, partial prefixes, bucket layouts, and client-distance pipeline ordering. Tests should cover files vs directories, missing paths, pagination inclusiveness, partial-prefix listing, ACL checks, and FSO vs OBS behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/fs/OzoneManagerFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/fs/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/fs/package-info.java

Purpose: This package descriptor identifies the Ozone Manager filesystem interface package.

Important APIs and types: It exports no code directly. `OzoneManagerFS` is the relevant interface in this package.

Control flow: No runtime flow exists.

State and persistence behavior: No state is held or persisted.

Dependencies and integration points: It contributes JavaDoc/package metadata for OM filesystem APIs.

Risks and test signals: Documentation drift is the only concern; behavior belongs to concrete implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/fs/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMHAMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMHAMetrics.java

Purpose: `OMHAMetrics` publishes metrics describing an OM node's HA identity and whether it is currently the leader.

Important APIs and types: It implements `MetricsSource`, registers under source name `OMHAMetrics`, and exposes static `create` and `unRegister`. `getMetrics` emits a `NodeId` tag and `OzoneManagerHALeaderState` gauge with value 1 for leader and 0 for follower.

Control flow: On each metrics collection, it compares `currNodeId` and `leaderId`, updates an internal info holder, emits the tag/gauge, and ends the record.

State and persistence behavior: State is process-local metric state. No persistent data is written.

Dependencies and integration points: It integrates with Hadoop metrics2, `DefaultMetricsSystem`, and OM HA leadership tracking.

Risks and test signals: `leaderId` is only constructor state in this class, so callers need a new instance or external update path if leadership changes are not represented elsewhere. Registration uses a fixed source name. Tests should cover leader/follower gauge values, node ID tag, unregister/re-register, and duplicate registration behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMHAMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMHANodeDetails.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMHANodeDetails.java

Purpose: `OMHANodeDetails` resolves OM HA configuration into local node details and peer node details. It supports explicit internal service IDs, multiple service IDs, listener nodes, flexible FQDN resolution, and non-HA fallback.

Important APIs and types: `loadOMHAConfig` is the main loader. Accessors return local details and peer map. Static helpers create non-HA or HA `OMNodeDetails` objects from service ID, node ID, RPC address, Ratis port, HTTP/HTTPS addresses, and listener status.

Control flow: The loader chooses candidate OM service IDs, reads active and listener node IDs for each service, reads RPC and Ratis addresses, resolves socket addresses, detects whether each address belongs to the local host unless an explicit node ID forces peer status, builds peer details, and returns when exactly one local match is found. If no node-specific OM address is configured, it falls back to default non-HA OM address. Configuration errors throw `OzoneIllegalArgumentException`.

State and persistence behavior: Instances are immutable references to local and peer node lists. The loader mutates the provided configuration by applying node-specific config overrides through `ConfUtils.setNodeSpecificConfigs`.

Dependencies and integration points: It is used during OM startup and Ratis ring construction. It depends on `OzoneConfiguration`, `OmUtils`, `ConfUtils`, `OzoneNetUtils`, Hadoop `NetUtils`, and `OMNodeDetails`.

Risks and test signals: Local address detection can be tricky with unresolved hosts, aliases, containers, and multi-homed nodes. Multiple local matches or no matches block startup. Tests should cover explicit node ID, multiple service IDs, listener nodes, unresolved flexible FQDN behavior, missing RPC address, non-HA fallback, duplicate local matches, and node-specific HTTP/HTTPS config substitution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMHANodeDetails.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMPeriodicMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMPeriodicMetrics.java

Purpose: `OMPeriodicMetrics` is a reusable framework for metrics that need periodic recomputation on a single daemon thread.

Important APIs and types: Subclasses implement `updateMetrics()` returning true on successful update. Public methods are `start`, `stop`, and `getLastUpdateTime`. Construction requires a non-empty task name and positive update interval.

Control flow: `start` is idempotent, creates a single-thread scheduled executor, and schedules `updateMetrics` with fixed delay starting immediately. Successful updates set `lastUpdateTime`; thrown exceptions are logged and do not stop scheduling. `stop` cancels without interrupting current work, shuts down the executor, waits up to 30 seconds, then forces shutdown and waits briefly if needed.

State and persistence behavior: Runtime state includes executor, future, last update timestamp, task name, interval, and a `started` flag. No durable state is written.

Dependencies and integration points: OM HA and background metric sources can subclass it to decouple metric calculations from request paths.

Risks and test signals: `started` is volatile but `start`/`stop` are not synchronized, so concurrent calls can race. A long-running `updateMetrics` delays shutdown. Tests should cover constructor validation, duplicate start, exception handling, timestamp update only on true, stop before start, forced shutdown, and concurrent start/stop behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMPeriodicMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMService.java

Purpose: `OMService` defines a lifecycle and status-notification contract for stateful OM background services that react to HA or safe-mode state changes.

Important APIs and types: Methods include `notifyStatusChanged`, `shouldRun`, `getServiceName`, `start`, and `stop`. `ServiceStatus` currently contains `RUNNING` and `PAUSING`.

Control flow: The interface defines no implementation. `OMServiceManager` calls these methods on registered services.

State and persistence behavior: Implementations decide their own runtime state and persistence. The interface carries no state.

Dependencies and integration points: OM background services can implement this to pause/resume based on leadership, Ratis readiness, or safe mode.

Risks and test signals: Implementations need clear semantics for `shouldRun` around leadership transitions. Tests should cover manager notification, start failure handling, stop idempotence, and paused service behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMServiceException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMServiceException.java

Purpose: `OMServiceException` is the checked exception type used by `OMService.start()`.

Important APIs and types: It extends `Exception` and provides default, message, message-plus-cause, and cause-only constructors.

Control flow: There is no custom control flow.

State and persistence behavior: It carries exception state only and persists nothing.

Dependencies and integration points: `OMServiceManager.start` catches this exception and logs a warning while continuing with other services.

Risks and test signals: This is straightforward. Tests should verify service manager catches it and does not prevent later services from starting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMServiceException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMServiceManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMServiceManager.java

Purpose: `OMServiceManager` registers and coordinates OM background services implementing `OMService`.

Important APIs and types: Public synchronized methods are `register`, `notifyStatusChanged`, `start`, and `stop`. It stores services in an `ArrayList`.

Control flow: `register` rejects null and appends the service. `notifyStatusChanged` iterates and calls each service. `start` iterates all services, catching and logging `OMServiceException` so one service failure does not block the rest. `stop` iterates and calls `stop` without exception handling.

State and persistence behavior: State is in-memory service registration order. No durable data is written.

Dependencies and integration points: OM startup and shutdown code use it to coordinate services that depend on HA readiness or safe mode state.

Risks and test signals: All methods synchronize on the manager, so a slow service callback blocks registration and other lifecycle operations. `stop` does not isolate runtime exceptions. Tests should cover registration order, null rejection, start continuation after checked failure, status notifications, stop ordering, and behavior when a service throws unchecked exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMServiceManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/package-info.java

Purpose: This package descriptor documents that `org.apache.hadoop.ozone.om.ha` contains classes related to OM high availability.

Important APIs and types: It exports no code directly. Key package classes include `OMHANodeDetails`, `OMHAMetrics`, `OMService`, `OMServiceManager`, and `OMPeriodicMetrics`.

Control flow: No runtime flow is present.

State and persistence behavior: No state is held or persisted.

Dependencies and integration points: It supports JavaDoc/package metadata for OM HA code.

Risks and test signals: Documentation drift is the only concern. Behavioral tests belong to concrete HA classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/helpers/OMAuditLogger.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/helpers/OMAuditLogger.java

Purpose: `OMAuditLogger` centralizes mapping OM request command types to audit actions and provides helper methods for writing audit log messages during request execution and failure handling.

Important APIs and types: Static `CMD_AUDIT_ACTION_MAP` maps protobuf `Type` to `OMAction`. Public `log` overloads write an already-built builder, add transaction index, or build audit data from an `OMClientRequest`, `OzoneManager`, `TermIndex`, and throwable. `Builder` holds `AuditMessage.Builder`, `AuditLogger`, audit params, and an `AtomicBoolean` log flag.

Control flow: Static initialization populates the command-action map. `getAction` special-cases `SetVolumeProperty` quota updates and `SetBucketProperty` owner updates. The request-aware `log` method either writes an already-prepared message or maps command to action, populates command and transaction parameters, asks the client request to build the audit message, marks the builder as logged, and writes through OM's audit logger.

State and persistence behavior: Static mapping is process state. Audit persistence is external to this class through the configured audit logger sink.

Dependencies and integration points: It is used by OM request execution, Ratis application, and failure paths. It depends on `AuditLogger`, `AuditMessage`, `OMAction`, protobuf command types, and `OMClientRequest`.

Risks and test signals: Missing map entries silently suppress audit logs. Builder state is mutable and can be reused incorrectly. Tests should cover every auditable command mapping, quota/owner special cases, transaction parameter insertion, already-logged short circuit, exception handling during audit message construction, and no log for unmapped commands.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/helpers/OMAuditLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/helpers/OmFSOFile.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/helpers/OmFSOFile.java

Purpose: `OmFSOFile` is a helper value object for file-system-optimized buckets. It precomputes volume ID, bucket ID, parent ID, and file name for a key path so request handlers can build FSO table keys consistently.

Important APIs and types: The nested `Builder` accepts volume, bucket, key, `OMMetadataManager`, and an optional error message. `build` derives file name with `OzoneFSUtils.getFileName`, volume and bucket IDs from metadata, and parent ID through `OMFileRequest.getParentID`. Instance methods expose all fields plus `getOpenFileName(clientID)` and `getOzonePathKey()`.

Control flow: Building performs all metadata lookups and parent-path resolution, then constructs an immutable-ish object. The path-key methods delegate to metadata manager key-construction helpers.

State and persistence behavior: The object is transient. It describes persistent FSO table key coordinates for `fileTable`, `openFileTable`, and related directory tables.

Dependencies and integration points: FSO file create/commit/lookup/delete request classes can use it to avoid duplicating parent ID and table-key derivation logic.

Risks and test signals: Builder fields are not validated for null before use, so errors surface from metadata manager or path helpers. Tests should cover root-level files, nested parent resolution, missing parent errors, volume/bucket ID lookup failures, open file key construction, and object path key construction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/helpers/OmFSOFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/helpers/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/helpers/package-info.java

Purpose: This package descriptor documents `org.apache.hadoop.ozone.om.helpers` as the package for Ozone Manager helper classes.

Important APIs and types: It exports no code directly. This subset includes `OMAuditLogger` and `OmFSOFile`, while the full package contains many OM metadata helper types.

Control flow: No runtime flow exists.

State and persistence behavior: No state is held or persisted.

Dependencies and integration points: It supports JavaDoc/package metadata for OM helper models and utilities.

Risks and test signals: Documentation drift is the only direct risk. Concrete helper classes need their own tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/helpers/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/DAGResourceLockTracker.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/DAGResourceLockTracker.java

Purpose: `DAGResourceLockTracker` enforces lock acquisition constraints for `DAGLeveledResource` values using a dependency DAG. It prevents a thread from acquiring an ancestor-style resource after it already holds dependent child resources.

Important APIs and types: It extends `ResourceLockTracker<DAGLeveledResource>`, is a package-private singleton exposed by `get`, and implements `canLockResource`, `lockResource`, `unlockResource`, and `getCurrentLockedResources`. It maintains an `EnumMap` of per-resource `ThreadLocal<Integer>` hold counts and a precomputed dependency adjacency map.

Control flow: Construction traverses every DAG resource with iterative DFS, building for each resource the transitive set of child resources that block later acquisition. `lockResource` and `unlockResource` update the thread-local count and delegate to the base tracker for details. `canLockResource` returns false if the current thread holds any dependent child resource.

State and persistence behavior: State is process-local, per-thread lock tracking plus static singleton state. No durable state is written.

Dependencies and integration points: It backs OM lock validation for DAG-style resources such as bootstrap and snapshot DB locks.

Risks and test signals: The DFS assumes child adjacency entries are populated before parent computation and the graph is acyclic. Unlocking more times than locking can drive counts negative unless the base tracker guards it. Tests should cover transitive dependency denial, independent lock allowance, reentrant lock counts, singleton thread isolation, and invalid DAG/cycle behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/DAGResourceLockTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/LeveledResourceLockTracker.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/LeveledResourceLockTracker.java

Purpose: `LeveledResourceLockTracker` enforces traditional OM lock-level ordering for `OzoneManagerLock.LeveledResource` values using a per-thread bitset.

Important APIs and types: It is a package-private singleton extending `ResourceLockTracker<OzoneManagerLock.LeveledResource>`. It uses `ThreadLocal<Short> lockSet` and implements `canLockResource`, `getCurrentLockedResources`, `lockResource`, and `unlockResource`.

Control flow: `canLockResource` delegates to the resource's `canLock` method against the current bitset. Locking sets the resource bit before delegating to the base tracker; unlocking clears the bit. Current locked resources are streamed by checking each enum value's bit.

State and persistence behavior: All state is process-local and per-thread. No persistent data is written.

Dependencies and integration points: It supports `OzoneManagerLock` enforcement for volume, bucket, key, user, prefix, and other leveled locks.

Risks and test signals: A single bit per resource cannot represent reentrant hold counts; correctness depends on the surrounding lock implementation and base tracker semantics. Tests should cover lock-order acceptance/denial, reentrant acquire/release behavior, thread isolation, and bitset cleanup after exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/LeveledResourceLockTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OBSKeyPathLockStrategy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OBSKeyPathLockStrategy.java

Purpose: `OBSKeyPathLockStrategy` is the object-store bucket lock strategy that combines a bucket read lock with a key-path read or write lock. It allows finer-grained key locking while keeping bucket metadata stable.

Important APIs and types: It implements `OzoneLockStrategy` methods for read/write acquire and release. It uses `BUCKET_LOCK`, `KEY_PATH_LOCK`, `OMMetadataManager`, `OMFileRequest.validateBucket`, `OMLockDetails`, and Guava `Preconditions`.

Control flow: Acquire methods first validate the bucket, acquire a bucket read lock, assert acquisition, then acquire the key-path lock and merge lock details. Release methods release the key-path lock first, then the bucket read lock, merging details.

State and persistence behavior: The strategy stores no state. It coordinates in-memory lock state around persistent key-table or file-table operations.

Dependencies and integration points: `OzoneLockProvider` chooses this strategy for object-store buckets and some legacy buckets when key-path locking is enabled.

Risks and test signals: If key-path lock acquisition fails after bucket lock acquisition, the current method does not explicitly release the bucket lock before propagating. Tests should cover successful read/write lock pairs, bucket validation failure, release order, merged lock details, and failure injection during second lock acquisition.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OBSKeyPathLockStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OmReadOnlyLock.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OmReadOnlyLock.java

Purpose: `OmReadOnlyLock` is an `IOzoneManagerLock` implementation for read-only snapshot metadata managers. It allows read-lock acquisition without actually locking and rejects write-lock acquisition.

Important APIs and types: All read acquire methods return `EMPTY_DETAILS_LOCK_ACQUIRED`; write acquire/release methods and read release methods return `EMPTY_DETAILS_LOCK_NOT_ACQUIRED`. Multi-user lock acquisition returns false. Hold-count and ownership checks return zero/false. `getOMLockMetrics` throws `UnsupportedOperationException`.

Control flow: Every method is a fixed response with no mutable logic.

State and persistence behavior: There is no state. The class is intended for immutable/read-only snapshot DB contexts where writes should be impossible.

Dependencies and integration points: Snapshot metadata managers can use it to satisfy APIs that expect `IOzoneManagerLock` without introducing lock overhead.

Risks and test signals: Code that expects release after read acquire to report acquired may be surprised because releases return not acquired. Any accidental write path should see lock-not-acquired and fail upstream. Tests should cover read-only manager operations, write rejection, metrics unsupported behavior, and compatibility with code that merges `OMLockDetails`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OmReadOnlyLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OzoneLockProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OzoneLockProvider.java

Purpose: `OzoneLockProvider` chooses a concrete key lock strategy based on configuration and bucket layout.

Important APIs and types: The constructor stores `keyPathLockEnabled` and `enableFileSystemPaths`. `createLockStrategy(BucketLayout bucketLayout)` returns either `OBSKeyPathLockStrategy` or `RegularBucketLockStrategy`.

Control flow: If key-path locking is enabled, object-store buckets use `OBSKeyPathLockStrategy`. Legacy buckets also use it when filesystem paths are disabled, covering old pre-created object-store-like legacy buckets. All other cases fall back to regular bucket locking.

State and persistence behavior: State is two configuration booleans. No persistence is involved.

Dependencies and integration points: Request handlers use the selected strategy to lock keys under different bucket layouts. It depends on `BucketLayout` and lock strategy implementations.

Risks and test signals: Misclassification changes concurrency and correctness for key operations. Tests should cover all bucket layouts with both booleans, especially legacy buckets under filesystem-path enabled/disabled configs, and verify the selected strategy's locking behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OzoneLockProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OzoneLockStrategy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OzoneLockStrategy.java

Purpose: `OzoneLockStrategy` defines the strategy interface for acquiring and releasing key-related read/write locks in OM. It allows runtime selection of locking behavior by bucket layout and configuration.

Important APIs and types: It declares `acquireWriteLock`, `releaseWriteLock`, `acquireReadLock`, and `releaseReadLock`, each taking `OMMetadataManager`, volume name, bucket name, and key name. Acquire methods may throw `IOException`.

Control flow: The interface has no implementation. Concrete strategies decide whether to use bucket locks only, key-path locks, or future FSO-specific locking.

State and persistence behavior: Strategies coordinate in-memory lock state around persistent OM metadata operations. The interface owns no state.

Dependencies and integration points: `OzoneLockProvider` returns implementations, and key/file request classes use them to guard metadata reads and writes.

Risks and test signals: All implementations must pair acquisitions and releases in reverse order and release partial acquisitions on failure. Tests should apply a shared suite across strategies for read/write success, exception safety, and lock-order compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OzoneLockStrategy.java -->
