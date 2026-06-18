# subset-b-008093 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMultiTenantManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMultiTenantManagerImpl.java

Purpose: `OMMultiTenantManagerImpl` implements `OMMultiTenantManager` for Ozone Manager S3 multi-tenancy. It coordinates OM metadata tables, in-memory tenant cache, Ranger-backed authorizer state, tenant authorization checks, and the background Ranger reconciliation service.

Important APIs and types: the constructor loads tenant cache from DB, creates `MultiTenantAccessController`, installs `AuthorizerOp` and `CacheOp`, and starts `OMRangerBGSyncService`. Public APIs expose `getAuthorizerOp()`, `getCacheOp()`, `checkAdmin()`, `checkTenantAdmin()`, `checkTenantExistence()`, tenant role/name lookups, tenant emptiness checks, `getAllRolesFromCache()`, and `getAuthorizerLock()`. `AuthorizerOp` mutates Ranger roles/policies; `CacheOp` mutates `CachedTenantState`.

Control flow: tenant changes are split between pre-execute authorizer work and validate-and-update-cache work. `AuthorizerOp` requires the `AuthorizerLock` write lock, creates/deletes tenant roles and policies, updates user/admin roles, and wraps Ranger I/O failures as `TENANT_AUTHORIZER_ERROR`. `CacheOp` uses a write lock to mirror successful DB mutations into `tenantCache`. Read paths use the tenant DB tables and cache to list users, resolve access IDs, and evaluate tenant admin status.

State and persistence: OM DB tables are the durable source (`tenantStateTable`, `tenantAccessIdTable`, `principalToAccessIdsTable`). `tenantCache` is rebuilt from those tables on startup, and stores tenant role names plus accessId to principal/admin flags. Ranger state is external and eventually reconciled by the background sync service.

Dependencies and integration points: depends on `OzoneManager`, `OMMetadataManager`, Ranger-oriented `MultiTenantAccessController`, `AuthorizerLock`, `CachedTenantState`, tenant helper DB objects, RPC remote user context, and `OMRangerBGSyncService`.

Risks: the code relies on correct lock ordering between authorizer, cache, and DB update phases; partial Ranger failures are intentionally repaired later, so tests must cover idempotency and background reconciliation. Cache rebuild throws runtime exceptions on inconsistent DB rows. `getUserNameGivenAccessId` logs and returns null on I/O, which can flow into admin-role updates if callers fail validation.

Test signals: useful coverage includes tenant create/delete idempotency, Ranger failure wrapping, cache rebuild from DB tables, accessId revocation, delegated versus non-delegated tenant admin checks, orphaned accessId metadata, and concurrent read/write lock behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMultiTenantManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMPerformanceMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMPerformanceMetrics.java

Purpose: `OMPerformanceMetrics` is the metrics2 source for Ozone Manager request latency and service-loop performance. It records nano-second request path rates and millisecond service gauges used by OM read/write paths, key operations, object tagging, cleanup services, and snapshot defrag.

Important APIs and types: `register()` registers a source named after the class with `DefaultMetricsSystem`; `unregister()` removes it. Fields are `MutableRate`, `MutableGaugeFloat`, and `MutableGaugeLong` annotated with `@Metric`. Public and package-private accessors expose mutable rate objects for scoped latency capture, while add/set methods record aggregate observations.

Control flow: callers either call direct add/set methods, such as `addLookupLatency`, `setListKeysOpsPerSec`, or `setSnapshotDefragServiceFullLatencyMs`, or retrieve a `MutableRate` and pass it to metric utilities. There is no persistence or internal branching beyond registration.

State and persistence: all state is in the metrics system and is process-local. Counters/rates reset on OM restart. No disk format or DB table is touched.

Dependencies and integration points: used by `OmMetadataReader`, `OmMetadataManagerImpl`, request submit/validation code, delete/open-key cleanup services, and snapshot defrag services. Depends only on Hadoop metrics2 mutable primitives.

Risks: metric method naming must match caller expectations; a likely maintenance trap is `addGetObjectTaggingLatencyNs` recording into the ACL-check metric instead of an overall object-tagging metric because no separate overall field exists. Package-private getters constrain use to the OM package.

Test signals: unit tests can register/unregister without duplicate sources, verify latency methods call the intended metric fields with fake metrics, and check service gauges accept last-iteration values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMPerformanceMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMPolicyProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMPolicyProvider.java

