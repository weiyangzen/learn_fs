# subset-b-008108 research

Grouped source research for Apache Ozone OM lock, multitenant, Ratis, snapshot, and request test files. Each section preserves the source path and is bounded by reconciliation markers for later splitting.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestOzoneLockProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestOzoneLockProvider.java

Purpose: unit test coverage for `OzoneLockProvider.createLockStrategy(BucketLayout)`, ensuring the configured key path lock and filesystem path flags choose the expected `OzoneLockStrategy` implementation across every `BucketLayout`.

Important APIs/types: `OzoneLockProvider`, `OzoneLockStrategy`, `OBSKeyPathLockStrategy`, `RegularBucketLockStrategy`, `BucketLayout`, and mocked `OzoneManager.getOzoneLockProvider()`. The parameter source enumerates all four boolean combinations of `keyPathLockEnabled` and `enableFileSystemPaths`.

Control flow: `testOzoneLockProvider` stores the parameter flags, loops through `BucketLayout.values()`, builds an `OzoneLockProvider`, and asserts implementation type only for behavior that should be constrained. If key path locking is enabled, `OBJECT_STORE` and legacy-without-filesystem-paths must use OBS key path locking. If key path locking is disabled, all layouts must return the regular bucket strategy.

State and persistence behavior: there is no persistent state; all state is per-test booleans and a Mockito `OzoneManager`. The test guards strategy selection that later affects lock granularity and contention behavior in OM metadata operations.

Dependencies and integration points: integrates with OM bucket layout policy and lock strategy implementations. Uses JUnit 5 parameterized tests and Mockito. Logging emits current flags and layout.

Risks: the test does not assert the positive strategy for every key-path-enabled layout, so FSO or legacy-with-filesystem-paths behavior can change without direct assertion. It also uses `assertInstanceOf` only on selected branches.

Test signals: verifies the expected object-store and legacy/OBS path-lock decisions and the full fallback when key path locking is disabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestOzoneLockProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestOzoneManagerLock.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestOzoneManagerLock.java

Purpose: broad unit coverage for `OzoneManagerLock`, including leveled lock ordering, DAG-style snapshot lock ordering, read/write/resource lock contention, multi-user locking, hold counts, and lock metrics.

Important APIs/types: `OzoneManagerLock`, `IOzoneManagerLock.Resource`, `OzoneManagerLock.LeveledResource`, `DAGLeveledResource`, `OMLockMetrics`, `MetricsCollectorImpl`, and generated resource names. Helper `ResourceInfo` records lock resources for stack-based release in reverse order.

Control flow: parameterized tests acquire and release every leveled resource; reacquire tests distinguish non-reentrant resources (`USER_LOCK`, `S3_SECRET_LOCK`, `PREFIX_LOCK`) from reentrant locks. Ordering tests acquire lower-level then higher-level locks, while violation tests attempt the inverse and assert runtime error messages. DAG tests encode forbidden edges for snapshot DB/content/local/GC/bootstrap locks. Contention tests start secondary threads and use `AtomicBoolean` plus short sleeps to verify blocking until release. Metrics tests run concurrent readers/writers and assert sample counts.

State and persistence behavior: no disk persistence. The important state is thread-local lock ownership, lock hold counts, resource-wide locks, and metrics histograms for waiting/held time.

Dependencies and integration points: depends on Ozone configuration, Hadoop metrics, JUnit parameterized tests, AssertJ, and Java concurrency. It is a behavioral contract for OM metadata mutation ordering and snapshot-related lock sequencing.

Risks: sleep-based concurrency checks can be timing-sensitive. Error message assertions are useful but couple tests to wording. Multi-resource lock tests rely on generated UUID names and do not cover every real OM key path shape.

Test signals: strong coverage of allowed and forbidden lock order, same-thread reentrancy policy, cross-thread exclusion, multi-lock collision, resource-wide lock conflicts, and metrics export fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestOzoneManagerLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestPoolBasedHierarchicalResourceLockManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestPoolBasedHierarchicalResourceLockManager.java

