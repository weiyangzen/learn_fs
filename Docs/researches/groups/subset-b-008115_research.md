# subset-b-008115 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotUtils.java

## Purpose
`TestOmSnapshotUtils` is a focused unit test for `OmSnapshotUtils.linkFiles(File source, File target)`. It verifies that the snapshot utility can copy a directory tree structure into a target location using hard links for files, which is central to snapshot checkpoint creation and local metadata reuse.

## Important APIs, Types, and Functions
- `OmSnapshotUtils.linkFiles(tree1, tree2)` is the API under test.
- `Files.write`, `Files.walk`, and `Path::toString` construct and compare source and target directory trees.
- `IOUtils.getINode(Path)` validates hard-link identity rather than content-only equality.
- JUnit `@TempDir` provides an isolated filesystem workspace.

## Control Flow
The test builds `tree1` with two directories and one file, asserts that target `tree2` and the expected linked file do not exist, invokes `linkFiles`, and then asserts that the target tree exists. It compares source and target inode values for `f1` and `tree2/dir1/f1`, then walks both trees and normalizes `tree1` paths to the expected `tree2` paths.

## State and Persistence Behavior
This test directly exercises filesystem persistence. The key invariant is that `linkFiles` creates hard links, not byte-for-byte copied files, so the inode of the linked file must match the source. Directory structure is persisted under the temporary target root and must mirror the source.

## Dependencies and Integration Points
The test depends on filesystem hard-link support in the local platform. It integrates with the snapshot utility layer used by OM snapshot/checkpoint code and with `hdds` inode helpers.

## Risks and Edge Cases
- The test covers a nested tree and one file but not empty directories beyond `dir2`, existing destination trees, symlink handling, permission failures, or cross-filesystem hard-link errors.
- The inode assertion may be platform-sensitive if the test environment does not support hard links.

## Test Signals
Passing assertions signal that `linkFiles` creates the target tree, preserves the full path set, and makes file entries share inodes with the source.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRequireSnapshotFeatureStateAspect.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRequireSnapshotFeatureStateAspect.java

## Purpose
`TestRequireSnapshotFeatureStateAspect` validates the annotation/aspect guard that blocks snapshot operations when the Ozone snapshot feature is disabled. It uses a small utility test object and mocked AspectJ join point metadata to exercise `RequireSnapshotFeatureStateAspect.checkFeatureState`.

## Important APIs, Types, and Functions
- `RequireSnapshotFeatureStateAspect.checkFeatureState(JoinPoint)` is the method under test.
- `SnapshotFeatureEnabledUtil.snapshotMethod()` supplies the annotated target method.
- AspectJ `JoinPoint` and `MethodSignature` are mocked to emulate intercepted method invocation.
- `OMException` is expected on disabled feature state.

## Control Flow
The test creates the aspect and target utility, mocks `joinPoint.getTarget()` to return the utility, mocks the method signature to resolve `snapshotMethod`, and then invokes the aspect. It asserts that the aspect throws `OMException` with the short method name included in the failure text.

## State and Persistence Behavior
No persistent state is written. The tested state is feature availability inferred by the aspect and target method metadata.

## Dependencies and Integration Points
This test integrates AspectJ-style interception with OM exception semantics. It protects CLI/RPC snapshot operations that rely on annotation-based feature gating.

## Risks and Edge Cases
- It only tests the disabled path; it does not assert the allowed path or behavior with malformed signatures.
- Message text is asserted exactly, so changes in wording require coordinated test updates.

## Test Signals
Passing means the aspect resolves the intercepted method and emits a user-facing `OMException` for disabled snapshot operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRequireSnapshotFeatureStateAspect.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRocksDbPersistentList.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRocksDbPersistentList.java

## Purpose
`TestRocksDbPersistentList` verifies the `RocksDbPersistentList` implementation of `PersistentList` against a real temporary RocksDB instance. It confirms append and iteration semantics, including duplicate preservation and insertion order.

## Important APIs, Types, and Functions
- `RocksDbPersistentList<String>` is instantiated with `ManagedRocksDB`, a dedicated `ColumnFamilyHandle`, `CodecRegistry`, and element class.
- `PersistentList.add` persists values.
- `PersistentList.iterator()` returns a `ClosableIterator<String>`.
- `ManagedDBOptions`, `ManagedColumnFamilyOptions`, and `ManagedRocksDB.open` manage RocksDB lifecycle.

