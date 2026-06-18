# Research: subset-b-000482

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataMetricsTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataMetricsTest.java

## Purpose
This PowerMock/JUnit test class validates metrics emitted by the legacy metadata sync path in `DefaultFileSystemMaster`, `InodeSyncStream`, `UfsStatusCache`, the instrumented metadata sync executors, and per-mount UFS operation counters. It extends `FileSystemMasterSyncMetadataTestBase`, which provides a real `DefaultFileSystemMaster` backed by a local `FlakyLocalUnderFileSystem` and static mocking of `UnderFileSystem.Factory`.

## Important APIs, Types, and Functions
- `metadataSyncMetrics()` constructs `InodeSyncStream` instances directly and asserts `DefaultFileSystemMaster.Metrics` counters for stream count, success, failure, skipped streams, changed/no-change paths, and per-path failures.
- `metadataPrefetchMetrics()` exercises `UfsStatusCache.prefetchChildren`, `fetchChildrenIfAbsent`, `remove`, and sync-time prefetch behavior through `InodeSyncStream`.
- `ufsStatusCacheSizeMetrics()` validates cache size counters for single statuses and children lists.
- `instrumentedThreadPool()` stresses `MetricKey.MASTER_METADATA_SYNC_EXECUTOR` and `MASTER_METADATA_SYNC_PREFETCH_EXECUTOR` meters under concurrent repeated syncs.
- `mountPointOpsCount()` reads a mount-specific counter from `MountTable.getUfsSyncMetric`.
- The test uses `AuthenticatedClientUser`, `UserState`, `MetricsSystem`, Dropwizard `Counter`/`Meter`, `LockingScheme`, `DescendantType`, and `FileSystemMasterCommonPOptions`.

## Control Flow
Setup delegates to the base fixture, then sets an authenticated user. The tests create local UFS directory/file hierarchies, run sync streams against `/` or individual paths, mutate UFS state, and compare metric deltas after each operation. Error coverage is driven by `FlakyLocalUnderFileSystem` flags that make `getStatus` or `listStatus` throw `IOException`, `RuntimeException`, or sleep.

`metadataPrefetchMetrics` first validates explicit cache prefetches, then invokes a full `InodeSyncStream` with prefetch enabled and checks aggregate prefetch counts. The concurrent tests use fixed thread pools; each worker repeatedly syncs a per-thread directory and checks monotonic executor meters before final exact total assertions.

## State and Persistence Behavior
The source file is test-only and does not persist production state directly. It observes state transitions in the inode tree, UFS status cache contents, and global `MetricsSystem` counters/meters. The base fixture uses a UFS journal, but this class focuses on in-memory metric side effects rather than replay.

## Dependencies and Integration Points
It integrates `DefaultFileSystemMaster` with `InodeSyncStream`, `UfsStatusCache`, `MountTable`, `InodeTree`, the absent-path cache, executor-service instrumentation, and the local UFS adapter. Static UFS factory mocking means the master under test always receives the base fixture's flaky UFS.

## Risks
- Several assertions depend on exact counter deltas and can fail when sync internals add or remove UFS calls.
- Global metrics state must be reset correctly; leakage from previous tests would invalidate exact counts.
- Concurrency tests assume executor meters increase promptly and monotonically, making them sensitive to instrumentation or scheduling changes.
- The `mIsSlow` retry check asserts only that retries are positive, so it detects retry presence but not retry policy quality.

## Test Signals
Strong regression signals include `SyncStatus.OK`, `NOT_NEEDED`, and `FAILED`; exact `INODE_SYNC_STREAM_*` counters; exact prefetch success/failure/cancel/path counts; cache size counters after add/replace/remove; executor submitted/completed totals; and per-mount UFS operation count totals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataMetricsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataTest.java

## Purpose
This PowerMock unit test covers user-facing `FileSystemMaster` metadata sync behavior for object-store mounts, fingerprint updates, owner/group propagation, alluxio-only deletes, and directory status lookups. It uses a custom `SyncAwareFileSystemMaster` to detect accidental sync calls in delete paths.