Purpose: `OMPolicyProvider` supplies Hadoop service authorization mappings for OM RPC protocols. It binds configured ACL keys to protocol interfaces used by client, admin, inter-service, and reconfiguration RPC endpoints.

Important APIs and types: `getInstance()` returns a memoized singleton via Ratis `MemoizedSupplier`. `getServices()` returns an array of `Service` records for `OzoneManagerProtocol`, `OMInterServiceProtocol`, `OMAdminProtocol`, and `ReconfigureProtocol`.

Control flow: there is no dynamic logic beyond singleton construction and array conversion. The service list is statically initialized and reused.

State and persistence: no persistent state. The effective authorization state lives in Hadoop configuration keys `OZONE_OM_SECURITY_CLIENT_PROTOCOL_ACL`, `OZONE_OM_SECURITY_ADMIN_PROTOCOL_ACL`, and `OZONE_SECURITY_RECONFIGURE_PROTOCOL_ACL`.

Dependencies and integration points: consumed by RPC server/security setup when Hadoop service-level authorization is enabled. It depends on Hadoop `PolicyProvider`, `Service`, and OM protocol classes.

Risks: missing a protocol here means service-level authorization may not be enforced for that endpoint. Mapping an endpoint to the wrong ACL key can over-grant or under-grant access. Since the class is private/unstable, changes should track protocol additions.

Test signals: authorization tests should assert the returned services include all exposed OM RPC protocols and that admin/inter-service protocols use admin ACLs while client protocol uses client ACLs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMPolicyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMStarterInterface.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMStarterInterface.java

Purpose: `OMStarterInterface` is a small dependency-injection seam for `OzoneManagerStarter`, allowing CLI code to invoke OM lifecycle commands without directly coupling to the concrete starter implementation.

Important APIs and types: it declares `start`, `init`, `bootstrap`, and `startAndCancelPrepare`. All methods accept `OzoneConfiguration`; `bootstrap` also accepts `force`. Methods throw `IOException` and `AuthenticationException`.

Control flow: none inside the interface. Implementations own startup, initialization, HA bootstrap, and start-with-prepare-cancel behavior.

State and persistence: no state. Implementations will affect OM storage, security login, and cluster metadata.

Dependencies and integration points: used by command-line bootstrapping and tests that inject alternate starters. Depends only on `OzoneConfiguration` and Hadoop authentication exception types.

Risks: lifecycle semantics are encoded only in method names and implementations. Tests should catch mismatches between CLI flags and invoked interface methods. Since exceptions are broad, callers need to present clear user-facing errors.

Test signals: CLI unit tests can mock this interface to verify `start`, `init`, forced bootstrap, and prepare-cancel flows are dispatched with the expected configuration and flags.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMStarterInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMStorage.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMStorage.java

Purpose: `OMStorage` models the OM `VERSION` file on top of common `Storage`. It records OM-specific identity fields: legacy OM UUID, HA node ID, and certificate serial ID, and resolves the OM metadata directory.

Important APIs and types: constructor initializes `Storage` for `NodeType.OM` under `OMConfigKeys.OZONE_OM_DB_DIRS`. Mutators include `setOmId`, `setOmNodeId`, `setOmCertSerialId`, `unsetOmCertSerialId`, and `validateOrPersistOmNodeId`. Accessors read the stored properties. `getNodeProperties()` supplies persisted properties and creates a UUID if needed. `getOmDbDir()` delegates to `ServerUtils.getDBPath`.

Control flow: identity fields cannot be changed after `StorageState.INITIALIZED` except cert serial handling. `validateOrPersistOmNodeId` requires initialized storage, compares the configured node ID to the VERSION file, and persists it when missing for older deployments.

State and persistence: fields are persisted in the VERSION file, not RocksDB. The node ID ties an OM process to its metadata directory and HA/Raft identity.

Dependencies and integration points: used during OM init/startup, upgrade layout version selection, SCM certificate handling, and OM DB location selection.

Risks: mismatched node IDs indicate potentially dangerous metadata reuse; the error text warns against manual VERSION edits and unsafe majority metadata removal. Tests must protect behavior for pre-existing VERSION files without nodeId.

Test signals: cover fresh init UUID generation, post-init mutation rejection for OM ID/node ID, cert serial persistence/unset, node ID mismatch failures, missing node ID migration, and fallback/required metadata directory resolution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetadataManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetadataManagerImpl.java

