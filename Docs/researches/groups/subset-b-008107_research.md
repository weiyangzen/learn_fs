# subset-b-008107 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestKeyManagerUnit.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestKeyManagerUnit.java

Purpose: Unit coverage for `KeyManagerImpl` behavior around multipart upload listing/parts, key lookup pipeline hydration, datanode failure refresh, and list-status SCM caching. The test boots an `OmTestManagers` instance with mocked SCM block/location protocols and a real OM metadata manager backed by a temp metadata directory.

Important APIs and types: `KeyManagerImpl`, `OzoneManagerProtocol`, `OMMetadataManager`, `OmMultipartInfo`, `OmMultipartKeyInfo`, `OmMultipartUploadList`, `OmMultipartUploadListParts`, `OmKeyArgs`, `OmKeyInfo`, `OmKeyLocationInfo`, `ResolvedBucket`, `OzoneFileStatus`, `StorageContainerLocationProtocol`, `ScmBlockLocationProtocol`, `Pipeline`, `ContainerWithPipeline`, and `OMRequestTestUtils`.

Control flow: setup creates an OM with mocked SCM clients, disables Ratis system exits, and resets mocks before each test. MPU tests create volumes/buckets through metadata helpers, initiate uploads through the write client, optionally insert cache tombstones or cache-only MPU rows, and call `keyManager.listMultipartUploads` or `listParts`. Key lookup tests seed key table entries with block IDs and verify SCM batch lookups only when needed or when forced. `lookupFile` starts with stale pipeline metadata and expects SCM replacement. `listStatus` inserts ten keys with containers, lists the bucket, and verifies a single SCM batch fetch is reused on the second call.

State and persistence: this test exercises real OM tables plus table cache entries. It explicitly adds `multipartInfoTable` cache entries, deletion-style cache values, volume/bucket/key table rows, and container-location cache state inside `KeyManagerImpl`/`ScmClient`. Creation times are compared against a per-test `startDate` to catch missing MPU timestamp propagation.

Dependencies and integration points: depends on OM request test utilities, current UGI owner names, `RatisReplicationConfig`, SCM pipeline/container APIs, and `OmTestManagers` wiring. It bridges metadata tables to service-level key-manager reads, so failures often indicate a contract drift between request handlers, metadata key formats, cache overlay semantics, and SCM location hydration.

Risks and edge cases: duplicate cache entries must collapse into correct MPU listing results; cache tombstones must hide deleted DB/cache uploads; prefix and marker pagination must preserve sorted ordering and truncation markers; backward-compatible MPU part listing must tolerate parts without eTags; stale or null pipelines must be refreshed without repeated SCM calls; list-status sorting and datanode pipeline population rely on SCM cache reuse.

Test signals: assertions cover zero-part MPU listing, five committed parts without eTags, MPU listing by bucket/prefix/cache/DB, 25-entry pagination with markers, SCM call counts for `getKeyInfo` and `listStatus`, pipeline replacement on DN failure, and stable result ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestKeyManagerUnit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMDBArchiver.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMDBArchiver.java

Purpose: Tests `OMDBArchiver`, the component that records files and emits OM DB checkpoint archives with hardlink metadata. It validates both individual hardlink recording and full tar archive generation.

Important APIs and types: `OMDBArchiver`, `recordFileEntry`, `recordHardLinkMapping`, `writeToArchive`, `OM_HARDLINK_FILE`, `OZONE_RATIS_SNAPSHOT_COMPLETE_FLAG_NAME`, Hadoop `FileUtil.unTar`, `IOUtils.getINode`, `OzoneConfiguration`, and temp filesystem paths.

Control flow: `testRecordFileEntry` creates a dummy file, asks the archiver to record it under a hardlink entry name, then checks that the stored file is a different path with the same inode. `testWriteToArchive` parameterizes completion state, adds ten files and hardlink mappings, writes the archive to an output stream, untars it, and verifies file content and optional completion marker files.

State and persistence: all behavior is filesystem-backed. The archiver maintains an in-memory map of tar entry names to files plus a temp directory. Completed archives persist an OM hardlink mapping file and a Ratis snapshot complete marker; incomplete archives contain only recorded files.

Dependencies and integration points: integrates with snapshot checkpoint transfer code that later consumes hardlink maps, with Hadoop tar utilities, and with filesystem inode semantics. It assumes the test filesystem supports hardlinks and stable inode comparison.

Risks and edge cases: hardlink creation may be platform-sensitive; archive completeness depends on writing marker files only after successful completion; hardlink mappings must be relative and extractable; tar output must not omit non-empty files.

Test signals: non-empty tar output, exact extracted file counts, byte-for-byte dummy content, inode equality for hardlinks, and marker presence only when `completed` is true.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMDBArchiver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMDBCheckpointServletInodeBasedXferNonLeader.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMDBCheckpointServletInodeBasedXferNonLeader.java