## Control Flow
`@BeforeAll` creates a RocksDB database with the default column family under `@TempDir`. The test creates a separate column family, appends `["e1", "e2", "e3", "e1", "e2"]`, iterates the persistent list, and compares each emitted value to the same index in the original list. The column family is dropped and closed in `finally`.

## State and Persistence Behavior
Values are written into a RocksDB column family. Duplicate elements must remain as distinct list entries, and iteration must reflect insertion order. Resource cleanup closes DB options, column-family options, and the DB, and drops the test column family.

## Dependencies and Integration Points
The test depends on the HDDS managed RocksDB wrappers, `CodecRegistry` raw encoding, and the Ozone `ClosableIterator` abstraction. It provides test coverage for snapshot-diff supporting persistent data structures.

## Risks and Edge Cases
- It does not reopen the DB to verify durability across process/lifecycle boundaries.
- It covers only strings and sequential iteration, not empty lists, large lists, or concurrent writes.

## Test Signals
Passing asserts that persisted list entries can be appended and read back in exact order with duplicates intact.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRocksDbPersistentList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRocksDbPersistentMap.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRocksDbPersistentMap.java

## Purpose
`TestRocksDbPersistentMap` validates the RocksDB-backed `PersistentMap` implementation for basic put/get behavior and bounded iteration. It is used by snapshot diff tables and report/job persistence paths.

## Important APIs, Types, and Functions
- `RocksDbPersistentMap<String, String>` implements `PersistentMap`.
- `put`, `get`, and `iterator(Optional<K> lowerBound, Optional<K> upperBound)` are tested.
- `CodecRegistry` encodes keys and values.
- Parameterized `rocksDBPersistentMapIteratorCases()` supplies lower/upper-bound scenarios.

## Control Flow
The class initializes one RocksDB database for all tests and creates unique column families with an atomic id. `testRocksDBPersistentMap` writes repeated keys with newer values and verifies the final map value for each unique key. The parameterized iterator test loads sparse sorted key ranges, creates an iterator with optional bounds, and checks emitted entries against expected lexicographic ranges.

## State and Persistence Behavior
The map persists serialized keys and values in RocksDB. Duplicate `put` operations overwrite existing key values. Iterator behavior follows RocksDB key ordering and respects lower and upper bounds, with the upper bound treated as exclusive in the expected cases.

## Dependencies and Integration Points
This test uses RocksDB column families through managed wrappers and `ClosableIterator<Map.Entry<K,V>>`. Snapshot diff job/report storage uses the same persistent-map abstraction.

## Risks and Edge Cases
- Iterators are not explicitly closed in the parameterized test, which is acceptable for this small scope but worth watching in resource-sensitive paths.
- Tests cover strings only and do not verify deletion, null handling, binary keys, or reopening.

## Test Signals
Passing indicates map overwrites, reads, and bounded sorted iteration work for snapshot persistent-map use cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRocksDbPersistentMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRocksDbPersistentSet.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRocksDbPersistentSet.java

## Purpose
`TestRocksDbPersistentSet` verifies the RocksDB-backed `PersistentSet` abstraction. It checks that duplicate additions collapse to unique entries and that iteration returns the same unique membership as an in-memory `HashSet`.

## Important APIs, Types, and Functions
- `RocksDbPersistentSet<String>` implements `PersistentSet`.
- `PersistentSet.add` and `PersistentSet.iterator()` are exercised.
- `ManagedRocksDB` and a dedicated column family back the set.

## Control Flow
The test initializes RocksDB in `@BeforeAll`, creates a `testSet` column family, adds `["e1", "e1", "e2", "e2", "e3"]`, builds an expected `HashSet`, and compares persistent-set iteration to the expected iterator until both are exhausted. The column family is dropped in `finally`.

## State and Persistence Behavior
The set persists serialized elements as keys or key-like records in RocksDB. Duplicate adds must not create duplicate logical entries. The test does not require deterministic ordering beyond matching the `HashSet` iterator used in the same JVM.

## Dependencies and Integration Points
It shares the RocksDB wrapper and codec path with snapshot diff support data structures.

## Risks and Edge Cases
- Comparing to `HashSet` iteration order can be brittle if persistent iteration ordering differs from hash iteration. With these fixed strings it currently works, but the core semantic under test is membership rather than ordering.
- It does not test deletion, contains checks, empty sets, or reload durability.