Purpose: `OmMetadataManagerImpl` is the concrete OM metadata facade over RocksDB. It opens OM or snapshot checkpoint DB stores, initializes all OM column-family tables, provides key-format helpers, list/expiration scans, S3 secret storage, table-prefix mapping, and lock access.

Important APIs and types: constructors cover live OM DB, checkpoint metadata managers, read-only checkpoint DBs, and snapshot DBs. Table getters expose user, volume, bucket, key/file, open key/file, multipart, deleted, prefix, transaction, tenant, snapshot, rename, and compaction-log tables. Utility APIs build DB keys for object-store and FSO layouts, list buckets/volumes/keys/snapshots/open files/MPUs, check emptiness, count rows, get expired open keys/MPUs, and batch S3 secret changes.

Control flow: `start()` validates the transient inconsistent DB marker, opens a DBStore via `DBStoreBuilder`, initializes tables with full cache for live OM or partial cache for checkpoints/snapshots, then creates `SnapshotChainManager`. Listing methods merge cache and persisted RocksDB views, skipping cache tombstones and preserving sorted pagination. Expiration methods scan open-key and multipart tables, special-casing hsync and MPU keys to avoid data loss.

State and persistence: all OM metadata tables are persistent RocksDB column families. Table caches represent unflushed updates. `tableMap` indexes opened tables by name; table cache metrics are registered for live tables. Locks protect OM resources but iterator snapshots are used for some read scans.

Dependencies and integration points: central dependency for `OzoneManager`, request handlers, `KeyManager`, `SnapshotUtils`, `SnapshotChainManager`, S3 secret APIs, tenant manager, delete services, and checkpoint/snapshot readers. It integrates with `OMDBDefinition`, `DBStoreBuilder`, `OzoneManagerLock`, hierarchical locks, performance metrics, and protobuf helper types.

Risks: DB key construction must remain compatible across bucket layouts and table definitions. Cache/DB merge logic is subtle around tombstones, pagination, and concurrent flushes. Expired open-key logic must not delete active hsync leases or orphan MPU state. Startup terminates when a DB transient marker exists.

Test signals: cover live versus checkpoint initialization, table presence, key encoding for legacy/OBS/FSO, list pagination with cache overrides and tombstones, bucket/volume emptiness, snapshot listing continuation, expired hsync/open-key cleanup, incomplete MPU detection, table bucket prefixes, S3 batcher behavior, and store close/unregister cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetadataManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetadataReader.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetadataReader.java

Purpose: `OmMetadataReader` implements `IOmMetadataReader` for live OM and snapshot-backed readers. It centralizes read-side bucket-link resolution, ACL checks, metrics, audit logging, and delegation to key/prefix/volume/bucket managers.

Important APIs and types: public read APIs include `lookupKey`, `getKeyInfo`, `listStatus`, `listStatusLight`, `getFileStatus`, `lookupFile`, `listKeys`, `listKeysLight`, `getAcl`, `getObjectTagging`, and ACL-check helpers. It implements `Auditor` with success/failure audit message builders.

Control flow: each operation resolves bucket links, updates arguments to real volume/bucket names, optionally checks ACLs, increments operation metrics, delegates to the relevant manager, logs audit success/failure, and records performance latency where configured. S3-authenticated requests map access IDs to principals for ACL checks. `getClientAddress()` handles both RPC and gRPC client-address contexts.

State and persistence: this class has no durable state. It reads from managers backed by OM metadata and emits process-local metrics/audit logs.

Dependencies and integration points: depends on `KeyManager`, `PrefixManager`, `VolumeManager`, `BucketManager`, `OzoneManager`, `IAccessAuthorizer`, audit classes, `OmMetadataReaderMetrics`, and `OMPerformanceMetrics`. `OmSnapshot` reuses it with snapshot-aware managers and authorizer.

Risks: ACL checks must use resolved bucket owners and correct resource type, especially for links and S3 contexts. Audit maps must represent original user inputs while operations use resolved names. A metric wiring issue appears in object tagging resolution using lookup resolve latency rather than the object-tagging resolve metric.

Test signals: cover successful and failed audit logging, ACL enabled/disabled behavior, S3 principal resolution, bucket-link resolution, list page-size limiting, object tagging failure metrics, gRPC client address fallback, and `throwIfPermissionDenied` behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetadataReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetadataReaderMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetadataReaderMetrics.java

Purpose: `OmMetadataReaderMetrics` defines the metrics contract consumed by `OmMetadataReader` without tying it to one concrete metrics implementation.