Purpose: tests `PoolBasedHierarchicalResourceLockManager`, the pool-backed hierarchical lock implementation for DAG resources, covering basic locking, resource-wide locks, key-level locks, pool limits, cleanup semantics, and DAG order enforcement.

Important APIs/types: `PoolBasedHierarchicalResourceLockManager`, `HierarchicalResourceLockManager.HierarchicalResourceLock`, `DAGLeveledResource`, `IOzoneManagerLock.Resource`, and configuration keys `OZONE_OM_HIERARCHICAL_RESOURCE_LOCKS_SOFT_LIMIT` / `HARD_LIMIT`.

Control flow: setup creates a fresh manager and teardown closes it. Basic tests acquire read/write locks with try-with-resources. Concurrency tests use `CompletableFuture`, latches, and fixed thread pools to confirm write exclusivity, resource-wide exclusion against keyed read/write locks, and read/write interactions. Stress tests run many keys across threads. Custom limit tests fill the pool to the hard limit, confirm a new acquisition blocks, then release one lock to allow progress. The DAG order test iterates all DAG resource pairs and enforces forbidden ordering for snapshot content and bootstrap locks.

State and persistence behavior: no persistent state; the manager maintains an in-memory pool of resource-key lock objects and an acquired flag on handles. Pool soft/hard limits are stateful capacity controls.

Dependencies and integration points: integrates with the same snapshot DAG resource model used by OM locks. Tests rely on Java concurrency primitives, Ozone configuration, and JUnit timeouts.

Risks: several assertions depend on scheduling and sleeps. The test name typo `testResouce...` is harmless but visible. It catches normal IOException propagation only superficially.

Test signals: validates close idempotence, null validation, empty and varied key strings, reentrant read behavior, concurrent stress, pool blocking, and DAG lock-order failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestPoolBasedHierarchicalResourceLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/multitenant/MultiTenantAccessControllerTests.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/multitenant/MultiTenantAccessControllerTests.java

Purpose: abstract conformance suite for `MultiTenantAccessController` implementations, covering Ranger-style policy and role lifecycle behavior without binding to one concrete backend.

Important APIs/types: `MultiTenantAccessController`, nested `Policy`, `Role`, and `Acl` builders, `ACLType`, and `OMMultiTenantManager.OZONE_TENANT_RANGER_ROLE_DESCRIPTION`. Subclasses supply `createSubject()`.

Control flow: setup initializes test users and obtains the controller, skipping via AssertJ assumptions if policy version access is unavailable. Policy tests create, read, update, label-query, duplicate-check, and delete policies. Role tests create, duplicate-check, update membership, and delete roles. Policy-with-role tests assert creating a policy can create a referenced role and that later policy creation does not overwrite existing role users. ACL conversion tests generate all `ACLType` values except `NONE` and verify round-trip conversion through the controller.

State and persistence behavior: state lives in the controller backend. The suite expects service policy version increments after create/delete operations, persistent policy/resource uniqueness, role IDs assigned by backend, role user maps with delegation flags, and cleanup by explicit deletes.

Dependencies and integration points: integrates with Ranger-compatible policy concepts, Ozone ACL types, tenant roles, and subclasses such as the in-memory controller test. Uses JUnit 5, AssertJ, and Java collections.

Risks: because this is abstract, real backend behavior may be skipped if policy version access throws. Tests assume users `om` and `hdfs` exist for real Ranger clusters. Cleanup failures can leave backend state in non-in-memory runs.

Test signals: verifies CRUD, duplicate rejection, label filtering, policy version bumps, role preservation, role IDs, user membership mutation, and ACL string compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/multitenant/MultiTenantAccessControllerTests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/multitenant/TestInMemoryMultiTenantAccessController.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/multitenant/TestInMemoryMultiTenantAccessController.java

Purpose: binds the abstract multitenant access-controller conformance tests to the in-memory implementation selected by development configuration.