## Test Signals
Passing means duplicate insertions are idempotent and persisted membership can be iterated.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestRocksDbPersistentSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotCache.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotCache.java

## Purpose
`TestSnapshotCache` validates `SnapshotCache`, the refcounted cache that loads `OmSnapshot` instances, protects snapshot DB access with OM locks, performs deferred eviction/close, compacts snapshot RocksDB tables, and updates OM metrics.

## Important APIs, Types, and Functions
- `SnapshotCache.get(UUID)` returns an `UncheckedAutoCloseableSupplier<OmSnapshot>` handle.
- `release(UUID)`, `invalidate(UUID)`, `invalidateAll()`, `size()`, `totalRefCount(UUID)`, and `getPendingEvictionQueue()` expose cache and eviction behavior.
- `SnapshotCache.lock()` and `lock(UUID)` acquire resource or snapshot-specific write locks and trigger cleanup.
- `IOzoneManagerLock`, `OmReadOnlyLock`, `SNAPSHOT_DB_LOCK`, and `VOLUME_LOCK` verify lock integration.
- Mock `CacheLoader<UUID, OmSnapshot>` creates snapshots with mocked metadata managers and DB stores.

## Control Flow
Setup creates a fresh cache with size limit 3, a mocked cache loader, and metrics. Basic tests load one or more UUIDs and assert cache size and metrics. Lock tests verify read-lock acquisition on `get`, write-lock acquisition on `lock`, and lock release on load/cleanup failures. Eviction tests load/release entries past the soft limit and use `GenericTestUtils.waitFor` to observe asynchronous cleanup. Failure-path tests simulate stale eviction keys, `OmSnapshot.close()` failure retry, and unchecked compaction failure.

## State and Persistence Behavior
The cache state is in-memory but protects persistent snapshot DB handles. `get` increments refcounts and close/release decrements them; entries with zero refcount enter a pending eviction queue. Eviction compacts non-reserved tables before closing snapshots and removes entries from `dbMap` only after successful cleanup. Metrics track current cache size. Snapshot DB compaction intentionally skips DAG-tracked/reserved tables such as `keyTable`.

## Dependencies and Integration Points
The test integrates Guava `CacheLoader`, OM metrics, OM lock hierarchy, `OmSnapshot`, `OMMetadataManager`, and `DBStore`. It also verifies that snapshot operations are not blocked while compaction is waiting by using a semaphore around `compactTable`.

## Risks and Edge Cases
- Timing-dependent eviction tests rely on scheduled cleanup intervals and waits.
- The mocked DB table set is small; production table filtering must remain aligned with the DAG-tracked table list.
- Correctness depends on lock release on every exceptional path because leaked snapshot DB locks can block OM operations.

## Test Signals
Passing signals that cache loading, refcounting, metrics, invalidation, eviction, compaction filtering, and lock cleanup semantics are coherent, including retry behavior after close failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotChain.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotChain.java

## Purpose
`TestSnapshotChain` validates `SnapshotChainManager`, which maintains chronological global snapshot chains and per-bucket path chains. It covers add, delete, load-from-table, iterator behavior, and corruption detection.

## Important APIs, Types, and Functions
- `SnapshotChainManager.addSnapshot`, `deleteSnapshot`, `nextGlobalSnapshot`, `previousGlobalSnapshot`, `nextPathSnapshot`, and `previousPathSnapshot`.
- `getLatestGlobalSnapshotId`, `getOldestGlobalSnapshotId`, and `getLatestPathSnapshotId`.
- `SnapshotInfo` previous-id fields: `pathPreviousSnapshotId` and `globalPreviousSnapshotId`.
- `OMMetadataManager.getSnapshotInfoTable()` provides persisted source data for chain rebuild.

## Control Flow
Setup creates a temporary `OmMetadataManagerImpl` and a fresh chain manager. Helper `createSnapshotInfo` creates active snapshots for `vol1/bucket1`. Add/delete tests build three-node chains and validate forward/backward traversal. Load tests write snapshots to the snapshot info table, construct a new manager, and assert reconstructed links and iterator order. Invalid-chain parameterized cases create disconnected, cyclic, partial cyclic, and diverged previous-pointer maps, then verify the manager marks the chain corrupted and rejects add/delete operations.

## State and Persistence Behavior
Snapshot chain state is reconstructed from `SnapshotInfo` rows in the OM metadata table. Deletion mutates next nodes' previous pointers in the in-memory helper map to emulate production chain rewiring before calling `deleteSnapshot`. Corruption state prevents subsequent chain mutation.

## Dependencies and Integration Points
The test integrates with the OM metadata RocksDB-backed table and `SnapshotInfo` model. It verifies global and path-chain behavior used by snapshot deletion, diff ordering, defrag, and chain traversal.

## Risks and Edge Cases
- The manual `deleteSnapshot` helper mirrors production rewiring logic; if production deletion changes, test setup may need updating.
- The test covers one snapshot path for normal operations, with corruption cases focused on pointer topology rather than multi-bucket isolation.

## Test Signals
Passing means chain construction and traversal are stable across table reload, corrupted chains are detected, and mutation is blocked once corruption is found.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotChain.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDiffManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDiffManager.java

## Purpose
`TestSnapshotDiffManager` is the main unit/integration-style test for `SnapshotDiffManager`. It covers object-id map generation, diff report generation and pagination, job lifecycle state transitions, cancellation, listing, startup recovery, executor saturation, submit APIs, and report-only APIs.

## Important APIs, Types, and Functions
- `SnapshotDiffManager.addToObjectIdMap`, `generateDiffReport`, `createPageResponse`, `getSnapshotDiffReport`, `submitSnapshotDiff`, `cancelSnapshotDiff`, `getSnapshotDiffJobList`, `getSnapshotDiffJobs`, and `loadJobsOnStartUp`.
- Persistent RocksDB column families for `SNAP_DIFF_JOB_TABLE_NAME`, `SNAP_DIFF_REPORT_TABLE_NAME`, and `SNAP_DIFF_PURGED_JOB_TABLE_NAME`.
- `SnapshotDiffJob`, `SnapshotDiffResponse`, `SubmitSnapshotDiffResponse`, `CancelSnapshotDiffResponse`, and `ListSnapshotDiffJobResponse`.
- `SstFileSetReader`, `TablePrefixInfo`, `PersistentMap<byte[], byte[]>`, and `SnapshotTestUtils.StubbedPersistentMap`.
- Snapshot model and OM integration: `SnapshotInfo`, `OmSnapshotManager`, `SnapshotCache`, `OMMetadataManager`, bucket layout, key tables, and codecs for `DiffReportEntry`.

## Control Flow
`@BeforeEach` builds a temporary RocksDB store, diff job/report column families, mocked OM metadata tables, snapshot info rows for several job statuses, bucket layout data, and an `OmSnapshotManager` backed by `SnapshotCache`. Object-id map tests mock `SstFileSetReader` to return keys with and without tombstones, then verify old/new object-id maps and object-id check sets across directory/file/key tables and native-library toggles. Diff generation tests build old/new object-id maps with create/delete/rename/modify patterns, mock key comparison logic, generate reports, and assert type ordering and entries. Pagination tests write report entries into RocksDB and verify page size, token, and job isolation.

Job lifecycle tests submit and cancel snapshot diff jobs, list jobs by status, reload in-progress jobs at startup, simulate full thread pools, and verify submit/report-only behavior for `IN_PROGRESS`, `DONE`, `FAILED`, `CANCELLED`, `REJECTED`, and absent jobs. Helper methods create random snapshot contexts, populate snapshot info mocks, and configure bucket/key-table mocks for running diff operations.

## State and Persistence Behavior
Diff jobs and report entries are persisted in RocksDB through `PersistentMap` and raw column-family writes. Job keys are formed from from/to snapshot UUIDs separated by `DELIMITER`; report keys encode job id, diff type ordering, and index. State transitions are central: new/queued jobs become `IN_PROGRESS`, completed jobs become `DONE`, failed/cancelled/rejected jobs can be resubmitted by `submitSnapshotDiff`, and cancelled jobs remain visible until cleanup. Rejected jobs caused by executor saturation are removed from the job table.

## Dependencies and Integration Points
This test touches much of the snapshot diff stack: RocksDB codecs, SST key readers, OM snapshot cache, bucket layout/key-table selection, HDFS `SnapshotDiffReport` entry types, JMX-adjacent job models, and Ozone configuration for thread pool size, full diff forcing, native library loading, and max changed keys.

## Risks and Edge Cases
- Many tests use mocks for metadata and snapshots; they validate manager control flow but not a full end-to-end OM database diff.
- Native tombstone behavior is mocked via `SstFileSetReader`; real RocksDB SST parsing remains a separate risk.
- Thread-pool saturation tests are timing-sensitive and depend on sleep durations and executor behavior.
- Report key ordering must remain compatible with paging tokens and persisted report entries.

## Test Signals
Passing provides strong signals that diff manager persistence, job state machine, cancellation semantics, pagination, object-id delta generation, startup recovery, and submission short-circuit behavior remain compatible with snapshot diff clients.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDiffManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDiffManagerMXBean.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDiffManagerMXBean.java

## Purpose
`TestSnapshotDiffManagerMXBean` verifies that `SnapshotDiffManager` registers its JMX MXBean and exposes persisted snapshot diff jobs through the `SnapshotDiffJobs` attribute.

## Important APIs, Types, and Functions
- `SnapshotDiffManager` constructor registers the MBean.
- Platform `MBeanServer` and `ObjectName("Hadoop:service=OzoneManager,name=SnapshotDiffManager")` are used for lookup.
- `CompositeData[]` represents JMX job rows.
- `RocksDbPersistentMap<String, SnapshotDiffJob>` writes test job state directly to the job table.

## Control Flow
Setup opens a temporary RocksDB database with job/report/purged job column families, builds a codec registry for `SnapshotDiffJob`, mocks enough `OzoneManager` and metadata manager state for construction, and creates `SnapshotDiffManager`. The test asserts that the MBean is registered, reads an initially empty `SnapshotDiffJobs` attribute, writes a queued job directly to the job table, reads the attribute again, and checks job id, from/to snapshot names, and sub-status.

## State and Persistence Behavior
The JMX view is backed by the persisted snapshot diff job table. Adding a job to RocksDB changes the MXBean attribute output without needing a separate in-memory registration step.

## Dependencies and Integration Points
This test integrates JMX registration, RocksDB-backed persistent maps, Ozone manager metadata configuration, and snapshot diff job codecs.

## Risks and Edge Cases
- Global MBean registration can be sensitive to prior tests if teardown does not unregister correctly.
- The test verifies a small subset of exposed composite fields, not every MXBean field.

## Test Signals
Passing means operators can discover `SnapshotDiffManager` through JMX and inspect persisted diff jobs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDiffManagerMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotInfo.java

## Purpose
`TestSnapshotInfo` validates the OM metadata table for `SnapshotInfo` rows and helper methods that determine whether snapshot create/change transactions have flushed to DB.

## Important APIs, Types, and Functions
- `OMMetadataManager.getSnapshotInfoTable()` stores `SnapshotInfo`.
- `SnapshotInfo.Builder` sets identity, volume, bucket, status, creation/deletion times, previous snapshot ids, and path.
- `SnapshotInfo.setSstFiltered`, `isSstFiltered`, `setLastTransactionInfo`, and `setCreateTransactionInfo`.
- `OmSnapshotManager.areSnapshotChangesFlushedToDB` and `isSnapshotFlushedToDB`.
- `TransactionInfo`, `TermIndex`, `CacheKey`, and `CacheValue` model table/cache transaction state.

## Control Flow
Setup creates a temporary `OmMetadataManagerImpl`. Table tests assert the snapshot table exists and supports put/get/delete. The SST-filtered test toggles and persists the filtered flag. Transaction tests add snapshot info, manipulate transaction info table and cache entries, and assert flush helper results for null snapshots, null transaction fields, cached snapshot updates, matching term/index, greater index, and greater term/index.

## State and Persistence Behavior
The tests write actual metadata table rows and transaction table rows in a temp OM DB. They also use table cache entries to emulate unflushed in-memory updates. Flush helpers compare snapshot transaction markers against the OM transaction table to decide whether snapshot metadata is durable.

## Dependencies and Integration Points
This test integrates `SnapshotInfo` serialization/table storage with `OmSnapshotManager` flush checks used by snapshot lifecycle services.

## Risks and Edge Cases
- It focuses on transaction comparison semantics, not full snapshot creation/deletion workflows.
- Cache behavior is manually injected, so it assumes table cache semantics remain compatible.

## Test Signals
Passing means snapshot metadata rows persist correctly, SST-filtered state is stored, and transaction flush checks return expected safety decisions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotRequestAndResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotRequestAndResponse.java

## Purpose
`TestSnapshotRequestAndResponse` is a base fixture for snapshot request/response tests. It prepares a mocked `OzoneManager`, real `OmMetadataManagerImpl`, metrics, snapshot manager, batch operation, volume/bucket state, and helpers for creating snapshot checkpoints and synthetic deleted/renamed key records.

## Important APIs, Types, and Functions
- `baseSetup()` initializes the OM test fixture.
- `createSnapshotCheckpoint(volume, bucket, snapshotName)` exercises `OMSnapshotCreateRequest.validateAndUpdateCache` and `OMSnapshotCreateResponse.addToDBBatch`, commits transaction info, and returns the checkpoint path.
- `getDeletedKeys`, `getRenameKeys`, and `getDeletedDirKeys` build table-key/value pairs for deleted key, rename, and deleted directory scenarios.
- Mocked `OzoneManager` methods cover bucket link resolution, metrics, snapshot feature flag, admin/owner checks, ACL authorizer, layout version manager, audit logger, default replication config, and snapshot manager access.

## Control Flow
Before each derived test, the fixture creates a temporary OM metadata DB, sets metadata directories, adds a random volume and bucket, opens a batch operation, and constructs `OmSnapshotManager`. Snapshot checkpoint helper builds a create snapshot request, runs pre-execute, validates/updates cache at transaction index 1, batches response writes and transaction info, commits, reads the resulting `SnapshotInfo`, and computes the expected checkpoint directory under the snapshot parent directory.

## State and Persistence Behavior
This base writes real OM metadata state into a temp RocksDB store. Snapshot checkpoint creation persists `SnapshotInfo` and transaction info, and creates a snapshot checkpoint directory. Helper key generators produce deterministic deleted and rename table keys that downstream tests can write into metadata tables.

## Dependencies and Integration Points
The class bridges request-layer code, response batch commits, audit/ACL/version mocks, metrics, replication config, bucket layout resolution, and snapshot manager behavior. It is not itself a test class with `@Test` methods but is a shared integration fixture.

## Risks and Edge Cases
- Because it centralizes many mocks, downstream tests can inherit assumptions about admin status, bucket layout, ACL behavior, and feature enablement.
- `stop()` clears inline mocks and closes batch operations; derived classes must avoid using fixture state after teardown.

## Test Signals
When used by subclasses, successful setup and checkpoint creation signal that snapshot request/response flows can be exercised against a real metadata manager with controlled OM dependencies.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotRequestAndResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotUtils.java

## Purpose
`TestSnapshotUtils` validates `SnapshotUtils.isBlockLocationInfoSame`, which determines whether two `OmKeyInfo` objects refer to equivalent block locations for snapshot diff and reclaim decisions.

## Important APIs, Types, and Functions
- `SnapshotUtils.isBlockLocationInfoSame(OmKeyInfo previous, OmKeyInfo deleted)` is the method under test.
- Helpers create `OmKeyLocationInfo`, `OmKeyLocationInfoGroup`, and `OmKeyInfo` objects.
- `OzoneConsts.HSYNC_CLIENT_ID` metadata marks hsync keys.
- `BlockID` and location group lists model block identity and versions.

## Control Flow
The tests cover null/null, one-null, both hsync, mismatched location-version counts, null latest locations, mismatched location-list sizes, block id mismatch, exact block id match, and partial mismatch across multiple blocks. For hsync keys, matching block ids with different lengths are treated as same unless object IDs differ.

## State and Persistence Behavior
No persistent state is used. The state under test is in-memory key metadata: object id, hsync marker, location groups, block ids, and block list shape.

## Dependencies and Integration Points
The helper influences snapshot diff/reclaim logic by deciding whether a key's block location changed between snapshots or deleted table entries.

## Risks and Edge Cases
- Tests focus on block id and structural comparisons; other `OmKeyInfo` fields are intentionally ignored here.
- Hsync behavior is special and relies on metadata and object id handling.

## Test Signals
Passing means block-location equivalence handles nulls, hsync keys, version/list size mismatches, and block id mismatches as expected.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSstFilteringService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSstFilteringService.java

## Purpose
`TestSstFilteringService` is an integration-style test for the background `SstFilteringService`, which removes irrelevant RocksDB SST files from snapshot checkpoints while preserving bucket-visible data. It also verifies service interactions with deleted snapshots and defrag-service enablement.

## Important APIs, Types, and Functions
- `KeyManager.getSnapshotSstFilteringService()` obtains the service.
- `SstFilteringService.getSnapshotFilteredCount`, `pause`, `resume`, `getBootstrapStateLock`, and `isSstFiltered`.
- `OmTestManagers` provides a runnable in-process OM, key manager, and write client.
- `RDBStore.getDb().flush(KEY_TABLE)` and `compactRange(KEY_TABLE)` force SST layout.
- Snapshot operations go through `OzoneManagerProtocol.createSnapshot` and `deleteSnapshot`.
- Helpers create volumes, buckets, keys, and list keys from active DB or `OmSnapshot` metadata.

## Control Flow
Class setup creates an OM with short container-report and SST-filtering intervals and DB profile `TEST`. `testIrrelevantSstFileDeletion` writes keys to one bucket, flushes and compacts, writes another bucket, snapshots the second bucket, waits for filtering, verifies active and snapshot key sets match, and checks that non-level-0 irrelevant SST files are removed from the snapshot directory while relevant ones remain. It also holds the bootstrap lock to prove filtering pauses and later resumes. `testActiveAndDeletedSnapshotCleanup` pauses filtering, creates two snapshots, deletes one, resumes, and verifies only active snapshot SST files are reduced while deleted snapshot files remain but counts/flags advance. `testSstFilteringService` writes 150 random keys across three buckets with periodic flush/compaction, snapshots each bucket, waits for filtering, and validates each snapshot key set. `testSstFilteringDisabledWhenDefragEnabled` starts a separate OM with both SST filtering and defrag intervals enabled and asserts SST filtering is not started.

## State and Persistence Behavior
The tests create real OM metadata, key table entries, snapshots, checkpoint directories, and RocksDB SST files. Filtering changes checkpoint file contents and updates `SnapshotInfo`'s filtered state. Service counters track how many active snapshot checkpoints have been processed.

## Dependencies and Integration Points
This file integrates OM protocol operations, key manager services, RocksDB flush/compaction behavior, snapshot manager checkpoint paths, snapshot metadata readers, and configuration gating between SST filtering and snapshot defrag.

## Risks and Edge Cases
- Tests depend on RocksDB file-level behavior and background service timing; waits use bounded polling.
- Random bucket selection in `testSstFilteringService` means key distribution varies, though expected sets are tracked.
- File deletion expectations distinguish level-0 from compacted files, which can be sensitive to RocksDB behavior changes.

## Test Signals
Passing means SST filtering removes irrelevant checkpoint SST files without losing visible keys, skips deleted snapshots appropriately, honors bootstrap locking, marks snapshots filtered, and is disabled when defrag service is enabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSstFilteringService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/defrag/TestInodeMetadataRocksDBCheckpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/defrag/TestInodeMetadataRocksDBCheckpoint.java

## Purpose
`TestInodeMetadataRocksDBCheckpoint` validates `InodeMetadataRocksDBCheckpoint`, which reads hard-link metadata and creates hard links for RocksDB checkpoint files, including paths prefixed with `om.db/`.

## Important APIs, Types, and Functions
- `InodeMetadataRocksDBCheckpoint(Path)` and `InodeMetadataRocksDBCheckpoint(Path, boolean deleteSourceFiles)` are constructed.
- A `hardLinkFile` in the checkpoint directory maps target paths to source paths separated by tabs.
- `IOUtils.getINode(Path)` verifies hard-link identity.

## Control Flow
The first test creates `source.sst`, writes a hardlink metadata file with one `om.db/target1.sst` target and one root-level `target2.sst` target, constructs the checkpoint wrapper, and asserts both targets exist and share the source inode. The second test constructs with `deleteSourceFiles=false`, verifies the source file remains, and checks that the `om.db/target.sst` link is created.

## State and Persistence Behavior
The tested behavior is filesystem-persistent: target links are created under the checkpoint directory, parent directories such as `om.db` must be created when needed, and source deletion is controlled by constructor argument/version mode.

## Dependencies and Integration Points
This test supports snapshot defrag/checkpoint code that stores inode metadata for SST hard links. It ensures compatibility with the newer `om.db/` path prefix and older source-preserving format.

## Risks and Edge Cases
- Hard-link behavior is filesystem-dependent.
- The tests do not cover malformed metadata rows, missing source files, duplicate targets, or delete-source true assertions.

## Test Signals
Passing means inode metadata checkpoint reconstruction creates expected hard links, handles `om.db/` target prefixes, and can preserve source files for v1-style metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/defrag/TestInodeMetadataRocksDBCheckpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/defrag/TestSnapshotDefragService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/defrag/TestSnapshotDefragService.java