Important APIs and types: it declares increment methods for key lookup, get-key-info, list status, file status, lookup file, key listing, ACL read, and object tagging operations, with separate failure increments for most operation families.

Control flow: none in the interface. Implementations decide whether increments map to counters, rates, or no-op behavior.

State and persistence: no state. Implementations are process-local metrics sources.

Dependencies and integration points: implemented by live OM metrics and snapshot metrics; injected into `OmMetadataReader`. This lets `OmSnapshot` reuse the reader while reporting to snapshot-specific metrics.

Risks: the interface has asymmetric success/failure coverage: `getAcl` has only a success increment and no failure method. Adding new read APIs requires updating both this interface and all implementations, or reads will be invisible to metrics.

Test signals: compile-time implementation coverage is important. Reader tests should verify the expected increment method fires for each success and failure branch.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetadataReaderMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetricsInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetricsInfo.java

Purpose: `OmMetricsInfo` is a Jackson-serializable bean used to persist OM metrics seed data across restart. At present it stores only `numKeys`.

Important APIs and types: package-private default constructor initializes `numKeys` to zero. `getNumKeys()` and `setNumKeys(long)` expose the field. `@JsonProperty` on the private field supports JSON serialization/deserialization.

Control flow: no branching beyond construction.

State and persistence: the `numKeys` value is intended for a file persisted outside the OM RocksDB metadata path so OM metrics can be initialized on restart.

Dependencies and integration points: depends on Jackson annotations and is likely used by OM metrics save/load code. It intentionally stays simple to preserve file compatibility.

Risks: expanding this object changes the persisted metrics file contract. The constructor is package-private, so external serializers/tests must be in-package or use Jackson field access. No validation prevents negative values.

Test signals: serialization round-trip tests should verify default zero, non-zero values, compatibility with missing fields, and rejection or handling policy for invalid negative input if introduced.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetricsInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshot.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshot.java

Purpose: `OmSnapshot` implements `IOmMetadataReader` for one OM snapshot. It wraps a snapshot-backed `KeyManager` and `PrefixManager` with an `OmMetadataReader`, normalizing user-facing `.snapshot/<name>/...` paths into snapshot DB keys and denormalizing results back to snapshot-prefixed paths.

Important APIs and types: read APIs mirror `IOmMetadataReader`: key lookup, get key info, list status, file status, lookup file, list keys, lightweight list, ACL read, and object tagging. Snapshot identity APIs expose `getName()`, `getSnapshotID()`, `getMetadataManager()`, `getKeyManager()`, and `getSnapshotTableKey()`.

Control flow: requests pass through `normalizeOmKeyArgs`, `normalizeKeyName`, or `normalizeOzoneObj` before delegation. Results use `denormalizeOmKeyInfo`, `denormalizeOzoneFileStatus`, or `denormalizeKeyInfoWithVolumeContext`. Bucket status responses with null `keyInfo` receive a synthetic zero-replication `OmKeyInfo` to carry the snapshot-prefixed key name.

State and persistence: holds snapshot identity and references a snapshot checkpoint `OMMetadataManager`. `close()` closes the snapshot DB store; `finalize()` logs a warning if the DB handle was not closed.

Dependencies and integration points: created by snapshot management code to serve snapshot read requests. It integrates with `OzoneAuthorizerFactory.forSnapshot`, `OmSnapshotManager` path helpers, `SnapshotInfo`, snapshot metrics, and key metadata classes.

Risks: path normalization must preserve trailing slashes and only strip valid snapshot prefixes. `listKeysLight` ignores its passed volume/bucket and uses the instance bucket, which is intentional for snapshots but should be covered. `finalize()` is a last-resort warning, not resource management.

Test signals: cover `.snapshot/name` root normalization, nested key normalization with trailing slash, denormalized lookup/list/file-status results, bucket status synthetic key info, close behavior, ACL normalization, and snapshot table key construction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshotInternalMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshotInternalMetrics.java

Purpose: `OmSnapshotInternalMetrics` is a metrics2 source for internal snapshot maintenance operations, including purge, property updates, moving table keys, and snapshot defragmentation.

Important APIs and types: `create()` registers the metrics source, `unregister()` removes it. `MutableCounterLong` fields track operation and failure counts. Increment methods update purge/set-property/move-table-key counters and full/incremental defrag counters; getter methods expose counter values for tests and diagnostics.