Purpose: Focused servlet tests for `OMDBCheckpointServletInodeBasedXfer` when the local OM is not leader-ready. It protects checkpoint download paths from serving snapshots from followers or unready leaders.

Important APIs and types: `OMDBCheckpointServletInodeBasedXfer`, `processMetadataSnapshotRequest`, `OzoneManager.isLeaderReady`, servlet context attribute `OzoneConsts.OM_CONTEXT_ATTRIBUTE`, `HttpServletRequest`, and `HttpServletResponse`.

Control flow: each test spies the servlet to inject a mocked `ServletContext`, returns a mocked OM with `isLeaderReady=false`, invokes `processMetadataSnapshotRequest`, and verifies response handling. One path checks normal `sendError(503, message)`; the other forces `sendError` to throw and verifies fallback `setStatus(503)`.

State and persistence: no durable state is created. The only state is the servlet context and response status/error side effect.

Dependencies and integration points: integrates with OM HTTP checkpoint transfer and servlet containers. It assumes the servlet obtains OM from context and performs leader gating before snapshot streaming.

Risks and edge cases: broken clients may cause `sendError` to throw; without fallback status setting the HTTP response could look successful. A regression could allow non-leaders to serve stale metadata snapshots.

Test signals: Mockito verifies exact service-unavailable response behavior and fallback status assignment.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMDBCheckpointServletInodeBasedXferNonLeader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMDBDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMDBDefinition.java

Purpose: Consistency test ensuring `OMDBDefinition` column-family definitions match the tables actually opened by `OmMetadataManagerImpl`.

Important APIs and types: `OMDBDefinition.get`, `DBColumnFamilyDefinition`, `OmMetadataManagerImpl.loadDB`, `DBStore.getTableNames`, `OmReadOnlyLock`, and `OzoneConfiguration`.

Control flow: the test collects defined column-family names from `OMDBDefinition`, opens a temporary OM DB store via metadata manager loading, removes RocksDB's default table, subtracts names in both directions, and asserts no missing entries plus equal counts.

State and persistence: creates a temporary RocksDB-backed OM DB and closes it with try-with-resources. The test validates schema metadata, not data rows.

Dependencies and integration points: guards the codec/definition layer used by tooling, checkpoint inspection, and metadata manager table initialization. It catches table additions that update only one side of the schema contract.

Risks and edge cases: the error messages appear label-swapped in spirit but still expose missing names. The test can fail on intentional table additions until both definitions and manager loading are synchronized.

Test signals: zero missing definition tables, zero missing OM DB tables, and equal counts between loaded RocksDB column families and `OMDBDefinition`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMDBDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMMetadataReader.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMMetadataReader.java

Purpose: Tests `OmMetadataReader.getClientAddress`, which chooses the client IP address for audit/security paths across gRPC and Hadoop RPC calls.

Important APIs and types: `OmMetadataReader`, static `io.grpc.Context.key("CLIENT_IP_ADDRESS")`, `Context.Key.get`, and static `org.apache.hadoop.ipc_.Server.getRemoteAddress`.

Control flow: the test uses Mockito static mocks for gRPC context and Hadoop RPC server state. It first returns a gRPC client IP, then a missing gRPC value, then a Hadoop RPC remote address, asserting the method prioritizes gRPC and falls back correctly.

State and persistence: no persistence. State is thread/context-local behavior simulated by static mocks.

Dependencies and integration points: integrates with OM request handling over gRPC and Hadoop RPC. The output is likely consumed by ACL/audit code that records request origin.

Risks and edge cases: static mocking can hide context key changes; returning empty string for missing gRPC address is an explicit contract. Fallback order matters if both transports expose values.

Test signals: expected gRPC IP, empty string for absent context value, and expected Hadoop RPC address after gRPC no longer yields one.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMMetadataReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMMultiTenantManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMMultiTenantManager.java

Purpose: Tests multi-tenancy feature gating and disabled-feature request rejection in `OMMultiTenantManager` and OM request dispatch.

Important APIs and types: `OMMultiTenantManager.checkAndEnableMultiTenancy`, `OzoneManager.checkS3MultiTenancyEnabled`, multi-tenancy OM request builders in `OMRequestTestUtils`, `OzoneManagerRatisUtils.createClientRequest`, `OzoneManagerRequestHandler.handleReadRequest`, `OMException.ResultCodes.FEATURE_NOT_ENABLED`, and Ranger/Kerberos OM config keys.

Control flow: `testMultiTenancyCheckConfig` builds an `OzoneConfiguration` incrementally and verifies the method fails until security, Kerberos or basic Ranger admin credentials, Ranger HTTPS address, and Ranger service are present. `testMultiTenancyRequestsWhenDisabled` mocks an OM with feature disabled, sends each multi-tenancy write request through Ratis request creation and each read request through the read handler, and expects feature-not-enabled results.

State and persistence: no OM DB persistence is used here. State is configuration and mocked OM security flags.