## Purpose
`TestSnapshotDefragService` validates `SnapshotDefragService`, which builds compacted/defragmented snapshot DB versions, performs full or incremental defrag, ingests non-incremental tables, atomically switches snapshot DB versions, and updates metrics/locks.

## Important APIs, Types, and Functions
- `SnapshotDefragService.start`, `pause`, `resume`, `needsDefragmentation`, `performFullDefragmentation`, `ingestNonIncrementalTables`, `createCheckpoint`, `createDefragCheckpointMetadataManager`, `atomicSwitchSnapshotDB`, `performIncrementalDefragmentation`, `checkAndDefragSnapshot`, and `triggerSnapshotDefragOnce`.
- `OmSnapshotLocalDataManager.WritableOmSnapshotLocalDataProvider` and `OmSnapshotLocalData` store local version/defrag metadata.
- `DeltaFileComputer`/`CompositeDeltaDiffComputer`, `SstFileSetReader`, and `RDBSstFileWriter` provide incremental delta discovery and SST generation.
- `TablePrefixInfo`, `COLUMN_FAMILIES_TO_TRACK_IN_SNAPSHOT`, and OM DB table constants define table/prefix scope.
- OM locks `BOOTSTRAP_LOCK` and `SNAPSHOT_DB_CONTENT_LOCK` protect service passes and snapshot DB switching.

## Control Flow
Setup mocks OM, snapshot manager, local data manager, metadata manager, locks, metrics, performance metrics, and layout version manager. It constructs the service while intercepting `CompositeDeltaDiffComputer` so tests can control delta files. Basic lifecycle tests check start/pause/resume. `needsDefragmentation` tests cover already-defragmented and requires-defrag provider states. Full defrag filters incremental tables by bucket prefix and compacts only tracked tables. Non-incremental ingestion dumps matching prefix ranges from the original snapshot DB and loads them into checkpoint tables.

Checkpoint tests create real temporary checkpoint metadata managers, write table contents, and verify `createCheckpoint` preserves incremental table content while clearing non-incremental tables and avoids RocksDB metrics registration for transient defrag managers. `atomicSwitchSnapshotDB` verifies next-version path replacement, local data version increment, and returned old-version cleanup value.

Incremental defrag builds large synthetic table contents for two snapshots with update/insert/delete/same/absent/non-delta patterns, mocks delta SST files and key readers, captures generated SST writer operations, and verifies version-specific behavior: version 0 dumps all incremental tables, later versions directly ingest single-delta tables and merge/dump multi-delta tables. It also checks processed-delta metrics.

`checkAndDefragSnapshot` tests cover deleted snapshots, already-defragged snapshots, full/incremental failures, and successful active snapshot flows with precise ordering under `SNAPSHOT_DB_CONTENT_LOCK`: needs check, checkpoint, full/incremental defrag, non-incremental ingestion, checkpoint close, atomic switch, old checkpoint cleanup, and metrics/perf updates. `triggerSnapshotDefragOnceFailure` verifies outer failure metric handling under bootstrap lock.

## State and Persistence Behavior
The service manages durable snapshot DB directories and version metadata. Full defrag compacts table contents by bucket prefix in a checkpoint DB. Incremental defrag writes SST delta files and ingests them into checkpoint tables. Atomic switch replaces the next snapshot DB version path and updates local data metadata. Tests also ensure transient defrag checkpoint DBs do not register generic RocksDB metrics.

## Dependencies and Integration Points
This test integrates snapshot local data, snapshot chain traversal, OM metadata managers, table prefixing, RocksDB checkpoint managers, SST readers/writers, delta-file computation, lock ordering, native SST reader loading, snapshot metrics, and OM performance metrics.

## Risks and Edge Cases
- Heavy mocking means many tests validate service orchestration rather than real RocksDB compaction internals.
- Incremental defrag correctness depends on delta SST key streams including tombstones and table prefixes.
- Atomic switching must maintain lock ordering and close checkpoint managers before replacing paths; tests explicitly assert this order.
- Metrics are part of the behavior contract and can regress independently from data correctness.

## Test Signals
Passing gives strong coverage that snapshot defrag decides when work is needed, creates correct checkpoints, handles full and incremental modes, ingests tables, switches DB versions atomically under locks, cleans old versions, skips deleted/already-defragged snapshots, and records success/failure metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/defrag/TestSnapshotDefragService.java -->
