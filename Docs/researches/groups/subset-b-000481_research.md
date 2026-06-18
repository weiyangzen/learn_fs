# Research: subset-b-000481

Grouped research for Alluxio master block and file tests. Each section preserves the source path and is bounded by reconciliation markers for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterWorkerServiceHandlerTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterWorkerServiceHandlerTest.java

**Purpose:** Exercises `BlockMasterWorkerServiceHandler`, the gRPC-facing worker service wrapper around `BlockMaster`, with emphasis on register-lease enforcement and validation of duplicate block locations in register and heartbeat requests.

**Important APIs/types/functions:** The fixture creates `DefaultBlockMaster`, `MetricsMaster`, `MasterRegistry`, `ManualClock`, and `BlockMasterWorkerServiceHandler`. It builds `RegisterWorkerPRequest`, `BlockHeartbeatPRequest`, `LocationBlockIdListEntry`, `BlockIdList`, `BlockStoreLocationProto`, and `GetRegisterLeasePRequest` messages. Test methods cover `registerWorker`, `blockHeartbeat`, `tryAcquireRegisterLease`, and `releaseRegisterLease`.

**Control flow:** `before` calls `initServiceHandler(true)`, enabling one register lease with a 3s TTL and disabling JVM-space gating. `registerWithNoLeaseIsRejected` sends a valid-looking registration without acquiring a lease and records the observer error. `registerWorkerFailsOnDuplicateBlockLocation` creates two `LocationBlockIdListEntry` values with the same location key, acquires a lease sized to both lists, and expects an `AssertionError`. `registerLeaseExpired` acquires a lease, waits past TTL, lets another worker acquire the recycled lease, then verifies the original registration is rejected. `registerLeaseTurnedOff` rebuilds the handler with leases disabled and verifies registration succeeds without a lease. `workerHeartbeatFailsOnDuplicateBlockLocation` sends duplicate added-block locations in heartbeat and expects an assertion.

**State and persistence behavior:** Tests run against `NoopJournalSystem`; they validate in-memory lease table and worker/block registration behavior rather than durable journal recovery. The lease tests mutate global `Configuration` keys and live master state; teardown stops the registry.

**Dependencies and integration points:** Integrates gRPC proto request/response types, `StreamObserver`, Alluxio configuration, `RegisterLease`, `BlockStoreLocation`, and the master registry lifecycle. It verifies handler-level request validation before worker state reaches normal block metadata paths.

**Risks:** Uses `SleepUtils.sleepMs(5000)` for TTL expiry, so it is wall-clock-sensitive. Duplicate-location behavior is asserted as Java `AssertionError`, so behavior depends on assertions being enabled in the test runtime or on implementation throwing assertion errors explicitly. Global configuration mutations can leak if test isolation fails.

**Test signals:** Strong signals are rejection message containing "does not have a lease or the lease has expired", empty error queue when leases are disabled, and assertion failures for duplicate block location maps in both registration and heartbeat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterWorkerServiceHandlerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/ConcurrentBlockMasterTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/ConcurrentBlockMasterTest.java

**Purpose:** Stress-tests `DefaultBlockMaster` locking semantics under concurrent reader/writer and writer/writer races involving commit, remove, register, and heartbeat paths. It validates that concurrent operations expose only legal before/after states and that block metadata, worker usage, to-remove commands, and orphan handling remain consistent.

**Important APIs/types/functions:** Uses `SignalBlockMaster` to signal after `lockBlock`, `BlockMasterTestUtils.verifyBlockOnWorkers`, `verifyBlockNotExisting`, `findWorkerInfo`, `commitBlock`, `commitBlockInUFS`, `removeBlocks`, `workerRegister`, `workerHeartbeat`, `getBlockInfo`, and `getWorkerReport`. It also uses `Command`, `CommandType.Free`, `CommandType.Nothing`, `RegisterWorkerPOptions`, `WorkerInfo`, `BlockInfo`, and `BlockLocation`.

**Control flow:** The fixture starts a primary `SignalBlockMaster` with a two-thread master executor and a separate client executor. `concurrentWriterWithReaders` schedules 20 readers blocked on a latch; the writer releases the latch inside `lockBlock`. `concurrentWriterWithWriter` schedules a second writer blocked on the same signal, runs the first writer in the calling thread, then verifies final state. Commit races cover register of same/different blocks and same/different worker heartbeats. Remove races run with `deleteMetadata` true and false and cover new worker register, same worker heartbeat, different worker heartbeat, same block, and different block permutations.

**State and persistence behavior:** The tests use a `NoopJournalSystem`, so state is volatile. They intentionally observe transient states such as worker usage not being rectified until heartbeat, blocks with zero locations, metadata removed while worker usage remains, and deferred `Free` commands in workers' to-remove lists. The `ManuallyScheduleHeartbeat` class rule isolates lost-worker detection heartbeats.

**Dependencies and integration points:** Integrates block master with worker registration, worker reports, heartbeat command generation, worker storage accounting, protobuf metadata locations, and the lock path exposed by `DefaultBlockMaster.lockBlock`. It depends on `SignalBlockMaster` to turn internal lock acquisition into deterministic concurrency coordination.

**Risks:** Concurrency tests still depend on thread scheduling after latch release; failures may be intermittent if operations complete too quickly or executor behavior changes. Some assertions intentionally allow multiple legal outcomes, especially whether a heartbeat sees a `Free` command before or after to-remove list update. The tests assume lock ordering prevents deadlock while mixing block locks and worker metadata locks.

**Test signals:** Passing signals include zero uncaught throwables from concurrent tasks, expected worker counts and used-byte values, correct block location sets, `BlockInfoException` when metadata is removed, `FREE_BLOCK1_CMD` when a worker must free removed block 1, and `EMPTY_CMD` when no worker action is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/ConcurrentBlockMasterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/DefaultBlockMasterCheckpointTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/DefaultBlockMasterCheckpointTest.java

**Purpose:** Verifies `DefaultBlockMaster` checkpoint write and restore paths for both stream-based and directory-based checkpoint APIs, across heap and RocksDB-backed block metastores.

**Important APIs/types/functions:** Parameterizes over `MetastoreType.HEAP` and `MetastoreType.ROCKS`. Uses `writeToCheckpoint(OutputStream)`, `restoreFromCheckpoint(CheckpointInputStream)`, `writeToCheckpoint(File, ExecutorService)`, `restoreFromCheckpoint(File, ExecutorService)`, `processJournalEntry`, `getJournaledNextContainerId`, and `getBlockInfo`.

**Control flow:** `before` sets `MASTER_BLOCK_METASTORE`, constructs a fresh block master with block and inode store factories, replays journal entries for next container id, two block infos, and a delete for block 1. `testOutputStream` writes a checkpoint to a temp file, restores into a new master, and checks generator and block state. `testDirectory` performs the same validation through the asynchronous directory checkpoint API with a single-thread executor.

**State and persistence behavior:** This is a persistence-focused test. It confirms that checkpoint state includes the next container id and live block 2 length, but excludes deleted block 1. It verifies journal-derived in-memory state is serialized in a way compatible with both metastore implementations.

**Dependencies and integration points:** Uses `MasterTestUtils`, `MasterUtils.getBlockStoreFactory`, `MasterUtils.getInodeStoreFactory`, `NoopJournalSystem`, `MetricsMasterFactory`, checkpoint streams, and Alluxio journal protobuf entries.

**Risks:** Executor shutdown is not explicit in `testDirectory`, so future executor lifecycle changes could leave resource warnings. The test covers only a tiny block metadata set and one delete edge, not worker-location checkpointing or large checkpoints.

**Test signals:** Restored master reports `mNextContainerId`, throws `BlockInfoException` for deleted block 1, and returns block 2 with persisted length `mBlockLength`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/DefaultBlockMasterCheckpointTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/JvmSpaceReviewerTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/JvmSpaceReviewerTest.java

**Purpose:** Unit-tests `JvmSpaceReviewer`, which gates worker register leases based on estimated JVM memory available for processing a requested number of blocks.

**Important APIs/types/functions:** Uses `JvmSpaceReviewer.reviewLeaseRequest`, `JvmSpaceReviewer.BLOCK_COUNT_MULTIPLIER`, `Runtime.maxMemory/freeMemory/totalMemory`, and `GetRegisterLeasePRequest`.

**Control flow:** The test mocks runtime memory so available space is effectively 1000 bytes, computes `maxBlocks` from available bytes divided by `BLOCK_COUNT_MULTIPLIER`, and validates three requests: zero blocks accepted, exactly max accepted, max plus one rejected.

**State and persistence behavior:** Pure in-memory unit test with no master or journal state. It constructs unused metric gauges, but the active reviewer instance is driven by mocked `Runtime`.

**Dependencies and integration points:** Depends on Mockito, Dropwizard metric types, and Alluxio gRPC lease request messages. It represents the JVM-space branch used by `RegisterLeaseManager` when `MASTER_WORKER_REGISTER_LEASE_RESPECT_JVM_SPACE` is enabled.

**Risks:** The mocked `MetricRegistry` is not passed into the reviewer and may be vestigial; future reviewer implementation changes that use metrics could make this test incomplete. It validates only threshold boundaries and not negative/overflow memory values.

**Test signals:** `reviewLeaseRequest` returns true for zero and boundary block counts and false when requested blocks exceed estimated available memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/JvmSpaceReviewerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/RegisterLeaseManagerTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/RegisterLeaseManagerTest.java

**Purpose:** Verifies `RegisterLeaseManager` acquisition, reuse, release, expiration, capacity limits, and non-JVM lease behavior.

**Important APIs/types/functions:** Uses `RegisterLeaseManager.tryAcquireLease`, `hasLease`, `releaseLease`, `GetRegisterLeasePRequest`, `RegisterLease`, and configuration keys `MASTER_WORKER_REGISTER_LEASE_COUNT`, `MASTER_WORKER_REGISTER_LEASE_TTL`, and `MASTER_WORKER_REGISTER_LEASE_RESPECT_JVM_SPACE`.

**Control flow:** `before` configures two concurrent leases, 3s TTL, and disables JVM-space checks. `acquireVerifyRelease` acquires a lease for worker 1, observes `hasLease`, releases, and verifies absence. `recycleExpiredLease` fills both lease slots, sleeps beyond TTL, then verifies workers 3 and 4 can acquire recycled leases and worker 5 is blocked. `findExistingLease` verifies repeat acquisition by the same worker returns a present lease without consuming another slot.

**State and persistence behavior:** All state is in the manager's in-memory lease table; there is no journal persistence. Expiration is time-based and lazy, occurring on later acquisition checks.

**Dependencies and integration points:** Integrates Alluxio configuration and gRPC lease requests. It is the core unit counterpart to handler-level lease enforcement tests.

**Risks:** Uses 5s sleeps for a 3s TTL, making the test slower and potentially flaky under severe scheduling delays. It does not cover enabled JVM-space rejection, because that is delegated to `JvmSpaceReviewerTest`.

**Test signals:** Expected signals are present optionals for allowed acquisitions, `hasLease` matching live lease ownership, absent optional when capacity is exhausted, and expired worker leases removed after recycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/RegisterLeaseManagerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/SignalBlockMaster.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/SignalBlockMaster.java

**Purpose:** Test helper subclass of `DefaultBlockMaster` that emits a latch signal when a block lock is acquired, enabling deterministic race orchestration in block master concurrency tests.

**Important APIs/types/functions:** Extends `DefaultBlockMaster`, overrides package-private `lockBlock(long)`, returns `LockResource`, and exposes `setLatch(CountDownLatch)`. Constructors mirror the default master constructor variants used by tests.

**Control flow:** `lockBlock` delegates to `super.lockBlock(blockId)`, then calls `mLatch.countDown()` before returning the lock resource. Test code swaps latches before exercising a race, causing readers or second writers to proceed once the first operation has entered the protected section.

**State and persistence behavior:** Holds only a mutable `CountDownLatch` reference and does not change persistence. Its side effect is synchronization-only; it relies on `CountDownLatch` no-op behavior after reaching zero.

**Dependencies and integration points:** Integrates with `ConcurrentBlockMasterTest` and any test needing visibility into `DefaultBlockMaster` lock timing. It depends on package-private access to `lockBlock`, so it lives in the same package.

**Risks:** Because it signals after the lock is acquired but before the caller's operation completes, tests depend on exact internal call placement. If `DefaultBlockMaster` changes locking granularity, this helper may no longer synchronize at the intended point.

**Test signals:** There are no direct assertions in this helper. Its signal is observed indirectly when concurrent tests proceed and complete without deadlock or illegal state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/SignalBlockMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/meta/BlockContainerIdGeneratorTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/meta/BlockContainerIdGeneratorTest.java

**Purpose:** Unit-tests monotonic ID generation for `BlockContainerIdGenerator`.

**Important APIs/types/functions:** Uses `BlockContainerIdGenerator.getNewContainerId` and `setNextContainerId`.

**Control flow:** `before` creates a fresh generator. `getNewContainerId` asserts the default sequence starts at 0 and increments to 1 and 2. `setNextContainerId` resets next id to `TEST_ID` and verifies subsequent calls return `TEST_ID`, `TEST_ID + 1`, and `TEST_ID + 2`.

**State and persistence behavior:** Tests only in-memory next-id state. Persistence is covered indirectly by `DefaultBlockMasterCheckpointTest`, which verifies journaled next container id restoration.

**Dependencies and integration points:** Simple JUnit unit test with no master lifecycle. It guards a primitive used by block id/container allocation and journaling.

**Risks:** Does not test invalid reset values, overflow, concurrent access, or journal serialization. It assumes sequential single-threaded usage.

**Test signals:** Exact id sequence values demonstrate initial state and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/meta/BlockContainerIdGeneratorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/meta/MasterWorkerInfoTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/meta/MasterWorkerInfoTest.java

**Purpose:** Unit-tests `MasterWorkerInfo`, the master-side model for worker capacity, usage, storage tiers, block membership, remove queues, and wire report generation.

**Important APIs/types/functions:** Covers `register`, `getFreeBytesOnTiers`, `addBlock`, `removeBlockFromWorkerMeta`, `generateWorkerInfo`, `updateToRemovedBlock`, `updateUsedBytes(Map)`, and `updateUsedBytes(String,long)`. Uses `StorageTierAssoc`, `DefaultStorageTierAssoc`, `WorkerInfo`, `WorkerState`, and `GetWorkerReportOptions.WorkerInfoField.ALL`.

**Control flow:** `before` registers a worker with MEM and SSD tiers, total and used bytes, and blocks 1 and 2. Tests verify registration-derived totals, free bytes, re-registration returning removed blocks, tier-count validation exception text, add/remove block idempotency, wire report fields, to-remove block queue behavior, and usage recalculation by map or tier.

**State and persistence behavior:** The test mutates only the `MasterWorkerInfo` object. It verifies derived aggregate state such as total capacity, total used bytes, per-tier free bytes, current block set, and to-remove set. No journal or master registry is involved.

**Dependencies and integration points:** Integrates Alluxio constants, storage tier association, worker report options, and wire `WorkerInfo`. The object under test is consumed by `DefaultBlockMaster` worker reports and heartbeat command generation.

**Risks:** Does not cover concurrent updates even though worker metadata is accessed by concurrent master paths. It validates an exact exception message for tier mismatch, which can be brittle under wording changes.

**Test signals:** Expected signals include exact maps for total/used/free tier bytes, aggregate byte counts, removed block set after re-register, matching `WorkerInfo` fields, empty to-remove set after block removal, and updated used bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/meta/MasterWorkerInfoTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/AccessTimeUpdaterTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/AccessTimeUpdaterTest.java

**Purpose:** Tests `AccessTimeUpdater`, which updates inode access time immediately or asynchronously while respecting access-time precision and journal flush lifecycle.

**Important APIs/types/functions:** Uses `AccessTimeUpdater.updateAccessTime`, `start`, scheduler-driven flush, `InodeTree.createPath`, `LockedInodePath`, `JournalContext.append`, `FileSystemMaster.createJournalContext`, `ControllableScheduler.jumpAndExecute`, and journal `UpdateInode` entries.

**Control flow:** The fixture constructs a real `InodeTree`, `InodeStore`, `BlockMaster`, UFS-backed journal system, root inode, and mock `FileSystemMaster`. `updateAccessTimeImmediately` uses zero async interval and precision to verify immediate inode mutation and journal append. `updateAccessTimeAsync` verifies inode mutation happens immediately while journal append waits for flush interval. `updateAccessTimePrecision` and `updateAccessTimePrecisionAsync` verify small timestamp deltas are suppressed and large deltas are applied. `updateAccessTimeAsyncOnShutdown` stops the journal system and verifies pending async access time is flushed.

**State and persistence behavior:** Tests both inode-store state (`lastAccessTimeMs`) and journal persistence behavior (`UpdateInode` append). Async mode accumulates pending access-time updates and flushes them later through a master-created journal context or shutdown hook.

**Dependencies and integration points:** Integrates `JournalSystem`, `JournalTestUtils`, `NoopJournalContext`, `MountTable`, `InodeLockManager`, `InodeDirectoryIdGenerator`, permission configuration, Mockito captors, and a controllable executor/scheduler. This is a high-fidelity unit/integration test for metadata mutation and journaling.

**Risks:** Uses current wall-clock values for timestamps, so very small time assumptions could be sensitive if clock behavior changes. The test relies on mocked journal context identity (`when(journalContext.get()).thenReturn(journalContext)`) and on manual scheduler execution matching the updater's scheduled tasks.

**Test signals:** Captured journal entries must have `UpdateInode`, correct inode id, and expected access time. Inode store values must update only when precision allows, and mocked journal context must not receive early appends in async scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/AccessTimeUpdaterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemJournalEntryMergerTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemJournalEntryMergerTest.java

**Purpose:** Verifies `FileSystemJournalEntryMerger` compacts related file-system journal entries while preserving non-mergeable records and special directory fingerprint updates.

**Important APIs/types/functions:** Uses `FileSystemJournalEntryMerger.add`, `getMergedJournalEntries`, `clear`, and journal protobuf entries: `InodeFileEntry`, `UpdateInodeEntry`, `UpdateInodeFileEntry`, `InodeDirectoryEntry`, `UpdateInodeDirectoryEntry`, and `AddMountPointEntry`.

**Control flow:** The main test adds file creations, inode updates, file-length updates, directory creation/update/name update, and a mount point entry. It then asserts merged output order and merged fields: file 1 has updated length but original name/path, file 2 has updated name, independent update for id 3 remains, directory id 1 has updated name and loaded flag, and mount point remains. It clears the merger and verifies empty output. The fingerprint test verifies a directory creation plus normal directory updates can merge, but an `UpdateInode` with `ufsFingerprint` remains a separate entry.

**State and persistence behavior:** Tests only in-memory journal-entry merging, but this directly affects journal persistence volume and metadata-sync journal flushing. It confirms that compaction does not lose UFS fingerprint updates that cannot be folded into directory creation entries.

**Dependencies and integration points:** Depends on `BlockId.createBlockId`, `PersistenceState`, Alluxio URI construction, and journal protobuf builders. It integrates with metadata sync and filesystem master contexts that use `FileSystemMergeJournalContext`.

**Risks:** Assertions are position-based, so any intended output ordering change will require test updates. The unused `AlluxioURI uri` local suggests historical context but no active behavior.

**Test signals:** Expected merged list sizes and fields, retained mount entry, separate fingerprint update entry, and empty list after `clear`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemJournalEntryMergerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterFsOptsTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterFsOptsTest.java

**Purpose:** Broad parameterized suite for `FileSystemMaster` option semantics: create, delete, rename, get/list metadata loading, recursive operations, ACL mutation, read-only mounts, permissions, and existence checks across inode-store factories.

**Important APIs/types/functions:** Exercises `createFile`, `createDirectory`, `delete`, `rename`, `getFileInfo`, `getFileId`, `listStatus`, `setAttribute`, `setAcl`, `exists`, `mount`, and block-master heartbeat interactions after deletion. Uses contexts such as `CreateFileContext`, `DeleteContext`, `RenameContext`, `GetStatusContext`, `ListStatusContext`, `SetAclContext`, and proto options including `DeletePOptions`, `ListStatusPOptions`, `LoadMetadataPType`, `SetAclPOptions`, `SetAttributePOptions`, and `MountPOptions`.

**Control flow:** Early tests cover duplicate create, overwrite behavior, operation-time propagation, file deletion, recursive directory deletion, and alluxio-only deletion from mounted local UFS. Several recursive delete tests set modes and switch authenticated users to validate partial failure behavior: inaccessible children remain, accessible sibling subtrees are removed, and aggregate `FailedPreconditionException` messages include permission and directory-not-empty causes. Metadata-loading tests verify `getFileInfo` and `getFileId` load UFS entries, `listStatus` respects NEVER/ONCE/ALWAYS, and non-persisted directories become persisted when corresponding UFS children are loaded. Listing tests cover normal and recursive results plus permission-pruned recursive listing. Rename tests cover root restrictions, existing destinations, nonexistent parent, and subpath traversal. ACL tests cover default ACL rejection on files, directory default ACL replace/modify/remove, file ACL replace/modify/remove, recursive ACL propagation, and mask updates. `exists` verifies normal true/false plus access-control errors.

**State and persistence behavior:** Tests mutate full filesystem metadata state, UFS-backed temporary files, block metadata, inode edges, permission bits, ACL entries, mount table state, and worker removal commands. Deletion checks include inode/edge cleanup counts, block metadata removal, and worker heartbeat command suppression after removed-block notification.

**Dependencies and integration points:** Extends `FileSystemMasterTestBase`, integrates `BlockMaster`, local UFS paths, authentication resources, Alluxio permission model, inode store implementations, wire `FileInfo`, and block heartbeat command generation. It is a key cross-component regression suite.

**Risks:** Large suite with many scenarios shares fixture helpers and global auth/config state; ordering or cleanup bugs can cause cascading failures. Exact exception-message assertions are useful but brittle. Recursive delete intentionally allows partial deletion, so callers must understand non-atomic semantics.

**Test signals:** Signals include expected exceptions, invalid file ids after deletion, UFS files surviving alluxio-only deletes, exact path counts after metadata loading, list sizes and paths, ACL string-entry sets, worker heartbeat `Nothing` after deletion acknowledgement, and access-control exceptions from `exists`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterFsOptsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterMetricsTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterMetricsTest.java

**Purpose:** Verifies filesystem master metric gauges for pinned files, total paths, and root UFS capacity.

**Important APIs/types/functions:** Uses `DefaultFileSystemMaster.Metrics.registerGauges`, `MetricsSystem.METRIC_REGISTRY`, `MetricKey.MASTER_FILES_PINNED`, `MASTER_TOTAL_PATHS`, `CLUSTER_ROOT_UFS_CAPACITY_TOTAL`, `CLUSTER_ROOT_UFS_CAPACITY_USED`, and `CLUSTER_ROOT_UFS_CAPACITY_FREE`.

**Control flow:** `before` clears all metrics, mocks `UfsManager` and `InodeTree`, and registers gauges. Individual tests mock `getPinnedSize`, `getInodeCount`, and root UFS `getSpace` return values, then read gauge values by metric name.

**State and persistence behavior:** Pure metric-registration test with no persistence. It validates gauges are live views into mocked dependencies rather than stored constants.

**Dependencies and integration points:** Integrates MetricsSystem, UFS manager resource acquisition, `CloseableResource<UnderFileSystem>`, and Alluxio configuration for the root UFS path.

**Risks:** Gauge names are exact and global registry state must be cleared to avoid test pollution. It does not cover exception behavior if UFS resource acquisition or space calls fail.

**Test signals:** Gauge values equal mocked inode and UFS values: 100 pinned files, 90 total paths, and 1000/200/800 UFS total/used/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterMetricsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterOptionsTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterOptionsTest.java

**Purpose:** Minimal unit test for `FileSystemMasterOptions.completeFileDefaults`.

**Important APIs/types/functions:** Uses `FileSystemMasterOptions.completeFileDefaults` and gRPC `CompleteFilePOptions`.

**Control flow:** The single test obtains defaults, asserts the options object is non-null, and asserts `ufsLength` defaults to 0.

**State and persistence behavior:** No mutable state or persistence. It protects the default option contract used by complete-file operations.

**Dependencies and integration points:** Depends only on JUnit and Alluxio gRPC option type. It is a low-level guard for callers relying on implicit complete-file defaults.

**Risks:** Coverage is intentionally narrow and does not validate other default fields or interactions with complete-file logic.

**Test signals:** Non-null options and `getUfsLength() == 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterPartialListingTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterPartialListingTest.java

**Purpose:** Parameterized suite for partial `FileSystemMaster.listStatus` behavior with batch size, offset id, offset count, prefix, start-after, recursion, deletion, and rename interactions.

**Important APIs/types/functions:** Uses `listStatus` with `ListStatusPartialPOptions` wrapped in `ListStatusContext`, helper generators for prefix/startAfter/offsetCount/offsetId, `context.isTruncated`, `context.getTotalListings`, `delete`, and `rename`.

**Control flow:** The suite creates fixed path sets under root and nested directories, then checks sorted non-recursive listings, depth-first recursive listings, prefix filtering, start-after filtering, and partial paging. It validates offset-id and offset-count forms produce equivalent pages. Mutation tests delete or rename the inode referenced by an offset and verify listing either continues when the inode remains in the same directory or fails when the offset no longer exists under the listing root. Batch tests build 13 files and five nested levels to verify repeated page traversal, final empty page behavior, and total-listing counts.

**State and persistence behavior:** Tests file-system metadata state in `InodeStore` and path topology. It validates cursor stability against inode ids, path renames, and deletions. Recursive partial listings report `totalListings == -1`, while non-recursive listings report total counts.

**Dependencies and integration points:** Extends `FileSystemMasterTestBase`, parameterized by inode store factory. Integrates `DeleteContext`, `RenameContext`, `LoadMetadataPType.NEVER`, `FileInfo` ids/paths, and `InvalidPathException`/`FileDoesNotExistException` error paths.

**Risks:** Assertions encode specific sort and depth-first order; changes to listing order will break many tests. Cursor behavior is subtle: offset id is stronger but can fail after deletion, while startAfter is path-based. Large repetitive loops can obscure the exact failing page without good assertion output.

**Test signals:** Expected page sizes, exact ordered paths, truncation flags, total listings, exceptions for invalid offsets or prefixes, empty results after final page, and equivalence between offset count and offset id for stable listings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterPartialListingTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterS3UfsTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterS3UfsTest.java

**Purpose:** Integration-style test for `FileSystemMaster` metadata sync against an S3-compatible UFS provided by `S3ProxyRule`.

**Important APIs/types/functions:** Uses Alluxio S3 configuration keys, AWS `AmazonS3ClientBuilder`, `S3ProxyRule`, `mount`, `exists`, `MountContext`, and `ExistsContext`.

**Control flow:** `before` configures endpoint, region, path-style access, and credentials from the S3 proxy, creates a bucket, then delegates to the base filesystem master setup. `basicSync` mounts `s3://test-bucket/` at `/s3_mount`, writes an object via the AWS client, and asserts `mFileSystemMaster.exists` sees the mounted object. `basicWrite` is ignored because directory/file creation semantics require client-side data writes outside the master scope.

**State and persistence behavior:** Mutates a local S3 proxy bucket and the Alluxio mount table. The test validates metadata visibility rather than data persistence or file content.

**Dependencies and integration points:** Integrates Alluxio UFS S3 configuration, AWS SDK, S3Proxy, mount table, and filesystem master existence checks. It is sensitive to network port 8001 and local proxy lifecycle.

**Risks:** Fixed proxy port can collide with other processes. The test does not cover write/complete-file behavior, S3 directory marker semantics, credentials failure, or object deletion sync.

**Test signals:** After mounting and uploading `test_file`, `exists(/s3_mount/test_file)` returns true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterS3UfsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataConcurrentTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataConcurrentTest.java

**Purpose:** Tests concurrent metadata sync deduplication for `InodeSyncStream`, ensuring overlapping syncs are skipped or allowed according to path relationship, recursion, force/load flags, sync interval, cancellation, and `shouldSync`.