Dependencies and integration points: covers Ranger integration prerequisites, Hadoop security authentication settings, OM Ratis write request creation, and protobuf read request handling. It codifies backward compatibility by noting `getS3VolumeContext` falls back rather than failing when MT is disabled.

Risks and edge cases: configuration checker must not enable MT with partial Ranger credentials or missing security; write and read paths fail differently, via exception versus `OMResponse`. New multi-tenancy request types must be added to this test or may bypass the gate.

Test signals: runtime failures contain "Failed to meet", successful Kerberos/basic-auth configurations return true, write requests throw `OMException` with `FEATURE_NOT_ENABLED`, and read requests return unsuccessful protobuf responses with status `FEATURE_NOT_ENABLED`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMMultiTenantManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMMultiTenantManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMMultiTenantManagerImpl.java

Purpose: Tests `OMMultiTenantManagerImpl` cache behavior and tenant/user lookup APIs using a real `OmMetadataManagerImpl` and skip-Ranger mode.

Important APIs and types: `OMMultiTenantManagerImpl`, `CachedTenantState`, `OmDBTenantState`, `OmDBAccessIdInfo`, `TenantUserList`, `UserAccessIdInfo`, tenant/access-id tables, and cache operations `createTenant`, `assignUserToTenant`, `assignTenantAdmin`, and `revokeUserAccessId`.

Control flow: setup creates an OM metadata DB under a temp directory, seeds one tenant and one access ID directly in DB, mocks `OzoneManager`, and constructs the tenant manager. Tests add tenants and users through paired DB and cache operations, reconstruct the manager to verify cache reload, list users with/without prefix, revoke access IDs, and resolve tenant ID by access ID.

State and persistence: durable state is in tenant-state and tenant-access-id tables. In-memory state is `tenantCache`, which is rebuilt from those tables on manager construction and mutated through `getCacheOp`.

Dependencies and integration points: depends on multi-tenant helper naming conventions for default roles and bucket policies, OM metadata manager table layouts, Ranger sync interval config, and dev skip Ranger mode.

Risks and edge cases: cache reload must include tenants with no users and admin/delegated-admin flags; list prefix filtering must return empty lists without errors; revoking unknown access IDs must throw; revocation must keep tenant presence but remove user mapping.

Test signals: exact cache sizes and `CachedTenantState` equality, user/access-id pairs in `TenantUserList`, specific "Tenant 'tenant2' not found!" IOException, empty cache map after revocation, and `Optional` tenant lookup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMMultiTenantManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMStorage.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMStorage.java

Purpose: Tests OM storage directory resolution and VERSION-file-backed OM identity fields.

Important APIs and types: `OMStorage`, `OMStorage.getOmDbDir`, `setOmId`, `setOmNodeId`, `validateOrPersistOmNodeId`, `setOmCertSerialId`, `unsetOmCertSerialId`, `getNodeProperties`, storage state `INITIALIZED`, `OMLayoutVersionManager`, `OZONE_OM_DB_DIRS`, and `OZONE_METADATA_DIRS`.

Control flow: directory tests set OM DB and metadata dirs and verify primary/fallback behavior and missing-config failure. Identity tests create `OMStorage` before or after persisted initialization, attempt setters, persist current state, reload storage, and validate node ID rules. Certificate serial tests run both before and after initialization.

State and persistence: the test writes and reloads OM VERSION state in the temp OM DB dir. Persisted properties include cluster ID, layout version, OM ID, OM node ID, and cert serial ID.

Dependencies and integration points: storage initialization is a prerequisite for OM startup, HA node identity validation, upgrade layout versioning, and certificate tracking. Directory resolution integrates HDDS and OM-specific metadata config.

Risks and edge cases: `OM_ID` and `OM_NODE_ID` are immutable after initialization except `validateOrPersistOmNodeId` may fill a missing node ID; mismatched node IDs must fail with the formatted error; cert serial ID intentionally remains mutable. Directory fallback can accidentally create the wrong path if config precedence regresses.

Test signals: exact directory existence checks, exact error messages for initialized setters and unexpected node ID, properties map contents, reload persistence of newly written node ID, and null cert serial after unset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOMStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmMetadataManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmMetadataManager.java

Purpose: Broad unit coverage for `OmMetadataManagerImpl`: table schema coverage, volume/bucket/key listing with cache overlays and pagination, open-file listing, expired open key and MPU discovery, snapshot listing, and multipart upload key listing.

Important APIs and types: `OMMetadataManager`, `OmMetadataManagerImpl`, `OMDBDefinition`, all core table constants, `OmVolumeArgs`, `OmBucketInfo`, `OmKeyInfo`, `OmMultipartKeyInfo`, `OpenKeySession`, `ListOpenFilesResult`, `SnapshotInfo`, `ListSnapshotResponse`, `BucketLayout`, `CacheKey`, `CacheValue`, `TransactionInfo`, and `OMRequestTestUtils`.