## Important APIs, Types, and Functions
- `completeFileWithOutOfDateHash()` verifies a completed through-written file keeps the complete-time content hash until a forced sync refreshes it from UFS fingerprint metadata.
- `setAttributeOwnerGroupOnMetadataUpdate()` ensures sync refreshes owner/group from updated `UfsFileStatus`.
- `listStatusWithSyncMetadataAndEmptyS3Owner()` verifies empty S3 owner/group values are replaced with mount parent owner/group when loading directories and files.
- `deleteAlluxioOnlyNoSync()` asserts recursive `alluxioOnly` delete avoids `syncMetadata`.
- `getStatusOnDirectory()` confirms `getFileInfo` on a directory does not recursively load children.
- `setupMockUfsS3Mount()` creates `/mnt/local` over a mocked `s3a://bucket/` UFS.
- `SyncAwareFileSystemMaster` overrides `syncMetadata` to record whether a sync happened.

## Control Flow
The fixture starts a metrics master, block master, and custom file system master with a mocked `UnderFileSystem` returned by static factory calls. Individual tests configure mock UFS status, fingerprint, existence, file/directory type, and listing responses. Operations then use `createFile`, `completeFile`, `listStatus`, `getFileInfo`, `delete`, and `mount` through the normal master API.

## State and Persistence Behavior
The tests use a UFS journal and temporary mount root. Restart behavior is not the focus here, but journal-backed service setup ensures operations follow production master initialization. Observable state includes inode fingerprints, owner/group fields, inode IDs, mocked UFS invocation counts, and a boolean flag proving whether `syncMetadata` was invoked.

## Dependencies and Integration Points
The class ties `DefaultFileSystemMaster` to `BlockMaster`, `MetricsMaster`, `JournalSystem`, mocked `UnderFileSystem`, S3 `Fingerprint`, `UfsFileStatus`, `UfsDirectoryStatus`, `MountContext`, `ListStatusContext`, `GetStatusContext`, and `DeleteContext`. It also uses `ManuallyScheduleHeartbeat` for persistence checker scheduler context.

## Risks
- Static factory mocking makes test order and cleanup important.
- Mocked object-store behavior may not capture all real S3 edge cases, especially fingerprint and owner/group defaults.
- Assertions around `getStatusOnDirectory` are negative Mockito verifications; additional legitimate UFS calls would require test updates.
- The alluxio-only delete guard relies on the custom subclass and could miss lower-level side effects outside `syncMetadata`.

## Test Signals
Key signals are fingerprint content hash changes after forced sync, owner/group equality, non-empty owner/group fallback for empty S3 metadata, invalid file IDs after alluxio-only delete, absence of sync invocation, and exact mocked `listStatus`/`getStatus` invocation counts for directory status calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataTestBase.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataTestBase.java

## Purpose
This base fixture supports metadata sync tests that need a real `DefaultFileSystemMaster` and a controllable local UFS. It centralizes temporary UFS setup, static UFS factory mocking, metric reset, master startup, UFS helpers, and a `FlakyLocalUnderFileSystem` implementation for failure injection.

## Important APIs, Types, and Functions
- `before()` reloads configuration, creates local UFS and journal directories, installs `UnderFileSystem.Factory.createWithRecorder` mocking, builds `MetricsMaster`, `BlockMaster`, and `DefaultFileSystemMaster`, starts the journal, gains primacy, starts the registry, and resets metrics.
- `after()` stops the registry and shuts down metadata sync executor services.
- `createUfsDir`, `createUfsFile`, and `cleanupUfs` provide direct UFS mutation helpers.
- `createUfsStatusWithName()` builds a synthetic `UfsFileStatus` for cache metric tests.
- `FlakyLocalUnderFileSystem` extends `LocalUnderFileSystem` and can throw `IOException`, throw `RuntimeException`, sleep, or fail selected path substrings from `getStatus` and `listStatus`.
- `createUfsHierarchy()` recursively creates mixed directory/file trees.

## Control Flow
Subclasses call `super.before()` to get a complete master environment. The base configures the root mount to point at the temporary UFS and enables `MASTER_METADATA_SYNC_INSTRUMENT_EXECUTOR`. It creates two executor services: one for the file system master and one for UFS status cache tests. UFS operations go through the same local UFS object that production code receives from the mocked factory.

## State and Persistence Behavior
The fixture uses a UFS-backed journal and starts the journal in primary mode. It does not test replay itself, but it gives each test a fresh temporary root, inode tree, master registry, and reset metric namespace. The flaky UFS mutable flags are shared state that tests must reset when changing failure modes.

## Dependencies and Integration Points
It integrates Alluxio configuration, journal test utilities, master registry, metrics master, block master, file system master, local UFS, PowerMockito static mocking, and path utilities. Subclasses rely on protected fields such as `mFileSystemMaster`, `mInodeTree`, `mUfs`, and executor services.

## Risks
- Static mocking of `UnderFileSystem.Factory` can affect other tests if setup/teardown fails.
- `FlakyLocalUnderFileSystem` throws generic `RuntimeException` for path failures, which is useful for broad failure paths but not fine-grained exception semantics.
- Slow UFS injection uses real sleep, which can make tests sensitive to timing and timeouts.
- `after()` shuts down executor services but does not await termination.

## Test Signals
This file is a fixture, so signals appear in subclasses: successful registry startup, inode-tree population, metrics reset, controlled UFS failures, and deterministic temporary UFS hierarchy construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncMetadataTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncTest.java

## Purpose
This test class validates legacy `FileSystemMaster.syncMetadata` cache and invalidation semantics. It focuses on `UfsSyncPathCache` decisions, sync timestamps for different `DescendantType` values, deletion propagation from UFS, and explicit invalidation through `needsSync`.

## Important APIs, Types, and Functions
- `createSyncStream()` wraps `mFileSystemMaster.syncMetadata(createRpcContext(), path, options, descendantType, null, null)`.
- `syncSetup()` mounts a temporary UFS directory and replaces the test clock with a mutable `Long[]`.
- `checkSyncTime()` and `checkNeedsSync()` inspect `getSyncPathCache().shouldSyncPath`.
- Tests cover `syncDelete`, `syncDir`, `syncDirChild`, `syncNestedFileChild`, `syncNestedFile`, `syncDeletion`, and `syncInvalidation`.

## Control Flow
Each test mounts `/mount`, creates files/directories through the master using cache-through write options, advances the mocked clock, calls sync with interval and descendant parameters, and checks whether sync is `OK` or `NOT_NEEDED`. Some tests delete files directly from UFS via `deleteFileOutsideOfAlluxio`, while invalidation tests call `mFileSystemMaster.needsSync`.

## State and Persistence Behavior
The central state is the sync path cache, which stores sync times separately for direct/self and recursive descendant coverage. The tests assert cache timestamps for files, directories, and parents after recursive syncs, partial syncs, child refreshes, deletions, and invalidations. File existence is checked through the inode tree after UFS deletion syncs.

## Dependencies and Integration Points
The class extends `FileSystemMasterTestBase`, using its file creation, block completion, temporary UFS, mock clock, and master services. It uses `DescendantType`, `FileSystemMasterCommonPOptions.syncIntervalMs`, `SyncCheck`, create/delete/get-status contexts, and local UFS path deletion.

## Risks
- Time-dependent assertions rely on the mocked clock being used consistently by the sync cache.
- Descendant-type semantics are subtle: files can satisfy broader descendant coverage differently from directories.
- The `syncNestedFileChild` test disables permission checks because ACL fetches can alter skip behavior, so permission-enabled behavior is not covered here.
- Exact cache timestamp expectations can break with legitimate cache algorithm changes.

## Test Signals
Strong signals are `SyncStatus.OK` versus `NOT_NEEDED`, `FileDoesNotExistException` after UFS-side deletion, exact last sync times returned by `shouldSyncPath`, and parent timestamp behavior when one child was already fresh while siblings needed sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterSyncTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterTest.java

## Purpose
This large parameterized unit test covers broad `FileSystemMaster` behavior: path creation, recursive delete against persisted UFS trees, ID/path lookup, block info, ACL/default ACL rules, TTL delete/free, attribute mutation, free semantics, mount/unmount validation, worker heartbeat integration, lost-file detection, UFS info lookup, fingerprint persistence, invalid UFS file filtering, persistence propagation, xAttr update/propagation, read-only write denial, recursive journal flushing, and `exists` with sync/no-sync contexts.

## Important APIs, Types, and Functions
- Parameterization runs the suite with `MASTER_FILE_SYSTEM_MERGE_INODE_JOURNALS` disabled and enabled, with forced flush max entries set to zero in the merged-journal case.
- Persistent delete helpers exercise `delete` with `DeletePOptions.recursive`, `alluxioOnly`, and `unchecked`.
- TTL tests use `HeartbeatScheduler.execute(HeartbeatContext.MASTER_TTL_CHECK)` and `TtlAction.FREE`.
- Free tests call `mFileSystemMaster.free` and verify block removal through `BlockMaster.workerHeartbeat`.
- Mount tests cover read-only mounts, shadow mounts, prefix/suffix UFS mount rejection, unmount behavior, and root/non-mount errors.
- `RecursiveDeleteForceFlushJournals()` spies `createJournalContext(true)` to count flushes and closes.
- xAttr tests cover `TRUNCATE`, `UNION_REPLACE`, `UNION_PRESERVE`, `DELETE_KEYS`, and creation-time propagation via `XAttrPropagationStrategy.NEW_PATHS` or `LEAF_NODE`.

## Control Flow
The test suite builds on `FileSystemMasterTestBase`. Most tests create an Alluxio tree, optionally mirror or mutate UFS state, call a master API, and then inspect `FileInfo`, inode IDs, UFS filesystem paths, block locations, journal replay after `stopServices`/`startServices`, or thrown exceptions. The mounted persisted directory tests construct a deterministic UFS tree, load it into Alluxio, introduce synced or unsynced entries, and assert what remains after delete.

## State and Persistence Behavior
Persistent state coverage is substantial. Restart/replay is tested for TTL delete/free, UFS fingerprint updates, and persistence propagation. Recursive delete tests verify UFS files/directories and Alluxio inode IDs are removed consistently. TTL free keeps metadata but removes block locations. Lost-file detection changes persistence state from `NOT_PERSISTED` to `LOST`. Journal flush behavior is checked under merged inode journals.

## Dependencies and Integration Points
The class integrates `DefaultFileSystemMaster` with block master state, worker heartbeats, journal contexts, UFS mounts, local filesystem temp paths, ACL authorization, TTL heartbeat scheduling, metrics/test registry setup, `FileSystemOptionsUtils`, protobuf options, and wire types such as `FileInfo`, `FileBlockInfo`, `FileSystemCommand`, and `UfsInfo`.

## Risks
- Because the class is broad, failures can arise from shared fixture assumptions rather than the API under direct test.
- Parameterized journal behavior means tests must be valid in both merged and unmerged journal modes.
- TTL and worker heartbeat tests depend on manual heartbeat execution and block-master state synchronization.
- Recursive delete tests mix Alluxio metadata deletion with real local filesystem deletion and can be sensitive to UFS sync-check semantics.
- Some tests use deprecated `ExpectedException` style and may stop at first expected failure, leaving later assertions unreachable by design.

## Test Signals
Signals include exact inode existence/invalid ID checks, `FileInfo` field values, thrown `AccessControlException`, `InvalidPathException`, `UnexpectedAlluxioException`, `FileDoesNotExistException`, block location counts, worker heartbeat command types, UFS path existence, replayed metadata after restart, xAttr map contents, ACL entries, and flush/close counts in recursive journal deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterTestBase.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterTestBase.java

## Purpose
This shared fixture constructs a reusable in-process Alluxio master stack for file system master tests. It supplies common URIs, temporary UFS and journal roots, parameterized inode store factories, worker registration, block commit helpers, persisted-directory helpers, and service lifecycle management.

## Important APIs, Types, and Functions
- Static URI constants define common root, nested file, nested directory, and mount paths.
- `parameters()` provides heap, Rocks, and caching inode store factories for tests that use this base parameterization.
- `before()` configures the mock clock, resets group cache and metrics, creates the journal folder, and calls `startServices`.
- `startServices()` builds `MasterRegistry`, `JournalSystem`, `MetricsMaster`, `BlockMaster`, and a `DefaultFileSystemMaster` whose sync process is a `TestSyncProcessor`.
- `createFileWithSingleBlock()` creates a file, allocates a block, creates a UFS file for cache-through/through/async-through writes, commits a block to worker 1, and completes the file.
- Persisted-directory helpers build, load, mount, and verify deterministic local UFS directory trees.
- `stopServices()` stops registry, journal, and file master services.