**Important APIs/types/functions:** Uses `InodeSyncStream.sync`, `SyncStatus.OK`, `SyncStatus.NOT_NEEDED`, `LockingScheme`, `UfsSyncPathCache` via `mFileSystemMaster.getSyncPathCache`, `DescendantType.ALL/ONE`, `FileSystemMasterCommonPOptions.syncIntervalMs`, and `CompletableFuture`.

**Control flow:** `before` enables `MASTER_METADATA_CONCURRENT_SYNC_DEDUP`, creates a 2-branch, 3-level UFS hierarchy, slows UFS operations, and confirms only root inode exists. Tests launch two sync streams with staggered futures. Same directory or parent/subdirectory overlaps are skipped when dedup applies; different directories sync concurrently. Sequential syncs can happen twice when intervals permit. Negative sync interval scenarios return `NOT_NEEDED`. A cancellation test cancels the second overlapping sync and then verifies a later sync is not deadlocked. `syncWhenShouldSyncIsSetTrue` constructs locking schemes with shouldSync true and verifies dedup does not suppress those syncs.

**State and persistence behavior:** Syncs load UFS directory hierarchy into inode metadata. Assertions compare inode counts, especially expected full tree size. Dedup state lives in sync-path cache and must be released after completion or cancellation.

**Dependencies and integration points:** Extends `FileSystemMasterSyncMetadataTestBase`, uses PowerMock for UFS factory preparation, a slow mock/test UFS, Alluxio locking scheme, sync path cache, and async execution.

**Risks:** Timing uses fixed sleeps of 10ms and 100ms around futures plus UFS slow time, so scheduling changes can affect overlap. Dedup semantics are complex and path relationship dependent. Cancellation behavior is critical for avoiding leaked sync-path locks.

**Test signals:** Expected `(OK, NOT_NEEDED)`, `(OK, OK)`, or `(NOT_NEEDED, NOT_NEEDED)` result pairs; inode count equals root-only, one-level loaded, or full expected tree as appropriate; post-cancellation sync returns OK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataConcurrentTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataFlushJournalTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataFlushJournalTest.java

**Purpose:** Verifies metadata sync journal merging/flushing behavior for hierarchical and flat UFS trees, including successful load/update/delete cycles and failure paths.

**Important APIs/types/functions:** Uses `InodeSyncStream.sync`, custom `TestInodeSyncStream`, `FileSystemMergeJournalContext`, `FileSystemJournalEntryMerger`, `MetadataSyncMergeJournalContext`, custom `TestJournalContext`, `LockingScheme`, `RpcContext`, `InternalOperationContext`, and `DescendantType.ALL`.

**Control flow:** `hierarchicalDirectory` and `flatDirectory` call `run` with different tree shapes. `run` creates UFS hierarchy, syncs it with a spying merge journal context, disables further appending/flushing after sync, verifies all metadata-sync journal mergers are empty, and checks inode counts and journal count bounds. It then recreates UFS with newer timestamps and expects delete/recreate-style file journal entries, then deletes all UFS content and expects Alluxio inode count to return to root. Failure tests inject failed UFS paths for a hierarchical child or root and validate failed sync status or thrown runtime while still flushing collected metadata-sync journals.

**State and persistence behavior:** Tests inode store population, direct-children-loaded flags for directories, completed flags for files, journal append accumulation, pending flush clearing, and exactly one flush per sync phase when pending entries exist. It explicitly verifies no metadata-sync merged journal entries remain after asynchronous writer flushing.

**Dependencies and integration points:** Extends `FileSystemMasterSyncMetadataTestBase`, uses PowerMock, Mockito spies, `UnderFileSystem` test hooks, journal protobuf entries, and master RPC contexts. It links `FileSystemJournalEntryMerger` behavior to real metadata sync.

**Risks:** Journal-entry count bounds are broad but still tied to implementation details such as access-time updates and directory journal sequence. Failure path for flat root expects a runtime exception, which can be sensitive to exception wrapping. Uses `Thread.sleep(1000)` to force timestamp differences.

**Test signals:** `SyncStatus.OK` for successful phases, `FAILED` or runtime on injected UFS failures, expected inode counts, directory loaded and file completed flags, appended journal counts within bounds, delete journal count equal to removed inodes, one flush count, and empty metadata-sync merger queues after sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataFlushJournalTest.java -->