Important APIs/types: `InMemoryConfigurationForTesting`, `MutableConfigurationSource`, `OMMultiTenantManagerImpl.OZONE_OM_TENANT_DEV_SKIP_RANGER`, `MultiTenantAccessController.create`, and `InMemoryMultiTenantAccessController`.

Control flow: `createSubject()` constructs an in-memory mutable configuration, sets `OZONE_OM_TENANT_DEV_SKIP_RANGER` to true, invokes the static factory, and asserts the result is an `InMemoryMultiTenantAccessController`. The inherited test suite then exercises policy and role operations.

State and persistence behavior: backend state is in-memory and isolated to the controller instance returned per setup. There is no external Ranger server or persistent policy store. It still must emulate policy versioning, uniqueness checks, role IDs, labels, and role membership semantics expected by `MultiTenantAccessControllerTests`.

Dependencies and integration points: integrates with the controller factory and the dev-skip-Ranger branch used for tests and development. The class is intentionally package-private and has no direct tests of its own beyond inherited tests.

Risks: this subclass only proves factory routing and in-memory semantics. It does not cover HTTP/Ranger serialization or remote failure modes. If the factory condition changes, all inherited tests fail early because the instance assertion fails.

Test signals: confirms the in-memory backend is selected by configuration and satisfies the full abstract controller CRUD, role, label, version, and ACL conversion contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/multitenant/TestInMemoryMultiTenantAccessController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/package-info.java

Purpose: package-level documentation marker for `org.apache.hadoop.ozone.om` tests. It declares the package as "OM tests."

Important APIs/types: no classes, methods, or runtime APIs are defined. The only Java element is the package declaration.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: documents the test package for Javadoc and package metadata. It sits above the OM test package tree and has no direct dependency imports.

Risks: low. If removed, code behavior would not change, but package-level generated documentation would lose this brief description.

Test signals: none; this file is documentation metadata, not executable test code.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerDoubleBuffer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerDoubleBuffer.java

Purpose: tests snapshot-aware flushing, metrics, async flush notification, and S3 secret cache cleanup in `OzoneManagerDoubleBuffer`.

Important APIs/types: `OzoneManagerDoubleBuffer`, `FlushNotifier`, `OzoneManagerDoubleBufferMetrics`, `OMClientResponse`, snapshot/key/bucket response mocks, `TransactionInfo`, `S3GetSecretRequest`, `S3SecretLockedManager`, `S3SecretCache`, and `OmMetadataManagerImpl`.

Control flow: setup builds a temporary OM metadata manager and double buffer with mocked OM responses and a spied flush notifier. Parameterized cases stop the daemon, add response sequences, manually flush, and assert flush iteration counts and metrics. Snapshot create/purge responses force split flushing behavior. `testAwaitFlush` wires notifier answers to assert buffers are empty when notified and verifies repeated await semantics. S3 secret testing creates successful `GetS3Secret` requests, confirms cache population, flushes, and asserts cache entries are cleared.

State and persistence behavior: uses a real temporary metadata store, but most response DB updates are mocked no-ops except S3 secret request paths. Metrics are static/shared enough that expected totals account for cumulative state and are explicitly reset in places. Flush state spans current/ready buffers and transaction counts.

Dependencies and integration points: integrates OM metadata, audit logging, S3 secret manager/cache, Kerberos principal shortening, response classes, and double-buffer internals.

Risks: metric expectations can be brittle because metrics are shared. Manual daemon stopping avoids races but differs from production timing. Some mocked snapshot responses report `SnapshotPurge` for create mocks, so the test targets splitting semantics more than command identity.

Test signals: validates snapshot-aware split counts, flush transaction metrics, await/notify behavior, empty-buffer await, and post-flush S3 cache eviction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerDoubleBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerDoubleBufferWithDummyResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerDoubleBufferWithDummyResponse.java

Purpose: validates `OzoneManagerDoubleBuffer` with a simple custom `OMClientResponse` that writes bucket rows, proving flush-to-DB and transaction info persistence without full OM request handling.

Important APIs/types: `OzoneManagerDoubleBuffer`, `OzoneManagerDoubleBufferMetrics`, `OMMetadataManager`, `OmMetadataManagerImpl`, `TransactionInfo`, `TermIndex`, `OMClientResponse`, `@CleanupTableInfo(cleanupTables = {BUCKET_TABLE})`, and nested `OMDummyCreateBucketResponse`.

Control flow: setup creates a temporary metadata DB and starts the double buffer. The test asserts zero initial metrics, adds 100 dummy bucket create responses with monotonically increasing `TermIndex`, waits until flushed transaction count reaches 100, then validates metrics, bucket table row count, singleton metrics object identity, and `TRANSACTION_INFO_KEY` term/index persistence.

State and persistence behavior: real RocksDB-backed OM metadata tables are mutated. Each dummy response writes an `OmBucketInfo` into the bucket table through a batch operation. The double buffer persists the last applied transaction info with term `1` and index equal to the bucket count.

Dependencies and integration points: integrates batch write behavior, cleanup table annotations, bucket table definitions, metrics, and async double-buffer daemon flushing. Uses `GenericTestUtils.waitFor` to observe eventual flush.

Risks: depends on async timing with a 60-second bound. The dummy response covers bucket table writes but not validation/cache preconditions from real OM requests.

Test signals: confirms flush operation count, max/avg transactions per flush, queue size metrics, bucket table persistence, flush iteration count, and transaction info persistence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerDoubleBufferWithDummyResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerDoubleBufferWithOMResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerDoubleBufferWithOMResponse.java

Purpose: exercises `OzoneManagerDoubleBuffer` with actual OM request and response classes for volume and bucket create/delete workflows, including concurrent producers.

Important APIs/types: `OzoneManagerDoubleBuffer`, `OMVolumeCreateRequest/Response`, `OMBucketCreateRequest/Response`, `OMBucketDeleteRequest/Response`, `ExecutionContext`, `TermIndex`, `OMRequestTestUtils`, `OmMetadataManagerImpl`, volume and bucket tables, and `TransactionInfo`.

Control flow: setup builds mocked `OzoneManager`, real metadata manager, metrics, audit logger, and a large-capacity double buffer. Simple tests call `testDoubleBuffer` with increasing volume/bucket counts, spawning one daemon per volume. Mixed transaction tests create a volume, alternate bucket creates with deletes, wait for expected flushed count, then verify table row counts and row contents. Parallel mixed test runs two volume workflows concurrently and relaxes last-applied-index equality because transaction ordering can vary between threads.

State and persistence behavior: real metadata DB tables are updated by response batch operations. Cache validation runs through real request `validateAndUpdateCache` paths. The transaction info table is checked for exact term/index in serial mixed workflow and bounded index in parallel workflow.

Dependencies and integration points: integrates request validation, cache update, double-buffer persistence, audit logging, OM config, user identity, and table row counting.

Risks: high-count test (`MAX_VOLUMES` and 500 buckets each) can be expensive. Parallel test intentionally does not assert exact last-applied index. Empty catch around `setUGI` in `createBucket` can hide setup failure.

Test signals: proves real OM responses survive double-buffer batching, resulting DB rows match response payloads, deleted buckets are absent, and flush counts converge.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerDoubleBufferWithOMResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerRatisRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerRatisRequest.java

Purpose: focused tests for OM Ratis request conversion and unknown command handling.

Important APIs/types: `OzoneManagerRatisUtils.createClientRequest`, `OzoneManagerProtocolServerSideTranslatorPB`, `OMExecutionFlow`, `OMMetadataManager`, `OmMetadataManagerImpl`, `OMRequestTestUtils.createCompleteMPURequest`, `OMException`, `ProtocolMessageMetrics`, and `OzoneManagerProtocolProtos.Type.UnknownCommand`.