Control flow: setup creates a temp RocksDB metadata manager. Tests seed rows either through DB helpers or direct table cache entries, then call listing APIs with prefixes, start markers, and limits. Volume and bucket tests validate sorted traversal. Key tests cover pure cache, cache+DB, delete markers, and pagination. Parameterized open-key tests cover default and FSO layouts. Expiration tests create old open keys or MPUs based on configured thresholds and verify limit behavior. Snapshot tests seed snapshots across prefixes and buckets and validate path checks. Multipart upload key tests interleave table and cache rows and check marker behavior.

State and persistence: this file exercises both persisted RocksDB tables and unflushed table caches. It writes transaction info, volumes/users, buckets, keys, open keys/open files, multipart info and parts, snapshot info, and table definitions. Cache deletion entries are used to ensure in-memory tombstones override DB rows.

Dependencies and integration points: integrates OM metadata naming conventions for DB keys, bucket layouts, snapshot chain/listing expectations, cleanup-service selectors for expired open keys/MPUs, and generated table definitions. It is a high-signal contract for Recon, cleanup services, S3 MPU flows, and client list APIs.

Risks and edge cases: prefix/start marker arithmetic is easy to break because cache and DB iterators must merge without duplicates; deleted cache entries must hide persisted keys; expired open key logic must exclude MPU-related entries even when legacy `isMultipartKey` flags are false; MPU expiration limits are by part count and round to whole uploads; snapshot listing must not leak snapshots from other buckets; `getMultipartUploadKeys` uses `maxUploads + 1` sentinel behavior unless no-pagination is requested.

Test signals: exact counts for list volumes/buckets/keys/snapshots, equality with `TreeSet`/`TreeMap` expected ordering, exception result codes for missing volume/bucket snapshot paths, complete table-name equality with `OMDBDefinition`, expired item name containment, and all-MPU key listing across mixed cache/DB rows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmMetadataManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmMetadataManagerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmMetadataManagerMetrics.java

Purpose: Regression tests for table-cache metrics registration conflicts when OM metadata tables are repeatedly initialized, especially during Recon-style synchronization.

Important APIs and types: `OmMetadataManagerImpl`, `TableCacheMetrics`, `Table`, `TableCache`, `CacheStats`, `DefaultMetricsSystem`, `MetricsSystem`, and `MetricsException`.

Control flow: setup creates a temp metadata manager; cleanup stops it and shuts down the metrics system. Tests repeatedly fetch the same table, fetch multiple tables, concurrently fetch tables from ten threads, manually unregister/reregister `TableCacheMetrics`, and simulate Recon reinitialization loops.

State and persistence: RocksDB table state is only indirectly involved. The primary state under test is Hadoop metrics source registration in `DefaultMetricsSystem` and table cache metrics lifecycle.

Dependencies and integration points: targets the table initializer path used by OM and Recon. It depends on metrics source naming convention `<tableName>Cache` and `TableCacheMetrics.create/unregister`.

Risks and edge cases: the helper `getRegisteredMetrics` is a weak proxy because it returns the metrics system rather than inspecting a source registry, so these tests mostly catch thrown exceptions rather than proving exact source identity. Concurrent reinitialization must not surface "already exists" metrics exceptions.

Test signals: no `MetricsException` during repeated/concurrent table access, non-null table and metrics handles, successful unregister/reregister for same source name, and a non-null metrics system after conflict resolution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmMetadataManagerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmSnapshotLocalDataYaml.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmSnapshotLocalDataYaml.java

Purpose: Tests YAML serialization/deserialization for `OmSnapshotLocalData`, including checksum handling, version/SST metadata, transaction info, and backward-compatible missing fields.

Important APIs and types: `OmSnapshotLocalData`, `OmSnapshotLocalDataYaml.YamlFactory`, `YamlSerializer`, `ObjectSerializer`, `VersionMeta`, `SstFileInfo`, `LiveFileMetaData`, `TransactionInfo`, SnakeYAML `Yaml`, and `OzoneConsts` snapshot-local-data field constants.

Control flow: a shared serializer is created in `BeforeAll`. Helper `writeToYaml` builds snapshot local data from mocked RocksDB live-file metadata, sets version, flags, previous snapshot ID, transaction info, defrag time, needs-defrag flag, and defragged SST version entries, then saves YAML. Tests load and compare the object graph, update and resave data, validate empty-file failure, verify checksum, check field names in raw YAML, and mutate YAML to simulate legacy missing/empty `lastDefragTime`.

State and persistence: writes real YAML files under a test root and deletes them after each test. The serialized state includes snapshot UUIDs, previous snapshot UUID, DB sequence number, transaction info, checksum, SST filtered/defrag flags, last defrag time, and versioned SST file lists.

Dependencies and integration points: integrates with snapshot local data management and RocksDB SST metadata filtering. The exact YAML keys are a compatibility surface for persisted snapshot sidecar files.

Risks and edge cases: version numbering changes during serialization (`42` becomes expected current versions `43/44` in the metadata map); checksum computation must ignore its own checksum field; legacy YAML without last-defrag-time must still load; empty YAML must fail loudly.

Test signals: exact `VersionMeta` map equality, checksum presence and verification, raw YAML containing all current constants, updated flags and transaction info after save/load, IOException message for empty file, and default `lastDefragTime=0` for missing or empty legacy values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmSnapshotLocalDataYaml.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmSnapshotManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmSnapshotManager.java

Purpose: Unit coverage for `OmSnapshotManager` snapshot gating, cache eviction, snapshot limit enforcement, hardlink restoration, checkpoint archive file classification, snapshot path construction, and idempotent checkpoint creation.

Important APIs and types: `OmSnapshotManager`, `OmSnapshot`, `SnapshotChainManager`, `OmSnapshotLocalDataManager`, `SnapshotInfo`, `RDBStore`, `DBStore`, `RDBBatchOperation`, `InodeMetadataRocksDBCheckpoint`, `OmSnapshotUtils.createHardLinkList`, `OMDBCheckpointServlet.processFile`, `OM_HARDLINK_FILE`, snapshot/checkpoint directory constants, `TypedTable`, and `HddsWhiteboxTestUtils`.

Control flow: setup starts an OM with filesystem snapshots enabled, cache size one, RocksDB snapshot metrics disabled, and max FS snapshots two. Cleanup removes snapshots from chain/table and YAML sidecars. Tests replace metadata tables with mocks where needed, create snapshot infos and checkpoints, fetch active snapshots to trigger eviction, set up leader/follower directory trees for hardlink restoration, call `processFile` with and without destination dirs, check static path construction, and create the same checkpoint twice to validate idempotent logging.

State and persistence: uses real temporary OM DB, snapshot checkpoint directories, candidate directories, SST-like files, hardlinks, snapshot chain state, and local YAML path cleanup. Some tests mutate metadata manager internals to mocked tables.

Dependencies and integration points: covers OM snapshot cache lifecycle, RocksDB checkpoint creation, metadata table lookup for volume/bucket/snapshot info, checkpoint servlet archive generation, follower checkpoint extraction, HA hardlink preservation, and snapshot count limits.

Risks and edge cases: cache eviction must close DB stores; disabling snapshots is unsafe when snapshot table is non-empty; snapshot limit uses both chain state and in-flight count; follower hardlink remapping must account for leader/follower directory layout differences; `processFile` must classify copied files, hardlink candidates, exclusions, and non-SST files correctly; repeated checkpoint creation should not fail.

Test signals: boolean safety-check results, mocked DBStore `close` on eviction, log message for skipped RocksDB metrics registration, `TOO_MANY_SNAPSHOTS` exception, inode equality after hardlink restoration, exact process-file map sizes and byte counts, deterministic snapshot paths with version suffixes, and idempotent log message on duplicate checkpoint creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmSnapshotManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmSnapshotManagerConfig.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmSnapshotManagerConfig.java

Purpose: Parameterized validation of snapshot RocksDB max-open-files configuration.

Important APIs and types: `OMConfigKeys.OZONE_OM_SNAPSHOT_DB_MAX_OPEN_FILES`, `OmTestManagers`, `OzoneConfiguration`, snapshot feature enablement, and JUnit parallel execution.

Control flow: for each configured value, the test creates a temp metadata dir, enables filesystem snapshots, sets all OM bind ports to dynamic values to allow concurrent execution, then either expects `OmTestManagers` construction to throw or starts and stops the managers.

State and persistence: starts a real lightweight OM test manager for valid values, writing temp metadata state. Invalid values fail before usable manager state is created.

Dependencies and integration points: integrates startup-time config validation for snapshot DB options and OM service port binding.

Risks and edge cases: only values less than `-1` are invalid; `-1`, `0`, and positive values are accepted. Parallel execution makes dynamic ports necessary to avoid flaky bind conflicts.

Test signals: `-2` throws `IllegalArgumentException`; `-1`, `0`, and `1` construct without throwing and are stopped cleanly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmSnapshotManagerConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneConfigUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneConfigUtil.java

Purpose: Tests server-side replication configuration preference resolution.

Important APIs and types: `OzoneConfigUtil.resolveReplicationConfigPreference`, `ReplicationConfig`, `RatisReplicationConfig`, `ECReplicationConfig`, `DefaultReplicationConfig`, `HddsProtos.ReplicationType`, and `HddsProtos.ReplicationFactor`.

Control flow: setup mocks `OzoneManager.getDefaultReplicationConfig` to return RATIS/THREE. Tests call preference resolution with no client preference plus EC bucket default, no bucket default, explicit client EC preference, and RATIS bucket default.

State and persistence: no persistence. State is pure config values and mocked default replication config.

Dependencies and integration points: covers OM key creation config resolution where client, bucket, and server defaults compete.

Risks and edge cases: `ReplicationType.NONE` and `ReplicationFactor.ZERO` mean no client preference; EC proto config must be honored when type is EC; bucket defaults should override server defaults but not explicit client preference.

Test signals: exact object equality to bucket EC config, server RATIS default, client EC config `rs-3-2-1024K`, and RATIS bucket default.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneConfigUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHttpServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHttpServer.java

Purpose: Tests OM HTTP/HTTPS server startup policy and Jetty temp directory placement.

Important APIs and types: `OzoneManagerHttpServer`, `HttpConfig.Policy`, `URLConnectionFactory`, `KeyStoreTestUtil`, `BaseHttpServer.SERVER_DIR`, `DefaultMetricsSystem`, OM HTTP/HTTPS address and bind config keys, and `/jmx` endpoint probing.

Control flow: `BeforeAll` creates metadata and SSL config directories, generates test keystores, configures HTTP/HTTPS bind addresses on localhost dynamic ports, and builds a URL connection factory. The policy test starts the server for HTTP-only, HTTPS-only, and both, then probes HTTP/HTTPS URLs according to enabled schemes. The Jetty test starts the server and asserts the webserver dir is under the Ozone metadata directory.

State and persistence: writes temp keystore resources and metadata/webserver directories. Server start binds local network sockets and registers metrics.

Dependencies and integration points: integrates OM HTTP server config, Hadoop SSL test infrastructure, metrics system initialization, and client URL connection behavior.

Risks and edge cases: network probing can be environment-sensitive; incorrect address/scheme handling could expose or hide endpoints contrary to policy; Jetty temp dir must not default outside configured metadata dir.

Test signals: successful `/jmx` access only when policy enables the scheme, failed access for disabled schemes, webserver directory existence, and exact `getJettyBaseTmpDir` value.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListMultipartUploadsAcls.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListMultipartUploadsAcls.java

Purpose: Unit tests ACL enforcement and metrics around `OzoneManager.listMultipartUploads`.

Important APIs and types: `OzoneManager`, `OmMetadataReader.checkAcls`, `KeyManager.listMultipartUploads`, `OMMetrics`, `ResolvedBucket`, S3 authentication thread-local state, `OzoneObj.ResourceType.BUCKET`, ACL types `READ` and `LIST`, and `OMException.PERMISSION_DENIED`.

Control flow: setup starts a real OM via `OmTestManagers`; each test spies it, injects mocked metadata reader/key manager/metrics through whitebox state, resolves requested bucket names to real linked bucket names, and installs audit-message mocks. Tests cover ACL-disabled bypass, ACL-enabled read-then-list ordering, READ denial, and LIST denial.

State and persistence: no key metadata is persisted for the tested call; state is the spied OM internals, S3 auth context, and metrics side effects. `AfterEach` clears S3 auth.

Dependencies and integration points: covers link-bucket resolution, S3 request context, ACL manager integration, key manager delegation, audit message construction, and operation/failure metric counters.

Risks and edge cases: ACLs must use resolved real volume/bucket names, not requested symlink names; key manager must not be called after any ACL denial; read permission must be checked before list permission; failure metrics must increment exactly on exceptions.

Test signals: Mockito verifies no ACL calls when disabled, ordered READ then LIST ACL checks when enabled, key-manager argument values with real bucket names, success/failure metric increments, and no key-manager delegation on denied access.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListMultipartUploadsAcls.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListPartsAcls.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListPartsAcls.java

Purpose: Unit tests ACL enforcement and metrics around `OzoneManager.listParts` for multipart upload part listing.

Important APIs and types: `OzoneManager.listParts`, `OmMetadataReader.checkAcls`, `KeyManager.listParts`, `OMMetrics`, `ResolvedBucket`, S3 authentication context, `OzoneObj.ResourceType.BUCKET`, `OzoneObj.ResourceType.KEY`, ACL `READ`, and `OmMultipartUploadListParts`.

Control flow: setup mirrors the multipart-upload listing ACL test: a real OM is spied, metadata reader/key manager/metrics are mocked, bucket links resolve requested to real names, and audit messages are mocked. Tests cover ACL-disabled path, ACL-enabled bucket-read then key-read order, bucket-read denial, and key-read denial.

State and persistence: no real metadata rows are needed. State is mock/spy side effects and per-test S3 auth cleared in `AfterEach`.

Dependencies and integration points: validates that object-level part listing checks both bucket and key READ ACLs after bucket-link resolution, delegates to key manager only after both pass, and records metrics/audit failures.

Risks and edge cases: failing bucket READ must skip key READ; failing key READ must skip key manager; success and failure metrics are distinct; audit failure construction should happen on denied requests.

Test signals: ordered ACL verifications, exact key-manager arguments, success/failure metric calls, `OMException` propagation, and absence of downstream calls after ACL denial.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListPartsAcls.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerStarter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerStarter.java

Purpose: Tests the Picocli-backed `OzoneManagerStarter` command dispatch for start, init, upgrade/cancel-prepare, error handling, and usage output.