## Control Flow
Tests using this base start with global configuration rules for UFS journaling, umask, work dir, root UFS, and retry-cache disabling. `startServices` registers two workers with memory and SSD tiers. Helper methods create local UFS trees through Java NIO, load metadata through `listStatus(... LoadMetadataPType.ALWAYS)`, and compare both UFS filesystem state and Alluxio inode IDs.

## State and Persistence Behavior
The fixture is explicitly journal-backed and supports simulated restarts by calling `stopServices` and `startServices` while retaining the same journal folder. It tracks `mInodeTree`, `mInodeStore`, `mBlockMaster`, worker IDs, metrics, and a mock clock. The file creation helper updates both inode metadata and block metadata, and may create persisted UFS files depending on write type.

## Dependencies and Integration Points
It integrates Alluxio configuration/test directory utilities, authentication rules, manual heartbeat rules, TTL interval rules, journal test utilities, heap/Rocks/caching inode stores, block metadata stores, metrics master, block master, file master, local filesystem paths, worker registration protobufs, and `TestSyncProcessor`.

## Risks
- Shared mutable fixture fields make test isolation dependent on correct `before`/`after` execution.
- `stopServices()` calls multiple stop/close methods and can mask lifecycle ordering assumptions in subclasses.
- The Rocks inode store parameter uses a shared directory per `parameters()` invocation, which may need care if tests are parallelized.
- The helper creates UFS files for certain write types but not file content, so tests should not infer data contents.

## Test Signals
The file itself is fixture code; downstream tests signal through successful master startup, registered worker IDs, deterministic block IDs/locations, replayable journal state, loaded persisted directories, and helper assertions for UFS/inode deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMasterTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMetadataSyncV2BenchmarkTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMetadataSyncV2BenchmarkTest.java

## Purpose
This ignored benchmark/debug test compares metadata sync V2 against legacy V1 loading on a large local UFS tree. It is not intended as a normal unit test; it requires pre-generated files under a hard-coded `/tmp/s3-test-files/bucket` layout.

## Important APIs, Types, and Functions
- Class-level `@Ignore` disables the benchmark by default.
- `syncV2()` mounts `file:///tmp/s3-test-files/bucket/0/0/0/0` at `/local_mount`, runs `getMetadataSyncer().syncPath` with `DescendantType.ALL` and `DirectoryLoadType.BFS`, waits indefinitely, and prints task stats twice.
- `syncV1()` mounts the same path, calls `listStatus` with recursive `LoadMetadataPType.ALWAYS`, and prints elapsed time.
- `generateTestFiles()` is separately ignored and writes a large nested tree of small files for benchmark input.
- `listSync()` builds the V1 recursive list context with `syncIntervalMs(0)`.

## Control Flow
The benchmark extends `FileSystemMasterTestBase`, mounts the configured local UFS path, and then either invokes V2 sync directly or V1 metadata loading through list status. The file generator uses nested loops to create paths like `/tmp/s3-test-files/bucket/i/j/k/l/n/fm` and logs every 10,000 files.

## State and Persistence Behavior
This test creates and reads real local filesystem data outside the repository under `/tmp`. It does not assert replay behavior and prints performance data rather than checking exact state, though it uses the normal master fixture and journal-backed setup from the base class.

## Dependencies and Integration Points
It depends on the local filesystem, Apache Commons `FileUtils`, `DefaultFileSystemMaster` metadata sync V2, legacy `listStatus` metadata loading, `MountContext`, and file master contexts. The benchmark assumes the Alluxio local UFS adapter can access the hard-coded path.

## Risks
- Hard-coded `/tmp` paths and huge file counts make accidental execution expensive.
- The test uses `System.out` timing/stats instead of assertions.
- `syncV2` hardcodes `DirectoryLoadType.BFS`, so it does not compare all V2 modes.
- Generated data volume is large enough to affect disk usage and local performance.

## Test Signals
Because the class is ignored, signals are manual: printed `TaskStats` from V2 first/second pass and elapsed milliseconds from V1 recursive list status. It is best treated as a local profiling tool, not a CI regression test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMetadataSyncV2BenchmarkTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMetadataSyncV2Test.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMetadataSyncV2Test.java

## Purpose
This parameterized test suite validates metadata sync V2 against S3-style object storage across `DirectoryLoadType.SINGLE_LISTING`, `BFS`, and `DFS`. It checks listing depth, create/noop/delete/recreate operations, non-persisted inode handling, mount-prefix behavior, directory-loaded markers, UFS failures, processing failures, concurrent master modifications, absent-path caching, and `startAfter` pagination.

## Important APIs, Types, and Functions
- `syncPath(path, DescendantType, DirectoryLoadType, interval[, startAfter, descendants])` is exercised through `mFileSystemMaster.getMetadataSyncer()`.
- `BaseTask.waitComplete`, `BaseTask.succeeded`, `TaskInfo`, `TaskStats`, `SyncOperation`, and `SyncFailReason` provide validation points.
- `asyncListingOperations()` directly uses `UfsClient.performListingAsync`.
- `listAsync()` resolves mount table entries and acquires UFS resources.
- Tests use `checkUfsMatches`, `assertSyncOperations`, and `assertSyncFailureReason` from `MetadataSyncV2TestBase`.
- `TestSyncProcessor` hooks inject processing errors and block at selected sync operations for concurrency tests.

## Control Flow
Most tests mount `s3://alluxio-mdsync-test-bucket/` at `/s3_mount`, create S3 objects through the mock S3 client, run sync with a descendant depth and directory load type, wait for task completion, assert operation counts, and compare Alluxio namespace to S3 listing. Tests then mutate S3 or Alluxio-only state and run another sync to verify noop, delete, recreate, skip, or failure behavior.

The suite covers single object sync, directory sync, nested mount prefixes, directory markers, empty directories, large paginated listings, recursive nested object trees, non-S3 directory deletion, S3 fingerprint changes, mount-point descendant-none noops, missing UFS paths, unmount during sync, concurrent delete/create, and start-after filtering for relative and absolute paths.

## State and Persistence Behavior
The suite observes inode tree changes, `isDirectChildrenLoaded` flags, absent path cache entries, file completion state, S3-derived fingerprints, and non-persisted Alluxio-only inodes that must survive sync. It does not focus on journal replay; it validates live namespace reconciliation between UFS and Alluxio.

## Dependencies and Integration Points
It extends `MetadataSyncV2TestBase`, which supplies S3Proxy, AWS SDK v1/v2 clients, no-sync/list-sync contexts, tiny UFS listing page size, and Alluxio master setup. It integrates `MountTable`, `UfsClient`, `UnderFileSystem`, `DefaultSyncProcess`, `TestSyncProcessor`, `CompletableFuture`, `SynchronousQueue`, create/delete/exists contexts, and S3 object APIs.

## Risks
- Exact `SyncOperation` counts vary by `DirectoryLoadType`, so mode-specific behavior can regress independently.
- S3Proxy behavior differs from real S3 in some edge cases; one test documents a mock-server 403 when `startAfter` exceeds the last key.
- Concurrency tests rely on deterministic `TestSyncProcessor` blocking points.
- Non-persisted skip logic is subtle and protects Alluxio-only files/directories from UFS-driven deletion.
- `isDirectChildrenLoaded` assertions encode cache/loading semantics that may change with sync algorithm refactors.

## Test Signals
Signals include exact operation maps for `CREATE`, `NOOP`, `DELETE`, `RECREATE`, `SKIPPED_NON_PERSISTED`, and `SKIPPED_DUE_TO_CONCURRENT_MODIFICATION`; failure reasons such as `LOADING_UFS_IO_FAILURE`, `PROCESSING_UNKNOWN`, `PROCESSING_CONCURRENT_UPDATE_DURING_SYNC`, and mount-point-not-found reasons; namespace equality with S3; direct-children-loaded flags; absent path cache entries; and list sizes after `startAfter` syncs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemMetadataSyncV2Test.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncDepthV2Test.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncDepthV2Test.java

## Purpose
This parameterized V2 sync test isolates descendant-depth behavior for syncing a single directory, nested directory, or single file. It runs every combination of `DirectoryLoadType.SINGLE_LISTING`, `BFS`, `DFS` and `DescendantType.ALL`, `ONE`, `NONE`.