Control flow: `testRequestWithNonExistentBucket` creates a real metadata manager, inserts a volume only into the volume table cache, builds a Complete MPU request for a missing bucket, and asserts the Ratis utility raises `OMException.ResultCodes.BUCKET_NOT_FOUND`. `testUnknownRequestHandling` builds an `UnknownCommand` request, wires mocked OM execution flow/config, invokes the server-side translator, and compares the exact invalid-request response.

State and persistence behavior: temporary metadata state includes a cached volume entry and no bucket. No DB mutation is expected beyond setup. Unknown command processing returns an error response without writing metadata.

Dependencies and integration points: covers the boundary between protobuf OM requests, request factory creation, Ratis server-side translator, and OM execution flow.

Risks: the missing-bucket test depends on cache-visible volume state rather than a persisted volume row. Exact response equality can be brittle if error message wording changes.

Test signals: verifies semantic validation in request factory paths and graceful `INVALID_REQUEST` response for unrecognized write command types.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerRatisRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerRatisServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerRatisServer.java

Purpose: unit/integration-style tests for single-node `OzoneManagerRatisServer` startup, peer address generation, snapshot info loading, read-only command categorization, and Raft group ID derivation.

Important APIs/types: `OzoneManagerRatisServer`, `OMNodeDetails`, `OMStorage`, `OMCertificateClient`, `SecurityConfig`, `OmMetadataManagerImpl`, `TransactionInfo`, `SnapshotInfo`, `RaftGroupId`, and `OmUtils.isReadOnly`.

Control flow: setup disables system exit, creates temporary metadata/configuration, mocks OM storage and manager, constructs certificate client, starts a single-node OM Ratis server, and teardown stops it. Tests assert running lifecycle state, verify `createRaftPeer` preserves configured hostname strings, manually update transaction info then restart to ensure snapshot info is loaded, loop every OM command type through `OmUtils.isReadOnly` to detect uncategorized enum values, and verify default/custom OM service IDs map deterministically to 16-byte Raft group IDs.

State and persistence behavior: the metadata manager persists `TRANSACTION_INFO_KEY`, which is used to seed last-applied term/index on server restart. Ratis server lifecycle state is observable through `getServerState`.

Dependencies and integration points: integrates Ratis server construction, OM node details, certificate/security config, OM metadata DB, command classification, and Raft identity.

Risks: binds to local host/network behavior and real server startup. Hostname preservation test uses a synthetic DNS name and only checks formatting, not live resolution. Snapshot restart test mutates DB directly.

Test signals: verifies server starts, peer addresses are not pre-resolved, last-applied term/index survives restart, every command type is categorized, and service ID determines Raft group UUID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerRatisServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerStateMachine.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerStateMachine.java

Purpose: extensive unit coverage for `OzoneManagerStateMachine`, including Ratis transaction lifecycle, prepare-mode gating, request execution, error response handling, query handling, last-applied tracking, snapshot creation/loading, leader/configuration notifications, snapshot installation, and lifecycle methods.

Important APIs/types: `OzoneManagerStateMachine`, `OzoneManagerDoubleBuffer`, `RequestHandler`, `OzoneManagerPrepareState`, `TransactionContext`, `RaftClientRequest`, `RaftProtos`, `TermIndex`, `OMRequest`, `OMResponse`, `OMClientResponse`, `OMLockDetails`, `OmRatisSnapshotProvider`, `OMServiceManager`, and `OMMetrics`.

Control flow: setup builds the state machine with mocked OM, double buffer, handler, executor, and service manager. Start-transaction tests validate request parsing, handler validation, and group ID mismatch. Pre-append tests check prepare gate transitions and admin ACL denial. Apply/run-command tests cover leader/follower context paths, double-buffer backpressure, lock detail propagation, IOException conversion to error responses, and runtime termination. Query tests parse read requests. Term-index tests model notified/applied/skipped ranges. Snapshot tests wait for double-buffer flush before flushing DB and setting transaction info. Notification tests cover leader change audit/cache/metrics, peer-list updates, snapshot-provider init on local install, leader-ready cleanup, and Ratis event recording.