Important APIs and types: `OzoneManagerStarter`, `OMStarterInterface`, `GenericCli.EXECUTION_ERROR_EXIT_CODE`, Picocli exit codes `OK` and `USAGE`, `OzoneConfiguration`, and `AuthenticationException`.

Control flow: each test captures stdout/stderr, installs a `MockOMStarter`, executes command-line args, and checks the exit code plus method flags. The mock can throw on start/init/upgrade or return false from init. Invalid-option tests assert no action method ran and stderr starts with unknown-option usage text.

State and persistence: no persistent state. It temporarily replaces `System.out` and `System.err` and restores them after each test.

Dependencies and integration points: verifies CLI-to-service dispatch used by OM process startup. Bootstrap is implemented in the mock but not tested here.

Risks and edge cases: invalid options must not call service methods; failed init returning false must map to execution error; upgrade flag should call `startAndCancelPrepare`; stderr encoding must be stable for regex matching.

Test signals: exact exit codes, boolean flags on the mock starter, simulated exception paths, and regex match for usage text on invalid input.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerStarter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestScmClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestScmClient.java

Purpose: Tests `ScmClient` container-location and datanode-details caching behavior.

Important APIs and types: `ScmClient`, `StorageContainerLocationProtocol.getContainerWithPipelineBatch`, `ScmBlockLocationProtocol`, Guava `Cache<DatanodeID,DatanodeDetails>`, `ContainerWithPipeline`, `ContainerInfo`, `Pipeline`, `DatanodeDetails`, and `DatanodeID`.

Control flow: setup constructs `ScmClient` with mocked SCM protocols. Parameterized tests prepopulate cache with one SCM batch call, then request different ID sets with or without force refresh and verify only expected container IDs are fetched. Failure tests make SCM throw checked and unchecked exceptions. Datanode cache tests check stats and IP-address updates replacing cached node details.

State and persistence: all state is in-memory cache state inside `ScmClient` and Guava datanode detail caches. No filesystem or RocksDB use.

Dependencies and integration points: used by key lookup/list APIs to attach live pipelines to OM block locations while avoiding repeated SCM calls. Datanode detail cache preserves object identity unless updated node data arrives.

Risks and edge cases: force refresh must bypass cache for requested IDs; unchecked SCM errors are wrapped, while IOExceptions propagate; datanode IP changes must update cached node objects so stale addresses do not persist in refreshed pipelines.

Test signals: exact SCM batch call sets and counts, returned pipelines equal expected container pipelines, exception identity/cause assertions, cache miss stat count, and `assertSame`/IP checks for datanode replacement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestScmClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestServiceInfoProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestServiceInfoProvider.java

Purpose: Tests `ServiceInfoProvider`, which returns service list and CA certificate information to clients in secure and unsecure configurations.

Important APIs and types: `ServiceInfoProvider`, `ServiceInfoEx`, `OzoneManagerProtocol.getServiceList`, `SecurityConfig`, `CertificateClient`, `getAllRootCaCerts`, `registerRootCARotationListener`, certificate PEM encoding, and root CA rotation callback functions.

Control flow: base setup mocks OM service list as an empty list. In unsecure mode, provider returns no CA data. In secure mode, setup creates two self-signed certs, mocks all root certs, and constructs the provider. Tests call `provide` before and after a simulated root CA rotation listener callback with a newer cert list.

State and persistence: no files are persisted. Provider caches/currently tracks PEM root cert list and current CA certificate in memory. The cert client listener updates that state asynchronously via a returned completed future.

Dependencies and integration points: clients rely on this response to trust OM/SCM service endpoints. The provider bridges OM protocol service discovery, security config, and certificate rotation.

Risks and edge cases: unsecure mode must not expose CA fields; secure mode must choose the latest/active CA consistently; root CA rotation must update both single CA certificate and PEM list without recreating the provider.

Test signals: service list identity, null/empty CA fields in unsecure mode, PEM membership for root list, expected current PEM before and after rotation, and listener registration capture.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestServiceInfoProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestSnapshotListJSONServlet.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestSnapshotListJSONServlet.java

Purpose: Tests Jackson serialization for snapshot-list servlet output using `SnapshotListJSONServlet.SnapshotInfoMixin`.

Important APIs and types: `SnapshotListJSONServlet.SnapshotInfoMixin`, `SnapshotInfo`, Jackson `ObjectMapper`, `SnapshotInfo.newInstance`, and `Time.now`.

Control flow: the test registers the mixin on an object mapper, creates one snapshot info object, serializes a singleton list, and checks that problematic internal fields are excluded while the snapshot name is included.

State and persistence: no persistence; serialization happens in memory.

Dependencies and integration points: protects JSON servlet output from leaking protobuf or transaction internals that are not intended for HTTP clients and may be hard to serialize.

Risks and edge cases: changes to `SnapshotInfo` fields or mixin annotations can reintroduce unwanted fields or omit expected public fields.

Test signals: serialization does not throw, JSON lacks `protobuf`, `createTransactionInfo`, and `lastTransactionInfo`, and includes `"name":"snap1"`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestSnapshotListJSONServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/failover/TestOMFailovers.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/failover/TestOMFailovers.java

Purpose: Tests OM failover retry behavior for `AccessControlException` through Hadoop RPC retry proxies.

Important APIs and types: `RetryProxy`, `HadoopRpcOMFailoverProxyProvider`, `OMFailoverProxyProviderBase`, `OMProxyInfo`, `OzoneManagerProtocolPB`, protobuf `OMResponse`, `ServiceException`, `AccessControlException`, and `GenericTestUtils.LogCapturer`.

Control flow: the test configures a mock failover provider with three OM proxy infos and proxies that always throw `ServiceException` wrapping the selected exception. It creates a retry proxy with default max attempts, calls `submitRequest`, expects a `ServiceException`, and checks debug logs mention all three OM node IDs.

State and persistence: no persistent state. Runtime state is failover proxy provider list, the selected test exception, and captured logs.

Dependencies and integration points: exercises client-side HA failover policy, proxy creation, node ordering, and logging behavior for permission-denied responses.

Risks and edge cases: Access-control failures might be treated as non-retryable or failoverable depending policy; this test asserts the current behavior tries every OM before surfacing the last access-control cause. Log-message format is part of the test signal and can be brittle.

Test signals: thrown `ServiceException` has `AccessControlException` cause and expected message prefix; captured logs contain retry debug lines for `om1`, `om2`, and `om3`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/failover/TestOMFailovers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ha/TestOMHAMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ha/TestOMHAMetrics.java

Purpose: Tests leader-state gauge behavior in `OMHAMetrics`.

Important APIs and types: `OMHAMetrics.create`, `getMetrics`, `getOmhaInfoOzoneManagerHALeaderState`, `MetricsCollectorImpl`, and metrics unregister lifecycle.

Control flow: one test creates metrics with local node equal to leader ID and expects leader state `1`; another creates metrics with a different leader ID and expects `0`. `AfterEach` unregisters static metrics state.

State and persistence: metrics are in-memory Hadoop metrics sources. No durable state.

Dependencies and integration points: OM HA metrics are consumed by monitoring systems to distinguish leader and follower nodes.

Risks and edge cases: static metrics registration can leak between tests without unregister; leader-state comparison depends on exact node ID strings.

Test signals: metric value `1` for leader, `0` for follower, after invoking `getMetrics`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ha/TestOMHAMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ha/TestOMServiceManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ha/TestOMServiceManager.java

Purpose: Tests `OMServiceManager` notification flow for services that should run only when OM is leader.

Important APIs and types: `OMServiceManager`, `OMService`, `ServiceStatus`, and `OMServiceException`.

Control flow: the test defines a small context with a mutable leader boolean and an anonymous `OMService` whose `notifyStatusChanged` sets status to RUNNING or PAUSING from that boolean. It registers the service, toggles leader state, calls `notifyStatusChanged`, and checks `shouldRun`.

State and persistence: all state is in-memory service status. No persistence.

Dependencies and integration points: OM background services use this manager to react to HA role transitions.

Risks and edge cases: services must begin paused, transition to running on leadership, and pause again after step-down. Missing notification would leave services running on followers.

Test signals: `shouldRun` is false initially, true after becoming leader, and false after stepping down.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ha/TestOMServiceManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestKeyPathLock.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestKeyPathLock.java

Purpose: Tests `OzoneManagerLock.LeveledResource.KEY_PATH_LOCK` concurrency and lock-level ordering constraints.

Important APIs and types: `OzoneManagerLock`, `LeveledResource.KEY_PATH_LOCK`, `LeveledResource.BUCKET_LOCK`, read/write lock acquisition and release, current-lock tracking, `CountDownLatch`, and `GenericTestUtils.waitFor`.

Control flow: `testKeyPathLockMultiThreading` runs same-key and different-key write-lock scenarios. Same-key threads all contend on one key path, increment a shared counter while locked, and record sequential tokens. Different-key threads lock unique keys under one bucket and wait until all have acquired/released enough to show independent locking. Four additional tests acquire key-path read/write locks and assert acquiring higher-level bucket read/write locks is rejected.

State and persistence: all state is in-memory lock maps, per-thread lock tracking, and a shared counter. No persistence.

Dependencies and integration points: protects OM file/key operations that lock path-level resources and enforce hierarchical lock ordering to avoid deadlocks.

Risks and edge cases: same key path must serialize writers; distinct key paths should not block each other globally; lock hierarchy must prevent acquiring a higher-level bucket lock while holding a lower-level key-path lock, for both read and write modes. Thread sleeps and waits can be timing-sensitive.

Test signals: final counter equals `threadCount * iterations`, sequential token list proves same-key serialization, current-lock size is one per different-key thread, latch completion reaches zero, and hierarchy violations throw with a message naming the held key-path lock.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestKeyPathLock.java -->