## Important APIs, Types, and Functions
- `data()` defines the 3-by-3 load-type/depth matrix.
- Constructor stores `mDirectoryLoadType` and `mDescendantType`.
- `syncSingleDir()` syncs a directory marker and verifies second-pass noops without marking the mount point as direct-children-loaded.
- `syncSingleDirNested()` syncs a nested directory, deletes it, validates parent deletion behavior, then syncs the mount root.
- `syncSingleFile()` syncs a nested file, handles content modification as `RECREATE`, then deletes and syncs the root with depth-dependent deletion expectations.

## Control Flow
Each test mounts the S3 bucket, writes an object or directory marker, calls `syncPath` on the target path with the current parameterized depth/load type, waits for the `BaseTask`, and verifies operation counts. Follow-up syncs exercise idempotence, deletion, and mount-root reload semantics.

## State and Persistence Behavior
The suite observes inode creation/deletion, content hash driven recreation, direct-children-loaded flags on the mount point, and whether a nested file remains when the root is synced with `DescendantType.NONE`. It validates live metadata state rather than journal replay.

## Dependencies and Integration Points
It extends `MetadataSyncV2TestBase` and uses S3Proxy-backed clients, `MountContext`, `BaseTask`, `SyncOperation`, no-sync `getFileInfo`, and `checkUfsMatches`. It directly depends on V2 syncer's interpretation of descendant depth for object-store listings.

## Risks
- Depth semantics are easy to regress: `NONE` must sync only the path itself, while `ONE` and `ALL` affect deletion of descendants differently.
- Directory marker handling and inferred parent directories can differ by UFS implementation.
- The operation counts intentionally vary based on depth and must be updated if V2 task accounting changes.

## Test Signals
Signals are exact operation counts, task success, `exists` result for the deleted nested file under `DescendantType.NONE`, mount point `isDirectChildrenLoaded` flags, and full UFS/Alluxio namespace equality after root syncs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncDepthV2Test.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncLockManagerTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncLockManagerTest.java

## Purpose
This unit test validates `MetadataSyncLockManager` path locking, invalid path rejection, lock-pool garbage collection, URI normalization, and ancestor/descendant concurrency blocking.

## Important APIs, Types, and Functions
- `setup()` reloads configuration and sets metadata sync lock pool initial size, low watermark, and high watermark to zero for deterministic garbage collection.
- `lookPoolGC()` acquires locks for `/a/b/c/d` and `/e`, checks pool size, closes locks, and waits for unused locks to be recycled.
- `invalidPath()` asserts malformed paths throw `InvalidPathException`.
- `concurrentLock()` checks independent, same, sibling, descendant, duplicate slash, and `alluxio://` normalized path cases.
- `metadataSyncLockTest()` acquires one path lock, asynchronously attempts a second lock, and uses a timeout to detect expected blocking.

## Control Flow
The test creates a `MetadataSyncLockManager`, acquires `MetadataSyncPathList` instances through `lockPath`, and closes them with try-with-resources or explicit `close`. Blocking behavior is detected by `CompletableFuture.get(200ms)`; if it times out while blocking is expected, the held lock is released and the future must complete.

## State and Persistence Behavior
The lock manager maintains an in-memory lock pool. This test checks that pool size grows with path components and shrinks to zero when watermarks are configured to zero and locks are closed. No persistent state is involved.

## Dependencies and Integration Points
It uses Alluxio path parsing via `AlluxioURI`, configuration keys for lock pool sizing, `CommonUtils.waitFor`, `InvalidPathException`, Java `Closeable`, `CompletableFuture`, and timeout-based concurrency checks.

## Risks
- Timeout-based blocking detection can be sensitive to heavily loaded test environments.
- The test name `lookPoolGC` appears to mean lock-pool GC, but the behavior is clear.
- Invalid path coverage is narrow and focused on whitespace/non-absolute examples.
- Exact pool size expectations encode the lock manager's path-component allocation model.

## Test Signals
Signals are pool-size counts after lock acquisition/release, thrown `InvalidPathException`, whether a second path lock completes within 200ms, and successful completion after the first lock is closed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncLockManagerTest.java -->