State and persistence behavior: mostly mocked, with selected real `OmMetadataManagerImpl` usage for transaction info loading. Critical state includes prepare status, last-notified/applied term indexes, skipped ranges, double-buffer unflushed permits, and metrics event strings.

Dependencies and integration points: central integration boundary among Ratis, OM request handler, double buffer, prepare state, snapshots, audit, HA service manager, and metrics.

Risks: many tests rely on mocks and may not catch serialization or DB batch side effects. Term-index skip behavior is subtle and regression-prone. Runtime error tests intentionally expect `ExitUtils.ExitException`.

Test signals: strong behavioral signals for command validation, prepared-state enforcement, error classification, snapshot safety, leader transitions, peer updates, lifecycle cleanup, and double-buffer synchronization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerStateMachine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis_snapshot/TestOmRatisSnapshotProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis_snapshot/TestOmRatisSnapshotProvider.java

Purpose: tests multipart form-data generation and download request setup in `OmRatisSnapshotProvider`.

Important APIs/types: `OmRatisSnapshotProvider`, `URLConnectionFactory`, `OMNodeDetails`, `HttpURLConnection`, `HttpConfig.Policy`, `OzoneConsts.MULTIPART_FORM_DATA_BOUNDARY`, and `OZONE_DB_CHECKPOINT_REQUEST_TO_EXCLUDE_SST`.

Control flow: setup builds a provider with temporary snapshot/download directories, a mocked leader node map, mocked HTTP policy, and mocked connection factory. `testDownloadSnapshot` makes the leader return a checkpoint URL, mocks connection output/input streams and HTTP 200 status, invokes `downloadSnapshot`, and verifies the request body contains an empty exclude-SST multipart field and closing boundary. Other tests call static `writeFormData` with one SST filename or an empty list and compare the exact wire body.

State and persistence behavior: target file is prepared in a temporary download directory, but assertions focus on request body bytes rather than downloaded content. No durable state remains.

Dependencies and integration points: integrates snapshot provider HTTP download path with leader endpoint generation and checkpoint exclude-list protocol. Uses Java `HttpURLConnection` and HDFS `URLConnectionFactory`.

Risks: exact CRLF and boundary matching is intentionally strict. The download test uses an empty input stream derived before body writes, so it mainly tests outgoing form data, not actual file copy behavior.

Test signals: validates multipart field name, boundary format, optional SST filename inclusion, closing delimiter, and provider use of leader checkpoint endpoint/connection factory.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis_snapshot/TestOmRatisSnapshotProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/OMRequestTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/OMRequestTestUtils.java

Purpose: shared test fixture utility for OM client request tests, providing helpers to seed OM metadata tables/caches and construct protobuf `OMRequest` objects across volume, bucket, key, multipart upload, ACL, tenant, snapshot, FSO, and S3-auth workflows.

Important APIs/types: `OMMetadataManager`, `OmVolumeArgs`, `OmBucketInfo`, `OmKeyInfo`, `OmDirectoryInfo`, `OmMultipartKeyInfo`, `SnapshotInfo`, `OmPrefixInfo`, `CacheKey`, `CacheValue`, `BucketLayout`, `ReplicationConfig`, `OzoneAcl`, `OzoneObjInfo`, and many `OzoneManagerProtocolProtos` request builders.

Control flow: methods are static and grouped by fixture purpose. DB seeders add volumes/buckets/users/keys/directories/snapshots/prefixes to tables and often parallel cache entries. Key helpers branch between open key table and committed key table, update bucket used bytes when possible, and handle OBS/legacy vs FSO path-key formats. Multipart helpers seed open multipart keys, multipart info, parts, and request messages. Request factories build volume property, ACL, MPU, volume create, bucket delete, tenant, S3 volume context, snapshot create/move/rename/delete, and S3-authenticated commit-key requests. Configuration helpers enable FSO paths and install replication config validators on mocked OM.