Control flow: all methods are straightforward counter increments or reads. Some increment methods accept a `long count` for batched table-compaction or delta-file counts.

State and persistence: process-local metrics reset on restart. No DB or file persistence.

Dependencies and integration points: used by snapshot purge, snapshot property, move-table-key, and defrag services. Depends on Hadoop metrics2 annotations and `DefaultMetricsSystem`.

Risks: missing increments in maintenance services will make long-running snapshot work hard to diagnose. Counter-only metrics do not expose latency; latency is separately tracked in `OMPerformanceMetrics`.

Test signals: tests should register/unregister cleanly, assert each increment mutates only the intended counter, verify batch increments add exact counts, and ensure defrag success/failure/skipped paths are all instrumented.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshotInternalMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshotLocalData.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshotLocalData.java

Purpose: `OmSnapshotLocalData` is the in-memory and YAML-serializable model of per-snapshot local metadata used by snapshot SST filtering/defragmentation. It records snapshot identity, versioned SST file metadata, checksum, defrag state, previous snapshot linkage, purge transaction info, and RocksDB sequence number.

Important APIs and types: constructors create initial version `0` from RocksDB `LiveFileMetaData` or deep-copy an existing object. Getters/setters expose defrag flags, last defrag time, previous snapshot ID, transaction info, DB transaction sequence, version, and checksum. `addVersionSSTFileInfos` increments the version and stores a `VersionMeta`; `removeVersionSSTFileInfos` deletes a version. `VersionMeta` stores previous snapshot version and immutable `SstFileInfo` list and implements deep copy/equality.

Control flow: checksum computation sets a dummy 64-byte checksum, dumps the object through SnakeYAML, and computes SHA-256 of the dump. `LinkedHashMap` is used for deterministic version ordering and checksum stability.

State and persistence: persisted by YAML helpers, not RocksDB tables directly. The checksum protects serialized YAML content excluding its final checksum value.

Dependencies and integration points: used by snapshot local data YAML read/write code, snapshot defrag services, RocksDB live-file metadata, `TransactionInfo`, and checksum validation via `WithChecksum`.

Risks: deterministic serialization is required for stable checksums; changing field order, YAML representers, or map type can invalidate checksums. Copy constructor shares immutable/simple objects like UUID and `TransactionInfo`, which is acceptable if those remain immutable.

Test signals: cover checksum round trips, version ordering, add/remove version behavior, deep copy of `VersionMeta` and SST lists, default version zero creation, previous snapshot null handling, and equality/hashCode for `VersionMeta`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshotLocalData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshotLocalDataYaml.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshotLocalDataYaml.java

Purpose: `OmSnapshotLocalDataYaml` builds customized SnakeYAML instances for serializing and deserializing `OmSnapshotLocalData`, `VersionMeta`, and `SstFileInfo` with explicit tags and snapshot-local field names.

Important APIs and types: constants define YAML tags and `.yaml` extension. `OmSnapshotLocalDataRepresenter` tags supported classes, serializes `SstFileInfo`, `VersionMeta`, `TransactionInfo`, and UUID values, and omits null properties. `SnapshotLocalDataConstructor` registers tag constructors and type descriptions. `YamlFactory` is a Commons Pool factory that creates configured `Yaml` instances.

Control flow: serialization uses custom representers to emit stable block mappings for SST and version metadata. Deserialization constructs maps from tagged nodes, parses UUIDs and `TransactionInfo`, creates a baseline `OmSnapshotLocalData`, then overlays version, flags, timestamps, version map, and checksum. `lastDefragTime` is validated to be numeric when present.

State and persistence: no state except pooled YAML objects. It defines the on-disk YAML format for snapshot local data files and must remain compatible with checksum computation in `OmSnapshotLocalData`.

Dependencies and integration points: used by snapshot local data persistence and defrag code. Depends on SnakeYAML, Commons Pool, Ozone field-name constants, `SstFileInfo`, and `TransactionInfo`.

Risks: custom tag names and field constants form a durable file contract. Deserialization casts require YAML values to have expected types; malformed files can throw `ClassCastException`, `IllegalArgumentException`, or UUID parse errors. Changes to representer output can break checksum validation.

Test signals: cover YAML round trip with checksum, null optional fields, previous snapshot absent/present, numeric and invalid `lastDefragTime`, multiple version metadata entries, custom tag presence, pooled factory create/wrap behavior, and compatibility with older YAML missing newer optional flags.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmSnapshotLocalDataYaml.java -->
