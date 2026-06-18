# subset-b-008086 Research

Generated for work item `subset-b-008086`. Each section preserves the original source path and is delimited for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerPrepare.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerPrepare.java

## Purpose
Integration coverage for HA Ozone Manager prepare/cancel behavior against a real `MiniOzoneHAClusterImpl`. The test verifies that preparing an OM Ratis group blocks mutating OM requests, preserves already committed metadata, purges Ratis log files, survives restarts, and allows lagging peers to catch up to the prepare transaction.

## Important APIs and Types
Primary test type: `TestOzoneManagerPrepare`, extending `TestOzoneManagerHA`. Important helpers include `submitPrepareRequest`, `submitCancelPrepareRequest`, `assertClusterPrepared`, `assertClusterNotPrepared`, `assertRatisLogsCleared`, `writeKeysAndWaitForLogs`, `assertKeysWritten`, and `logFilesPresentInRatisPeer`. It uses `ClientProtocol`, `OzoneManagerPrepareState.State`, `PrepareStatus`, `OMMetadataManager`, `OmKeyInfo`, `MiniOzoneHAClusterImpl`, Ratis `RaftServer.Division`, and `OMException.ResultCodes.NOT_SUPPORTED_OPERATION_WHEN_PREPARED`.

## Control Flow
`@BeforeEach` waits for an OM leader, cancels any inherited prepare state, and asserts the cluster is writable. Test methods then issue writes, shutdown/restart OMs, submit prepare through `clientProtocol.getOzoneManagerClient().prepareOzoneManager`, and poll every OM until its prepare status reaches `PREPARE_COMPLETED` at or beyond the returned log index. Read requests are expected to continue, while write requests are expected to fail once prepared. `testPrepareWithMultipleThreads` races one prepare request against volume creation tasks and accepts either successful pre-prepare writes or explicit prepared-state failures.

## State and Persistence
The important persistent state is OM metadata in RocksDB and OM Ratis logs on disk. `writeKeysAndWaitForLogs` forces data writes and waits until each target OM has Ratis log files, making later log purge assertions meaningful. `assertKeysWritten` reads each OM's local metadata manager rather than only the client-visible majority, so it detects follower data loss. Prepare state must persist through full OM restart and be catch-up replicated to a previously downed OM.

## Dependencies and Integration Points
The test couples OM client RPC, HA Ratis replication, OM prepare state, metadata tables, mini-cluster lifecycle, and filesystem-level Ratis storage directories. It also uses `TestDataUtil` and `ContainerTestHelper` to create object-store keys.

## Risks and Edge Cases
The test is marked flaky for HDDS-5990 and one downed-OM case is unhealthy pending Ratis behavior. Assertions depend on log file naming and storage layout under Ratis directories. Timing is intentionally long because lagging followers and log purge are asynchronous. Concurrent prepare/write outcomes are nondeterministic but constrained by result code checks.

## Test Signals
Strong signals include prepare index propagation to all OMs, Ratis logs disappearing after prepare, reads succeeding while writes fail in prepared state, cancel restoring writes, two-down-OM quorum failure, one-down-OM catch-up, prepare persistence across restart, and repeated prepare idempotence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerPrepare.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerRestInterface.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerRestInterface.java

## Purpose
Abstract non-HA integration test for the Ozone Manager HTTP `/serviceList` endpoint. It validates that OM exposes discoverable service metadata for OM and SCM through its embedded HTTP server.

## Important APIs and Types
The file defines `TestOzoneManagerRestInterface`, implementing `NonHATests.TestCase`. Important members are `setup` and `testGetServiceList`. It uses `OzoneManagerHttpServer`, Apache `HttpClient`/`HttpGet`, Jackson `ObjectMapper`, `ServiceInfo`, `HddsProtos.NodeType`, `ServicePort.Type`, `OmUtils.getOmRpcAddress`, and `HddsUtils.getScmAddressForClients`.

## Control Flow
`@BeforeAll` caches the provided mini-cluster and configuration. The test builds an HTTP URL from the OM HTTP server address, performs `GET /serviceList`, parses the JSON response as `List<ServiceInfo>`, maps entries by node type, and compares returned host/port values with the configuration and live HTTP server address.

## State and Persistence
There is no local persistence. The endpoint reflects runtime service registration state from the running mini-cluster. The test reads configuration-derived OM and SCM addresses and HTTP/RPC ports from the response.

## Dependencies and Integration Points
This is an integration boundary between OM's HTTP server, JSON serialization of service discovery data, client-side service metadata types, and SCM address configuration.

## Risks and Edge Cases
The test assumes exactly one relevant SCM client address is available from the iterator and that host-name formatting matches `ServiceInfo`. It does not assert HTTP status before parsing, nor does it validate optional service entries beyond OM and SCM.

## Test Signals
Passing indicates `/serviceList` produces valid JSON consumable as `ServiceInfo`, includes OM and SCM entries, and advertises correct OM RPC/HTTP and SCM RPC addresses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerRestInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerRestart.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerRestart.java

## Purpose
Mini-cluster restart integration tests for core OM metadata operations. It checks that volume, bucket, and key/rename state survives OM and SCM restarts and that duplicate operations still return the expected OM error codes after restart.

## Important APIs and Types
Main class: `TestOzoneManagerRestart`. Important tests are `testRestartOMWithVolumeOperation`, `testRestartOMWithBucketOperation`, and `testRestartOMWithKeyOperation`. It uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `OzoneKey`, `OzoneOutputStream`, `OMException`, `BucketLayout.OBJECT_STORE`, and error codes `VOLUME_ALREADY_EXISTS`, `BUCKET_ALREADY_EXISTS`, `PARTIAL_RENAME`, and `KEY_NOT_FOUND`.

## Control Flow
`@BeforeAll` starts a mini-cluster with ACLs enabled, wildcard administrators, a larger SCM Ratis pipeline limit, and object-store default bucket layout. Each test creates metadata, restarts OM and SCM, then re-runs operations against the same client-side object handles or object store. The key test writes one key, attempts a two-key rename where one source is missing, verifies partial rename semantics, restarts, and checks that the successful rename persisted while the missing target remains absent.

## State and Persistence
The tested persistent state is OM RocksDB metadata for volumes, buckets, key entries, and rename results. Restarting both OM and SCM validates that metadata reload and client operation routing still preserve idempotent error behavior. The key test relies on persisted rename side effects despite `PARTIAL_RENAME`.

## Dependencies and Integration Points
This file integrates the object-store Java client, OM metadata layer, SCM restart path, bucket layout defaults, ACL configuration, and key create/rename APIs.

## Risks and Edge Cases
The tests reuse some client-side volume/bucket handles across restart, so failures can reflect handle/proxy behavior as well as server persistence. The key rename test intentionally accepts partial failure and then verifies only the expected successful subset. Random numeric suffixes reduce but do not completely eliminate name collision risk in reused clusters.

## Test Signals
Signals include duplicate volume and bucket creation returning stable error codes after restart, existing metadata being retrievable after restart, renamed key metadata surviving restart, and absent rename inputs remaining absent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerRestart.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerRocksDBLogging.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerRocksDBLogging.java

## Purpose
Integration test for OM RocksDB logging configuration. It verifies that RocksDB log output is absent when disabled and appears after enabling logging and restarting OM.

## Important APIs and Types
The class `TestOzoneManagerRocksDBLogging` uses `OzoneConfiguration`, `RocksDBConfiguration`, `DBStoreBuilder.ROCKS_DB_LOGGER`, `GenericTestUtils.LogCapturer`, and `MiniOzoneCluster`. Key methods are `init`, `shutdown`, `testOMRocksDBLoggingEnabled`, `enableRocksDbLogging`, and `waitForRocksDbLog`.

## Control Flow
Each test starts a mini-cluster without datanodes after explicitly disabling RocksDB logging in the configuration. The test first asserts that waiting for a RocksDB log marker times out. It then toggles the config object to enable logging, restarts OM, and waits until captured logs contain the RocksDB implementation marker `db_impl.cc`.

## State and Persistence
The tested state is configuration-derived RocksDB logger behavior across OM restart. No Ozone object metadata is created. The `LogCapturer` is static and observes process-level logger output.

## Dependencies and Integration Points
This integrates OM DB initialization, `RocksDBConfiguration` serialization back into `OzoneConfiguration`, mini-cluster restart, and the HDDS RocksDB logger bridge.

## Risks and Edge Cases
The test is timing-sensitive because log emission depends on RocksDB startup internals. The captured marker is implementation-specific. Because the log capturer is static, earlier logs could affect repeated execution if not isolated by the initial timeout expectation.

## Test Signals
Passing confirms disabled RocksDB logging suppresses expected low-level RocksDB output and enabling the configuration takes effect after OM restart.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerRocksDBLogging.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestRecursiveAclWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestRecursiveAclWithFSO.java

## Purpose
Abstract non-HA integration tests for recursive ACL enforcement and default ACL assignment in FILE_SYSTEM_OPTIMIZED buckets. It focuses on directory delete/rename permission checks that must inspect descendants, not just the requested parent path.

## Important APIs and Types
The class `TestRecursiveAclWithFSO` implements `NonHATests.TestCase`. Important tests are `testKeyDeleteAndRenameWithoutPermission` and `testKeyDefaultACL`. Helpers include `removeAclsFromKey`, `createVolumeWithOwnerAndAcl`, `setVolumeAcl`, `addVolumeAcl`, `setBucketAcl`, `setKeyAcl`, and `createKeys`. It uses `UserGroupInformation`, `ObjectStore`, `OzoneBucket`, `OzoneVolume`, `OzoneObjInfo`, `OzoneAcl`, `BucketArgs`, and `OMException.ResultCodes.PERMISSION_DENIED`.

## Control Flow
The permission test creates a volume owned by one test user, grants broad world ACLs, builds a multi-level FSO tree, then removes ACLs from a child file or child directory. A second user attempts recursive delete and rename on ancestor directories and must receive permission-denied errors. The default ACL test creates a volume, bucket, and key under different login users and asserts owner/group default ACL entries match `OmConfig` defaults.

## State and Persistence
Persistent OM state includes volume ownership, bucket and key ACL rows, FSO directory/key metadata, and default ACL entries. The test mutates the global/login UGI, so request identity is part of the test state. Removing all ACLs from a descendant should persist and influence later recursive operations on ancestors.

## Dependencies and Integration Points
This ties together OM ACL manager behavior, FSO path resolution, recursive directory delete/rename paths, Ozone object-store clients, `OzoneObj` ACL APIs, and Hadoop UGI identity.

## Risks and Edge Cases
The test depends on process-wide login user changes and must be isolated by the surrounding cluster provider. One created user has a group string containing a comma inside a single group array entry, which may be intentional but is easy to misread. Recursive ACL traversal can be expensive and timing-sensitive in larger trees; this test uses a compact but branching tree.

## Test Signals
Signals include permission denial when any descendant lacks needed access, denial for a directory where the acting user has no ACLs, correct default volume ACLs for admin user and group, and correct default bucket/key ACLs for the active user and primary group.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestRecursiveAclWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestScmSafeMode.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestScmSafeMode.java

## Purpose
Integration tests for SCM safe mode behavior as observed through OM, SCM client APIs, and OFS filesystem writes. It verifies restricted operations during safe mode, force-exit behavior, container threshold tracking, disabled safe mode, and client retry while SCM leaves safe mode.

## Important APIs and Types
The class `TestScmSafeMode` uses `MiniOzoneCluster`, `StorageContainerManager`, `SCMClientProtocolServer`, `StorageContainerLocationProtocolClientSideTranslatorPB`, `SCMSafeModeManager`, `ContainerManager`, `ContainerInfo`, `EventQueue`, `FileSystem`, `SafeMode`, `FSDataOutputStream`, `OMMetrics`, and `SCMException`. Test methods include `testSafeModeOperations`, `testIsScmInSafeModeAndForceExit`, `testSCMSafeMode`, `testSCMSafeModeRestrictedOp`, `testSCMSafeModeDisabled`, and `testCreateRetryWhileSCMSafeMode`.

## Control Flow
Setup tunes heartbeat/stale/dead intervals, builds the cluster without initially starting datanodes, starts them, and waits for readiness. Tests stop and rebuild the cluster with existing metadata to force SCM safe mode before datanodes report. They then check allocation failure messages, force exit, close containers manually, process event queues, shut down datanodes, and exercise OFS file creation while a helper thread restarts datanodes after an allocate-block failure is observed.

## State and Persistence
Persistent state includes SCM container metadata and OM key/bucket metadata created before restart. Safe mode state is runtime SCM state driven by datanode heartbeats, container reports, threshold counters, and configuration flags. Metrics such as `getNumBlockAllocateFails` are used as synchronization signals.

## Dependencies and Integration Points
The test spans OM allocate-block calls, SCM container allocation and pipeline lookup, datanode lifecycle, filesystem `SafeMode` interface, OFS URI configuration, SCM event queues, and container lifecycle transitions.

## Risks and Edge Cases
The class is marked unhealthy for HDDS-3260 and uses sleeps/timeouts around heartbeat-driven state. Some tests rebuild clusters while retaining builder/config state, so ordering and cleanup matter. Assertions depend on exact exception message fragments from safe-mode prechecks.

## Test Signals
Important signals are safe-mode allocation failures, `inSafeMode` and `forceExitSafeMode` API transitions, threshold reaching the configured cutoff after datanodes start, restricted open-container pipeline lookup during degraded safe mode, safe-mode disabled override, and successful file creation after retry while SCM exits safe mode.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestScmSafeMode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestSecureOzoneManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestSecureOzoneManager.java

## Purpose
Unit-style integration coverage for secure OM certificate initialization. It exercises `OMCertificateClient` behavior for missing and partial key/certificate material and validates secure OM initialization failure reporting when the OM RPC address cannot be resolved for certificate signing.

## Important APIs and Types
The class `TestSecureOzoneManager` uses `OzoneConfiguration`, `OMStorage`, `SecurityConfig`, `OMCertificateClient`, `CertificateClient.InitResponse`, `KeyStorage`, `CertificateCodec`, `KeyStoreTestUtil`, `OzoneManager.initializeSecurity`, and `HddsProtos.OzoneManagerDetailsProto`. Important tests are `testSecureOmInitFailures` and `testSecureOmInitFailure`.

## Control Flow
`@BeforeEach` enables Ozone security, Kerberos authentication, ACLs, metadata dirs, and test secure OM mode, then builds OM details from the config. The main test constructs `OMCertificateClient` repeatedly while deleting or creating key/certificate files between cases. It checks init responses for first boot, existing keypair without certificate, missing public key, missing private key, certificate-only, private-key-plus-certificate, and full keypair-plus-certificate states. The second test sets an invalid OM address and asserts `initializeSecurity` throws a descriptive runtime exception.

## State and Persistence
The test persists private/public key files and certificate files in the temporary metadata/security directory. It also records certificate serial ID in `OMStorage`. The state matrix is intentionally mutated between client initializations to cover recovery/failure decisions.

## Dependencies and Integration Points
This connects OM security bootstrap, HDDS key storage layout, certificate codec, generated X.509 test certificates, SCM certificate acquisition path, Kerberos config, and OM address binding.

## Risks and Edge Cases
The test toggles `OzoneManager.setTestSecureOmFlag(true)` and does not reset it in this file, so suite-level isolation matters. Some cases pass null SCM IDs or clients intentionally, so response expectations encode bootstrap assumptions. File deletion order is critical for distinguishing missing-public-key from missing-private-key states.

## Test Signals
Signals include correct `GETCERT`, `FAILURE`, and `SUCCESS` responses for each local material combination, correct key/certificate object availability after init, and clear failure message when secure initialization cannot obtain an SCM-signed certificate for an unresolved OM address.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestSecureOzoneManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/multitenant/RangerUserRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/multitenant/RangerUserRequest.java

## Purpose
Test helper for creating, querying, and deleting Apache Ranger users through Ranger Admin REST endpoints because the Ranger client used by Ozone tests does not provide those user-management APIs.

## Important APIs and Types
The helper class `RangerUserRequest` exposes `getUserId`, `createUser`, and `deleteUser`. Internal methods include `setupRangerIgnoreServerCertificate`, `openURLConnection`, `makeHttpCall`, `makeHttpGetCall`, `getCreateUserJsonStr`, and `getResponseData`. It uses `HttpURLConnection`, `HttpsURLConnection`, custom `X509TrustManager`, `SSLContext`, Ozone Ranger endpoint constants, `JsonUtils`, Jackson `JsonNode`, and Kerby `Base64`.

## Control Flow
Construction normalizes the Ranger endpoint, builds a Basic authorization header, and installs a permissive default HTTPS socket factory. Calls open HTTP or HTTPS connections, set method, timeouts, JSON headers, authorization, and optional request body. `createUser` posts generated JSON and parses the returned `id`; `getUserId` reads the Ranger user search/list response and scans `vXUsers` for the requested principal; `deleteUser` sends a force-delete request and accepts HTTP 200 or 204.

## State and Persistence
Runtime state is the Ranger endpoint, Basic auth header, and timeout values. Durable effects are external Ranger user records created or deleted via REST. The helper also mutates JVM-wide HTTPS default socket factory, which persists beyond one instance.

## Dependencies and Integration Points
It supports multitenancy Ranger sync integration tests, bridging Ozone test code to Ranger Admin user endpoints. It relies on Ozone constants for endpoint paths and Ranger's JSON response schema.

## Risks and Edge Cases
The permissive trust manager disables certificate validation process-wide for `HttpsURLConnection`, acceptable only in controlled integration tests. JSON request bodies are manually concatenated and do not escape usernames/passwords. `isSpnego` parameters are unused. Error handling logs some 400/401 cases but can return null response data, and Java `assert userInfo != null` is ineffective unless assertions are enabled.

## Test Signals
This file is helper infrastructure, not a test class. Its signals are indirect: Ranger sync tests can create cleanup users, resolve user IDs, and remove users after policy/role reconciliation checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/multitenant/RangerUserRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/multitenant/TestMultiTenantVolume.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/multitenant/TestMultiTenantVolume.java

## Purpose
Mini-cluster integration tests for Ozone multitenancy volume routing, tenant API upgrade finalization gating, S3 secret compatibility, tenant quota behavior, Ranger service-version persistence, and tenant ID validation.

## Important APIs and Types
The class `TestMultiTenantVolume` uses `MiniOzoneCluster`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `RpcClient`, `S3Auth`, `OzoneManagerProtocol`, `UpgradeFinalization`, `OMLayoutFeature`, `OMMultiTenantManagerImpl`, `S3SecretValue`, `OzoneQuota`, and multitenancy object-store APIs such as `createTenant`, `tenantAssignUserAccessId`, `tenantRevokeUserAccessId`, `deleteTenant`, `getS3Volume`, and `createS3Bucket`.

## Control Flow
`@BeforeAll` starts an OM-only cluster with multitenancy enabled, Ranger skipped for dev tests, and initial OM layout version forced before multitenancy finalization. It runs `preFinalizationChecks`, which asserts tenant APIs fail before finalization while S3 secret APIs still work, then triggers OM upgrade finalization and waits for completion. Tests then create default or tenant-scoped object stores, set thread-local S3 auth access IDs, create buckets, revoke tenant users, delete tenants/volumes, and validate quota and ID behavior.

## State and Persistence
Persistent OM state includes tenant table entries, tenant volumes, S3 bucket metadata, access ID mappings, S3 secrets, meta-table Ranger service version, and quota fields on tenant volumes. The manually created `ObjectStore` carries S3 auth state in the `RpcClient` thread-local rather than through the default mini-cluster client.

## Dependencies and Integration Points
This integrates OM upgrade finalization, multitenant manager, S3 auth routing, object-store S3 bucket APIs, OM metadata tables, quota handling, and Ranger background sync version writes through Ratis.

## Risks and Edge Cases
The static cluster is shared across tests, so cleanup of tenants, buckets, and volumes matters. `getStoreForAccessID` constructs `RpcClient` instances without explicit close in this file. The default tenant ID strictness test assumes S3-compliant naming is enabled by default and checks message content for underscores.

## Test Signals
Signals include tenant APIs blocked before finalization, S3 secret APIs still available before finalization, non-tenant S3 requests routed to the default S3 volume, tenant access ID requests routed to the tenant volume, other users not seeing tenant buckets, Ranger service version persisted in OM metadata, tenant volume quotas set/read correctly, and invalid tenant IDs rejected.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/multitenant/TestMultiTenantVolume.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/multitenant/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/multitenant/package-info.java

## Purpose
Package descriptor for `org.apache.hadoop.ozone.om.multitenant` integration tests. It supplies package-level documentation indicating these files are Ozone Manager tests.

## Important APIs and Types
No runtime API or types are defined beyond the Java package declaration.

## Control Flow
There is no executable control flow. Java tooling uses it as package metadata.

## State and Persistence
No mutable state or persistence.

## Dependencies and Integration Points
The package groups OM multitenancy integration tests and Ranger helper code under a shared namespace.

## Risks and Edge Cases
The only realistic risk is stale package documentation if the package purpose changes.

## Test Signals
No direct test signals; compilation confirms the package declaration matches the directory layout.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/multitenant/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/package-info.java

## Purpose
Package descriptor for `org.apache.hadoop.ozone.om` integration tests. It documents the package as Ozone Manager tests.

## Important APIs and Types
No runtime API, fields, or methods are defined beyond the package declaration.

## Control Flow
There is no runtime control flow.

## State and Persistence
No state or persistence behavior.

## Dependencies and Integration Points
This package contains OM integration tests covering prepare, restart, ACL, SCM safe mode, security, REST, and related behavior.

## Risks and Edge Cases
Only documentation drift is relevant.

## Test Signals
No direct tests; package compilation verifies source-tree alignment.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestBlockDeletionService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestBlockDeletionService.java

## Purpose
Integration tests for OM-to-SCM block deletion payloads, especially replicated and unreplicated quota fields sent with deleted blocks before and after SCM layout upgrade.

## Important APIs and Types
The class `TestBlockDeletionService` uses `MiniOzoneCluster`, `StorageContainerLocationProtocol`, `SCMPerformanceMetrics`, `BlockManager`, `BlockGroup`, `DeletedBlock`, `QuotaUtil`, `ReplicationConfig` variants (`RatisReplicationConfig`, `StandaloneReplicationConfig`, `ECReplicationConfig`), `InjectedUpgradeFinalizationExecutor`, and Mockito `ArgumentCaptor`. Key tests are `testDeleteKeyQuotaWithUpgrade` and parameterized `testDeleteKeyQuotaWithDifferentReplicationTypes`.

## Control Flow
Setup starts a nine-datanode cluster initialized at the `HBASE_SUPPORT` SCM layout with a custom upgrade finalization executor, creates a volume and bucket, and captures SCM metrics. Each test writes a fixed-size key with a specific replication config, injects a Mockito spy into SCM's private `scmBlockManager` field, deletes the key, captures the eventual `deleteBlocks` call, and verifies quota accounting. The upgrade test then finalizes SCM to `STORAGE_SPACE_DISTRIBUTION` and repeats the deletion checks.

## State and Persistence
Persistent state includes OM key metadata, deleted key entries processed by deletion service, SCM block deletion state, SCM layout version, and metrics counters for successful and failed delete-key blocks. Reflection replaces SCM's in-memory block manager with a spy while preserving the real implementation underneath.

## Dependencies and Integration Points
This couples OM key deletion service, SCM block manager RPC path, replication-specific quota calculation, SCM metrics, SCM upgrade finalization, datanode layout version, and mini-cluster object-store writes.

## Risks and Edge Cases
Reflection against `scmBlockManager` is brittle if SCM internals change. Mockito spy injection persists until overwritten, so test ordering could matter. EC configs with large cell sizes are used against small keys, relying on `QuotaUtil` semantics. The tests wait up to 50 seconds for async deletion service calls.

## Test Signals
Signals include exactly one deleted block per key, `DeletedBlock.getReplicatedSize` matching `QuotaUtil.getReplicatedSize`, unreplicated size equal to key size, successful delete metrics incrementing, failed delete metrics remaining unchanged, and behavior remaining stable across SCM layout finalization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestBlockDeletionService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestDirectoryDeletingServiceWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestDirectoryDeletingServiceWithFSO.java

## Purpose
Comprehensive integration tests for `DirectoryDeletingService` and related key/snapshot deletion services in FILE_SYSTEM_OPTIMIZED buckets. It validates empty and recursive directory purge, batching, multi-level cleanup, namespace/byte accounting, direct file deletion, double-buffer blockage, and snapshot retention interactions.

## Important APIs and Types
The class uses `MiniOzoneCluster`, Hadoop `FileSystem`, `Path`, FSO `BucketLayout`, `DirectoryDeletingService`, `KeyDeletingService`, `SnapshotDeletingService`, `DeletingServiceMetrics`, `OMMetadataManager`, `OzoneManagerDoubleBuffer`, `OzoneManagerStateMachine`, `OmSnapshotManager`, `OMFileRequest`, `OmKeyInfo`, `OmDirectoryInfo`, `RepeatedOmKeyInfo`, `SnapshotInfo`, `ReclaimableDirFilter`, and `ReclaimableKeyFilter`. Helper methods include `assertSubPathsCount`, `assertTableRowCount`, `checkPath`, `cleanupTables`, and `createFileKey`.

## Control Flow
Setup starts a three-datanode cluster, creates an FSO bucket, configures an `o3fs` URI, sets small iterate batch size, and records deletion metrics. Tests create directory trees via `FileSystem`, delete paths recursively, and poll OM metadata tables until expected row counts and service counters converge. Snapshot-focused tests suspend/resume services, create snapshots, rename and delete directories, run service tasks manually or through spies, and verify cleanup is deferred or moved between active and snapshot DBs as expected.

## State and Persistence
The key persistent state is active OM directory/file tables, deleted directory table, deleted key table, snapshot info table, snapshot renamed table, bucket namespace and byte counters, and double-buffered Ratis-applied transactions. Snapshot tests verify that deleted rows remain when referenced by snapshots and are later purged or moved only when safe.

## Dependencies and Integration Points
This file spans OM filesystem API, FSO metadata layout, async deletion services, key block deletion service, snapshot manager, Ratis double buffer, bucket accounting, and object-store snapshot APIs. It also uses Mockito to intercept snapshot manager and directory deletion service behavior in a concurrency-sensitive scenario.

## Risks and Edge Cases
The test suite is timing-sensitive with two-minute polling windows. Some scenarios manipulate OM metadata tables directly and stop the double-buffer daemon, which is powerful but brittle. Cleanup manually removes DB rows after snapshot-retention tests to protect later tests. Asynchronous services and suspended services must be resumed in all paths to avoid suite pollution.

## Test Signals
Signals include expected active/deleted table counts after empty, batched, and multi-level deletes; moved file/dir and purged dir counters; deletion metrics; namespace never becoming negative during blocked double-buffer processing; direct file deletes being handled by `KeyDeletingService`; snapshot-protected rows remaining in deleted tables; renamed-table cleanup only after safe snapshot flushing; and snapshot deleting service eventually restoring clean snapshot table counts after restart.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestDirectoryDeletingServiceWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestRangerBGSyncService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestRangerBGSyncService.java

## Purpose
External-service integration tests for `OMRangerBGSyncService`, validating reconciliation between OM multitenancy metadata and Apache Ranger policies/roles/users. The class is marked unhealthy because it requires a configured Ranger endpoint.

## Important APIs and Types
The class uses `OMRangerBGSyncService`, `RangerClientMultiTenantAccessController`, `MultiTenantAccessController.Policy`, `Role`, `RangerUserRequest`, `OMMultiTenantManager`, `OmDBTenantState`, `OmDBAccessIdInfo`, `OMMetrics`, `OmMetadataManagerImpl`, `AuthorizerLockImpl`, `OzoneManagerRatisServer`, `AuditLogger`, `KerberosName`, and Mockito. Tests include `testRemovePolicyAndRole`, `testConsistentState`, `testRecoverRangerRole`, and `testRecreateDeletedRangerPolicy`.

## Control Flow
Static setup reads Ranger connection properties from JVM system properties and configures logging. Per-test setup builds a mocked `OzoneManager`, real local OM metadata DB, mocked Ratis server that writes Ranger service version to the meta table, Kerberos short-name rules, and a real Ranger access controller. Helper `createRolesAndPoliciesInRanger` optionally populates OM tenant/access-ID tables, creates test Ranger users, creates admin/user roles, and creates default tenant policies. Tests start the background sync service, wait for its run counter to advance, shut it down, then inspect Ranger and OM DB service versions.

## State and Persistence
State is split between local OM metadata tables and the external Ranger service. OM persistence includes tenant state, access ID rows, and `RANGER_OZONE_SERVICE_VERSION_KEY` in the meta table. Ranger persistence includes users, roles, and policies created and cleaned up around each test.

## Dependencies and Integration Points
The file integrates OM multitenancy desired-state generation, Ranger REST/client APIs, OM audit/metrics, Ratis-mediated meta-table writes, Kerberos user normalization, and Ranger cleanup helper calls.

## Risks and Edge Cases
Tests require real Ranger credentials and endpoint system properties. Cleanup is best-effort and logs errors rather than failing, so leaked Ranger resources are possible after partial failures. The companion `RangerUserRequest` globally relaxes HTTPS certificate validation. Exact Ranger error status codes are asserted for missing policy/role lookups.

## Test Signals
Signals include orphan Ranger policies/roles being deleted when no OM DB tenant exists, no Ranger writes for consistent desired state, tampered role membership being restored from OM DB access IDs, deleted tenant policies being recreated, and OM DB Ranger service version matching Ranger's policy version after sync.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestRangerBGSyncService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestRootedDDSWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestRootedDDSWithFSO.java

## Purpose
Integration test for `DirectoryDeletingService` when using rooted OFS paths (`ofs://om/volume/bucket/path`) with FILE_SYSTEM_OPTIMIZED buckets. It specifically validates recursive bucket and volume deletion through the rooted filesystem view.

## Important APIs and Types
The class `TestRootedDDSWithFSO` uses `MiniOzoneCluster`, `FileSystem`, `Path`, `OzoneClient`, `OzoneBucket`, `DirectoryDeletingService`, `OMMetrics`, `OMMetadataManager` tables, `OmDirectoryInfo`, `OmKeyInfo`, and the shared `TestDirectoryDeletingServiceWithFSO.assertSubPathsCount` helper.

## Control Flow
Setup starts a three-datanode cluster with FSO default bucket layout, creates a volume and bucket, configures the OFS default filesystem root, and sets a small iterate batch size. `testDeleteVolumeAndBucket` creates a tree with five two-level directory branches and six files, asserts initial table row counts, deletes the bucket path recursively, deletes the volume path non-recursively, and then polls metadata tables and deletion-service counters.

## State and Persistence
Persistent state includes FSO directory and key table rows under the volume/bucket, OM key-delete metrics, and deletion-service counters for moved files and purged dirs. The test checks that bucket and volume namespace metadata disappear from the rooted filesystem after delete.

## Dependencies and Integration Points
This bridges OFS path handling, FSO metadata layout, recursive bucket deletion, volume deletion, OM metrics, and async directory deletion service behavior.

## Risks and Edge Cases
Cleanup deletes only top-level rooted filesystem entries non-recursively, which assumes the test has already cleaned nested state. The moved-file count intentionally excludes one immediate file under the bucket because it is moved during bucket delete, so this assertion encodes detailed service behavior.

## Test Signals
Signals include rooted path deletion success, volume path becoming not found, active dir/key tables reaching zero, OM key delete metric incrementing once for bucket deletion, moved subfile count matching nested files, and deleted directory count matching total directories.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestRootedDDSWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestSnapshotDeletingServiceIntegrationTest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestSnapshotDeletingServiceIntegrationTest.java

## Purpose
Large integration suite for snapshot deletion, snapshot deep cleaning, active DB to snapshot DB movement, snapshot-chain rewiring, and locking with concurrent key deletion. It covers both object-store and FSO bucket layouts.

## Important APIs and Types
The class uses `MiniOzoneCluster`, `SnapshotDeletingService`, `KeyDeletingService`, `DirectoryDeletingService`, `OmSnapshot`, `OmSnapshotManager`, `SnapshotInfo`, `SnapshotChainManager`, `SnapshotUtils`, `MultiSnapshotLocks`, `ReclaimableKeyFilter`, `OMLockDetails`, `OMMetadataManager` tables, `RepeatedOmKeyInfo`, `OmKeyInfo`, `OmDirectoryInfo`, and Mockito construction mocking. Main tests include `testMultipleSnapshotKeyReclaim`, `testSnapshotSplitAndMove`, `testSnapshotWithFSO`, and parameterized `testSnapshotDeletingServiceWaitsForKeyDeletingService`.

## Control Flow
Setup configures small block/chunk sizes, short deletion service intervals, snapshot deep cleaning, filesystem snapshot support, and a default bucket. Helper `createSnapshotDataForBucket` creates keys, snapshots, overwrites, deletes, and then deletes an intermediate snapshot to exercise reclaim and snapshot-chain changes. FSO testing suspends deletion services, creates keys/directories/snapshots, performs overwrites, deletes, key renames and dir renames, resumes services for deep cleaning, inspects snapshot DB tables, deletes snapshots, and verifies rows move to the next snapshot or active DB. The locking test constructs a `KeyDeletingTask`, mocks `ReclaimableKeyFilter` and `MultiSnapshotLocks`, races snapshot deletion against key deletion, and asserts snapshot GC waits for key deletion to finish.

## State and Persistence
Persistent state spans active key/file/directory tables, active deleted table, active deleted dir table, active renamed table, per-snapshot RocksDB metadata tables, snapshot info rows, snapshot cache, and snapshot chain predecessor IDs. Runtime state includes retained `OmSnapshot` suppliers that must be closed and suspended/resumed deletion services.

## Dependencies and Integration Points
This integrates OM snapshot APIs, object-store and FSO metadata layouts, key and directory deleting services, snapshot deleting service, snapshot cache, snapshot chain manager, active DB and checkpointed snapshot DBs, Ratis double-buffer flushing, and lock ordering for snapshot garbage collection.

## Risks and Edge Cases
The class is marked unhealthy and some tests are flaky. It is order-dependent through `@TestMethodOrder` and a `runIndividualTest` flag. Tests suspend services and hold snapshot references, so cleanup in `@AfterEach` is essential. Construction mocking of lock/filter classes is sensitive to implementation changes. Table row counts encode detailed garbage-collection semantics and can fail if cleanup batching changes without semantic regressions.

## Test Signals
Signals include deleted keys being reclaimed or retained according to snapshot references, deleted snapshot rows disappearing, next snapshot predecessor IDs rewired, snapshot cache purged, deleted entries split/moved into the next snapshot DB, FSO deleted dir/deleted key/renamed tables moved across snapshots and active DB correctly, deep-clean flags set, and snapshot deletion acquiring locks only after concurrent key deletion work finishes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestSnapshotDeletingServiceIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/SnapshotTests.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/SnapshotTests.java

## Purpose
Abstract nested-test aggregator for OM snapshot filesystem tests across bucket layouts and linked-bucket modes. It provides one shared mini-cluster and instantiates `TestOmSnapshotFileSystem` variants for FSO, FSO with linked buckets, legacy, and legacy with linked buckets.

## Important APIs and Types
The class `SnapshotTests` extends `ClusterForTests<MiniOzoneCluster>`. It overrides `onClusterReady` and defines nested classes `OmSnapshotFileSystemFso`, `OmSnapshotFileSystemFsoWithLinkedBuckets`, `OmSnapshotFileSystemLegacy`, and `OmSnapshotFileSystemLegacyWithLinkedBuckets`, each extending `TestOmSnapshotFileSystem`.

## Control Flow
When the cluster is ready, `onClusterReady` stops the OM key manager so deletion services do not purge keys that snapshot filesystem tests still need to read. Each nested class calls the superclass constructor with a bucket layout (`FILE_SYSTEM_OPTIMIZED` or `LEGACY`) and linked-bucket flag, and returns the shared cluster from `cluster()`.

## State and Persistence
The key state change is stopping the key manager/deletion services for the shared cluster. Snapshot filesystem tests then operate against persistent OM metadata without background deletion removing test data prematurely.

## Dependencies and Integration Points
This file integrates JUnit nested tests, the Ozone test cluster provider, bucket layout variants, linked bucket scenarios, and shared snapshot filesystem test logic in `TestOmSnapshotFileSystem`.

## Risks and Edge Cases
Stopping the key manager affects all nested tests and assumes those tests do not require active deletion services. Because the implementation is an aggregator, failures will often originate in the inherited `TestOmSnapshotFileSystem` behavior rather than this file.

## Test Signals
Signals are indirect: all nested snapshot filesystem variants run against the same cluster configuration and bucket-layout matrix while preserving readable deleted/snapshot key state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/SnapshotTests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOMDBCheckpointUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOMDBCheckpointUtils.java

## Purpose
Unit tests for `OMDBCheckpointUtils` behavior related to estimated checkpoint tarball size logging and HTTP request parsing for including snapshot data in OM DB checkpoints.

## Important APIs and Types
The class `TestOMDBCheckpointUtils` uses `OMDBCheckpointUtils.logEstimatedTarballSize`, `OMDBCheckpointUtils.includeSnapshotData`, `GenericTestUtils.LogCapturer`, `HttpServletRequest`, JUnit `@TempDir`, and Mockito request stubbing. Helpers include `writeSstFilesToDirectory` and `getExpectedLogLine`.

## Control Flow
`writeSstFilesToDirectory` writes fake `.sst` files with random bytes into the temporary DB directory. `testlogEstimatedTarballSize` captures logs, logs a checkpoint estimate without snapshots, waits for a 100 KB log prefix, then adds the DB directory as a snapshot directory and waits for a 200 KB estimate including 20 SST files and one snapshot. `testIncludeSnapshotData` mocks the request parameter `OZONE_DB_CHECKPOINT_INCLUDE_SNAPSHOT_DATA` as `true` and `false` and asserts boolean parsing.

## State and Persistence
Temporary filesystem state consists of generated `.sst` files under `dbDir`; no Ozone metadata DB is opened. Log output is captured from the `OMDBCheckpointUtils` logger. Request state is mocked in-memory.

## Dependencies and Integration Points
This file covers the snapshot checkpoint utility used by OM DB checkpoint/tarball streaming paths and the HTTP parameter controlling snapshot data inclusion.

## Risks and Edge Cases
The size test only verifies log substrings and uses the same directory as both checkpoint and snapshot input for the second estimate. It does not cover null request parameters, uppercase values, non-SST files, nested snapshot directories, or exact log formatting when snapshots are absent because the expected no-snapshot line is only a prefix.

## Test Signals
Signals include checkpoint size estimation accounting for snapshot SST files and `includeSnapshotData` returning true only when the request parameter is the string `true`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOMDBCheckpointUtils.java -->