State and persistence behavior: directly mutates OM DB tables and caches, frequently with synthetic transaction indexes and object IDs from `System.currentTimeMillis()`. Some helpers only add cache entries, while others write both cache and persistent table rows.

Dependencies and integration points: heavily integrated with OM metadata schema, request protobufs, snapshot cleanup tables, FSO object ID path encoding, quota side effects, replication validation, and tests across the OM request package.

Risks: helper behavior can diverge from production request side effects; object IDs based on current time can collide under fast tests; mixed cache/table writes require callers to know visibility expectations.

Test signals: not a test class itself, but it enables broad OM request tests by constructing realistic metadata and protobuf inputs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/OMRequestTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/TestBucketLayoutAwareOMKeyFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/TestBucketLayoutAwareOMKeyFactory.java

Purpose: validates `BucketLayoutAwareOMKeyRequestFactory` mapping and reflective instantiation of `OMKeyRequest` implementations by command type and bucket layout.

Important APIs/types: `OM_KEY_REQUEST_CLASSES`, `getKey`, `addRequestClass`, `getRequestInstanceFromMap`, `OMKeyRequest`, `BucketLayout`, `Type`, `OMDirectoriesPurgeRequestWithFSO`, and protobuf `OMRequest`.

Control flow: `testGetRequestInstanceFromMap` iterates every mapping entry. Keys containing the FSO layout are instantiated with `BucketLayout.FILE_SYSTEM_OPTIMIZED`; other mappings are instantiated twice with `LEGACY` and `OBJECT_STORE`. Each instance is checked for matching bucket layout and counted. The test asserts expected counts: 15 FSO, 16 legacy, 16 OBS, and mapping-size consistency. `testAddInvalidRequestClass` registers an FSO purge-directories class under a factory key and asserts instantiation fails with `NoSuchMethodException` because the class lacks the required `(OMRequest, BucketLayout)` constructor.

State and persistence behavior: no DB state. It mutates the static request-class map in the invalid-class test, which can affect later tests if not isolated by JVM ordering or map overwrite behavior.

Dependencies and integration points: protects request factory coverage for OM key command handling across bucket layouts. Uses reflection and constructor contract as an integration point between factory registry and request classes.

Risks: hard-coded counts require updates when mappings change. Static map mutation can be order-sensitive. Key string inspection for FSO mapping assumes factory key format.

Test signals: catches missing constructors, wrong bucket layout injection, absent mappings, and count drift in key request factory registration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/TestBucketLayoutAwareOMKeyFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/TestNormalizePaths.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/TestNormalizePaths.java

Purpose: unit tests `OMClientRequest.validateAndNormalizeKey` for normalized filesystem-style keys and raw object-store-style keys.

Important APIs/types: static `validateAndNormalizeKey(boolean, String)`, `OMException`, JUnit assertions, and AssertJ message checks.

Control flow: `testNormalizePathsEnabled` passes normalization enabled and checks leading slash removal, duplicate slash collapsing, `.` removal, `..` parent traversal within bounds, trailing slash handling, preservation of literal multi-dot path segments, and normal relative paths. `testNormalizeKeyInvalidPaths` centralizes invalid cases through `checkInvalidPath`, expecting `OMException` messages containing `Invalid KeyPath`. `testNormalizePathsDisable` passes normalization disabled and verifies raw strings, including repeated slashes and parent segments, are preserved.

State and persistence behavior: none. Behavior is pure string validation/normalization with exception signaling.

Dependencies and integration points: protects OM request key-path interpretation before metadata operations. It is especially relevant for FSO-style path handling and object-store mode compatibility where raw keys are legal.

Risks: expected strings encode exact normalization semantics. Invalid cases are representative but not exhaustive for all special characters or Unicode. Disabled normalization permits forms that enabled mode rejects, so callers must pass the correct flag.

Test signals: verifies valid canonicalization, invalid traversal/empty/root/colon cases, error message content, and no-op behavior when normalization is disabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/TestNormalizePaths.java -->
