# subset-b-000483 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncMultiMountV2Test.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncMultiMountV2Test.java

## Purpose
Parameterized JUnit coverage for Metadata Sync V2 across multiple Alluxio mount boundaries, especially S3/object-store mounts nested under local root and under other S3 mounts. It validates that metadata sync keeps mount-point inodes authoritative, creates only visible UFS-backed children, and skips UFS entries that would shadow Alluxio mount points.

## Important APIs/types/functions
- Extends `MetadataSyncV2TestBase`, using its S3 proxy buckets, mount constants, no-sync contexts, and `assertSyncOperations`.
- Constructor and `data()` run each test with `DirectoryLoadType.SINGLE_LISTING`, `BFS`, and `DFS`.
- Calls `mFileSystemMaster.mount`, `createDirectory`, `getMetadataSyncer().syncPath`, `listStatus`, `exists`, and `getFileInfo`.
- Asserts `TaskGroup` behavior via `waitAllComplete`, `allSucceeded`, `getTaskCount`, and sync stats for `CREATE`, `NOOP`, and `SKIPPED_ON_MOUNT_POINT`.

## Control flow
- Each test constructs UFS/S3 state, triggers `syncPath` from `/` with `DescendantType.ONE` or `ALL`, waits for completion, then inspects sync stats and resulting inode visibility.
- `syncNonS3DirectoryShadowingMountPoint` creates a local UFS file named like the S3 mount and verifies root sync skips it.
- `syncNestedS3Mount` mounts two buckets and verifies both mount subtrees are traversed without rewriting mount-point inodes.
- `syncNestedS3MountShadowingMountPoint` verifies S3 objects under a path that is itself a nested mount are hidden/skipped while unrelated objects are created.
- `syncS3NestedMountLocalFs` first syncs only one level, then all descendants, showing nested mount tasks are deferred until recursive sync.

## State and persistence behavior
- Uses real `DefaultFileSystemMaster` metadata state from the test base and transient S3Proxy buckets.
- Mount table entries are treated as persistent Alluxio namespace boundaries; UFS entries at matching paths must not overwrite mount-point directory/file metadata.
- Assertions use no-sync contexts afterward so test observations reflect the explicit sync task rather than implicit metadata loading.

## Dependencies and integration points
- Integrates file master mount table resolution, MetadataSyncer V2, `TaskGroup`, S3 UFS client behavior, and `FileInfo` mount-point attributes.
- Depends on AlluxioURI path joining and on object-store pseudo-directory semantics for keys like `d/f1`.

## Risks and edge cases
- Expected skipped counts differ by `DirectoryLoadType` in the shadowing S3 case, making the test sensitive to traversal implementation.
- A stray `System.out.println` of task stats in one test is diagnostic noise and may be undesirable in large test suites.
- Tests assume deterministic inode counts from recursive list output and stable pseudo-directory creation.

## Test signals
- Strong signal for mount-shadow correctness and recursive sync task partitioning across local and S3 mounts.
- Regression indicators: unexpected `CREATE` for mount-point-shadowed entries, missing nested S3 children, or changed task count for root plus nested mount sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncMultiMountV2Test.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncNonObjectStoreV2Test.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncNonObjectStoreV2Test.java

## Purpose
Parameterized unit/integration tests for Metadata Sync V2 on non-object-store UFS roots, mainly local filesystem mounts. The class verifies basic create/noop/update semantics for empty directories, files, nested directories, and fingerprint changes.

## Important APIs/types/functions
- Extends `FileSystemMasterTestBase` directly and imports helper methods from `MetadataSyncV2TestBase`.
- Parameterized over `DirectoryLoadType.SINGLE_LISTING`, `BFS`, and `DFS`.
- Uses `mFileSystemMaster.getMountTable().resolve("/")` to find local UFS root, creates Java `File` entries, then calls `getMetadataSyncer().syncPath`.
- Uses `BaseTask` and `TaskInfo` stats rather than `TaskGroup` aggregation.

## Control flow
- `syncEmptyDirectory` creates a UFS-only directory, syncs `/`, asserts one `CREATE`, then repeats and expects one `NOOP`.
- `syncNonS3DirectorySync` builds a local UFS tree and syncs targeted paths with `DescendantType.NONE`, `ONE`, and `ALL`, checking how many entries are created or nooped at each scope.
- `testNonS3Fingerprint` creates a directory through Alluxio, deletes only Alluxio metadata, recreates it as cache-only with a different mode, and syncs root to validate an `UPDATE`.

## State and persistence behavior
- Exercises local UFS metadata as the source of truth and Alluxio inode metadata as the sink.
- The fingerprint test explicitly separates UFS persistence from Alluxio metadata by using `DeletePOptions.setAlluxioOnly(true)` and `WriteType.MUST_CACHE`, then expects sync to reconcile the inode.
- Uses `existsNoSync` after sync to avoid implicit metadata refresh.

## Dependencies and integration points
- Ties local `java.io.File` state to file master metadata loading.
- Uses create/delete contexts, grpc options, and `Mode` to shape inode metadata before sync.
- Shares operation-count assertions with the S3 metadata sync suite.

## Risks and edge cases
- Contains a TODO noting root inode `NOOP` counting for descendant syncs may be unintuitive; future stat changes can break these assertions.
- Directory load type differences are abstracted by expecting identical operation counts, so traversal-specific regressions surface quickly.

## Test signals
- Good signal for non-object-store metadata sync correctness, especially idempotency and fingerprint-driven updates.
- Regression indicators: repeated sync produces `CREATE`, descendant scope changes operation counts unexpectedly, or cache-only recreated directory is not updated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncNonObjectStoreV2Test.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncV2TestBase.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncV2TestBase.java

## Purpose
Shared base class for Metadata Sync V2 tests that need S3-compatible UFS mounts. It configures S3Proxy or real S3 clients, exposes common bucket/mount constants, provides no-sync/list-sync contexts, and centralizes sync-stat and UFS-vs-Alluxio comparison helpers.

## Important APIs/types/functions
- Extends `FileSystemMasterTestBase`.
- Defines bucket constants, mount URI constants, test content strings, and `TIMEOUT_MS`.
- JUnit `@Rule` `S3ProxyRule` supplies transient S3-compatible object storage.
- `before()` configures S3 properties and creates two buckets; `after()` shuts clients and proxy down.
- Context helpers: `listSync`, `listNoSync`, `getNoSync`, static `existsNoSync`.
- S3 lifecycle helpers: `stopS3Server`, `startS3Server` use reflection into `S3ProxyRule`.
- Validation helpers: `checkUfsMatches`, `listUfsPath`, `assertSyncOperations` overloads, and `assertSyncFailureReason`.

## Control flow
- Setup branches on `mUseRealS3`: real AWS clients or local S3Proxy endpoint with path-style access and configured Alluxio S3 keys.
- `checkUfsMatches` does stack-based traversal: list Alluxio children without sync, list S3 children/prefixes with delimiter, compare normalized paths, and push directories for further checking.
- `listUfsPath` pages S3 `ListObjectsV2`, merges common prefixes and objects, filters descendants, sorts/distincts, and maps S3 keys to Alluxio paths.
- `assertSyncOperations(TaskGroup)` aggregates per-task atomic operation counters before comparing all enum counts, including zero-default operations.

## State and persistence behavior
- Manages external S3Proxy server resources and AWS SDK v1/v2 clients.
- Uses configuration global state for S3 endpoints, region, DNS bucket behavior, and listing length.
- Disables permission authorization to focus on metadata sync behavior.

## Dependencies and integration points
- Integrates Alluxio configuration, S3Proxy, AWS SDK v1 and v2, Alluxio file master contexts, path utilities, and mdsync stats types.
- Test subclasses depend on consistent bucket names and mount point constants.

## Risks and edge cases
- Reflection into S3Proxy internals is brittle across library upgrades.
- Global configuration mutation requires `super.after()` cleanup; leakage can affect unrelated tests.
- `checkUfsMatches` assumes sorted Alluxio list order is compatible with sorted S3 item order.
- Real S3 mode is disabled by default but would depend on external credentials/network.

## Test signals
- Provides high-value infrastructure for object-store sync tests and precise operation-count assertions.
- Failure in this base usually indicates environment/configuration breakage rather than a single sync scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncV2TestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PermissionCheckTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PermissionCheckTest.java

## Purpose
End-to-end FileSystemMaster permission tests with authorization enabled. The suite validates how create, mkdir, rename, delete, read/list/status, attribute changes, complete/free, ACL-style owner/group/mode updates, and explicit access checks behave for owner, group, other, superuser, and supergroup users.

## Important APIs/types/functions
- Configures `SECURITY_GROUP_MAPPING_CLASS`, permission supergroup, and root UFS via `ConfigurationRule`.
- Uses `AuthenticatedUserRule` to run individual file master calls as different users.
- `FakeUserGroupsMapping` maps admin/user1/user2/user3/user4 to deterministic groups.
- `before()` constructs `MasterRegistry`, `MetricsMaster`, block master, and file master with `TestUserState`, starts services, and calls `createDirAndFileForTest`.
- Helper methods wrap each operation: `verifyCreateFile`, `verifyCreateDirectory`, `verifyRename`, `verifyDelete`, `verifyRead`, `verifyGetFileId`, `verifyGetFileInfoOrList`, `verifySetState`, `verifyCompleteFile`, `verifyFree`, `verifySetAcl`, and `verifyAccess`.

## Control flow
- Shared fixture creates `/testDir`, `/testDir/file`, and `/testFile` with controlled owners/groups/modes.
- Each test switches the authenticated user, executes one master operation, and checks either result metadata or expected exception message.
- Negative tests use `ExpectedException` and `ExceptionMessage.PERMISSION_DENIED` with a constructed `user/access/path/failed-at` message.
- Umask-specific tests temporarily change `SECURITY_AUTHORIZATION_PERMISSION_UMASK` to create unreadable or non-executable paths.
- Recursive `setAttribute` tests verify child metadata changes after owner/group/mode updates.

## State and persistence behavior
- The file master runs against a temporary root UFS and a noop journal system.
- Permission state is inode owner/group/mode plus global auth config and group mapping cache.
- Tests reset group mapping cache and reload configuration in teardown, important because group mapping and authorization settings are process-global.

## Dependencies and integration points
- Exercises FileSystemMaster public methods and their contexts, security utilities that derive owner/group from authenticated user, group mapping service cache, and exception-message contracts.
- Integrates with block and metrics masters through a real `MasterRegistry`.

## Risks and edge cases
- The class is large and relies on shared mutable namespace; test order must not matter because each test rebuilds the master.
- `getRootInode()` appears unused and may be legacy helper drift.
- Exact exception-message assertions are useful but brittle if wording changes.
- Some comments in delete/free tests mention the wrong user/path, but assertions encode the intended behavior.

## Test signals
- Very strong regression signal for FileSystemMaster authorization enforcement at API boundaries.
- Covers both allow and deny paths, including supergroup bypass, owner-only ACL updates, execute requirement for directory listing, recursive attributes, and missing-file access checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PermissionCheckTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PermissionCheckerTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PermissionCheckerTest.java

## Purpose
Focused unit tests for `DefaultPermissionChecker` against a manually constructed `InodeTree`. It validates POSIX-style owner/group/other permission selection, parent/ancestor permission checks, superuser/supergroup bypass, invalid-path behavior, and effective permission calculation.

## Important APIs/types/functions
- Builds static `InodeTree`, `InodeStore`, `MountTable`, `InodeLockManager`, block master, and metrics master in `beforeClass`.
- `FakeUserGroupsMapping` provides deterministic single and multi-group membership.
- `createAndSetPermission` locks paths with `LockPattern.WRITE_EDGE`, creates inodes, then writes owner/group/mode directly into the inode store.
- `checkPermission` calls `PermissionChecker.checkPermission`; `checkParentOrAncestorPermission` calls `checkParentPermission`; `getPermission` validates `PermissionChecker.getPermission`.

## Control flow
- Class-level setup initializes root as admin/admin/0755 and creates `/testDir/file`, `/testFile`, and `/testWeirdFile`.
- Tests set `AuthenticatedClientUser` directly, lock the relevant inode path, and invoke permission checker methods.
- Weird mode `0157` is used to prove there is no fallback from owner to group/other or group to other when a more specific class lacks bits.
- Parent and ancestor tests use a partially missing path to ensure checks stop at the existing ancestor.

## State and persistence behavior
- Inode metadata is in a heap/metastore-backed tree and is modified directly after creation.
- Uses `NoopJournalContext`, so journal persistence is not the concern; lock correctness and checker semantics are.
- Global auth configuration and group mapping cache are changed at class setup and reset at teardown.

## Dependencies and integration points
- Integrates core inode tree locking, inode store mutation, group mapping, authenticated client user state, and permission exception formatting.
- Uses mocked UFS manager/mount info because permission checking only needs inode namespace context.

## Risks and edge cases
- Static fixture means inode state is shared across tests; current tests are read-only after setup.
- Direct inode mutation bypasses higher-level FileSystemMaster behavior, so this complements but does not replace `PermissionCheckTest`.
- Exact denial message assertions are brittle but pin user-facing diagnostics.

## Test signals
- Strong signal for the low-level permission algorithm, especially specific-class bit selection and supergroup bypass.
- Regression indicators: owner/group/other fallback changes, parent checks using the wrong ancestor, or `getPermission` returning non-POSIX effective bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PermissionCheckerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PersistJobTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PersistJobTest.java

## Purpose
Small unit test for the `PersistJob` value object. It checks that constructor-provided identifiers, URI, temporary UFS path, timer, and mutable cancel state are returned by the corresponding getters.

## Important APIs/types/functions
- Creates random `jobId`, `fileId`, `AlluxioURI`, temp UFS path string, `ExponentialTimer`, and `PersistJob.CancelState`.
- Constructs `PersistJob(jobId, fileId, uri, tempUfsPath, timer)` and calls `setCancelState`.
- Asserts `getId`, `getFileId`, `getUri`, `getTempUfsPath`, `getTimer`, and `getCancelState`.

## Control flow
- Single test method `fields()` generates randomized inputs, mutates cancel state, and validates field round-trip.

## State and persistence behavior
- No external state or persistence; the test is strictly object state/getter coverage.
- `ExponentialTimer` is stored by reference and not advanced.

## Dependencies and integration points
- Depends on `CommonUtils.randomAlphaNumString`, `AlluxioURI`, and timer type used by async persistence scheduling.

## Risks and edge cases
- Random string length can be zero, so it also lightly touches empty URI/path construction.
- Does not test timer behavior, equality semantics, serialization, or cancellation transitions beyond setter/getter.

## Test signals
- Basic regression signal for `PersistJob` API shape and field wiring used by `PersistenceTest` and FileSystemMaster persistence internals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PersistJobTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PersistenceTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PersistenceTest.java

## Purpose
PowerMock-based tests for FileSystemMaster asynchronous persistence scheduling and job tracking. The suite drives manual persistence scheduler/checker heartbeats, mocks JobMasterClient interactions, validates state transitions, retry/cancel behavior, rename/delete completion, and journal replay across master restarts.

## Important APIs/types/functions
- Uses `ManuallyScheduleHeartbeat` for `MASTER_PERSISTENCE_CHECKER` and `MASTER_PERSISTENCE_SCHEDULER`.
- Mocks `JobMasterClient.Factory.create` to return `mMockJobMasterClient`.
- Uses `scheduleAsyncPersistence`, `HeartbeatScheduler.execute`, `JobMasterClient.run`, `getJobStatus`, and UFS temp file touch.
- Whitebox helpers expose `mPersistRequests` and `mPersistJobs`.
- Helper methods: `createTestFile`, `checkEmpty`, `checkPersistenceRequested`, `checkPersistenceInProgress`, `waitUntilPersisted`, `startServices`, `stopServices`, and `createJobInfo`.

## Control flow
- `before()` sets UFS journal type, temporary root UFS, persistence retry intervals, authenticates a test user, then starts masters and mocks job client creation.
- Empty tests assert no residual requests/jobs across idle heartbeats.
- `successfulAsyncPersistence` moves from NOT_PERSISTED to requested, scheduled job, CREATED/RUNNING polling, temp UFS file creation, COMPLETED polling, and final PERSISTED state.
- `noRetryCanceled` ensures canceled job status clears queues without retry.
- `retryFailed` loops failed job status through checker/scheduler until max wait expires and state returns to not persisted with empty queues.
- `retryPersistJobRenameDelete` completes a job after the source file is renamed and source directory deleted, proving commit uses current file path by id.
- Replay tests stop/start services with the same journal and verify pending requests and in-progress jobs survive restart.

## State and persistence behavior
- Exercises both in-memory maps (`mPersistRequests`, `mPersistJobs`) and journaled persistence of their state.
- Touches temporary UFS files to simulate job output needed by the checker to mark files persisted.
- Validates `PersistenceState.NOT_PERSISTED`, `TO_BE_PERSISTED`, and `PERSISTED`, plus non-invalid UFS fingerprints after completion.

## Dependencies and integration points
- Integrates FileSystemMaster, block/metrics masters, UFS journal, job service client factory, heartbeats, UFS utilities, and security user state.
- Uses PowerMock static mocking, Mockito, and Whitebox reflection.

## Risks and edge cases
- Timing-sensitive loops and waits are bounded but can be flaky on slow environments.
- Whitebox field access is brittle against FileSystemMaster internal refactors.
- Static mocking of JobMasterClient factory can leak if teardown does not run.
- `mSafeModeManager`, `mStartTimeMs`, and `mPort` are initialized but not visibly used in the shown test body, suggesting legacy residue.

## Test signals
- High-value signal for async persistence lifecycle, retry policy, journal replay, and rename/delete race handling.
- Regression indicators: duplicate scheduling, missing persisted fingerprint, jobs lost after restart, or canceled/failed jobs staying in the wrong queue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PersistenceTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/RpcContextTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/RpcContextTest.java

## Purpose
Unit tests for `RpcContext` close semantics and cancellation tracking. It verifies close order, exception propagation/suppression, and how operation-context call trackers mark an RPC as cancelled.

## Important APIs/types/functions
- Mocks `BlockDeletionContext`, `JournalContext`, and `OperationContext`.
- Constructs `RpcContext(mMockBDC, mMockJC, mMockOC)`.
- Tests `close`, `isCancelled`, and `throwIfCancelled`.
- Uses custom `CallTracker` implementations through `InternalOperationContext.withTracker`.

## Control flow
- Basic close test calls `close()` with no exceptions.
- Order test records close calls and asserts journal context closes before block deletion context.
- Dual exception tests make both close calls throw, expecting the journal exception as primary and block deletion exception suppressed.
- Single exception tests verify both resources are still closed.
- Cancellation test adds one always-cancelled tracker and one active tracker, then expects `isCancelled()` true and `throwIfCancelled()` to throw.

## State and persistence behavior
- No persistent state; tests are resource-lifecycle and cancellation-state checks.
- Suppressed exceptions preserve secondary close failure context.

## Dependencies and integration points
- Integrates with journal and block deletion resource contracts and operation context call trackers used by file master RPC paths.

## Risks and edge cases
- Exact primary exception depends on close order; intentional but sensitive to resource ordering changes.
- Cancellation test expects any cancelled tracker to cancel the RPC, regardless of tracker type.

## Test signals
- Strong signal for safe cleanup under failures and correct cancellation propagation from client/state-lock trackers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/RpcContextTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/async/DefaultAsyncPersistHandlerTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/async/DefaultAsyncPersistHandlerTest.java

## Purpose
Unit tests for worker-side assignment behavior in `DefaultAsyncPersistHandler`. It validates that files are scheduled for persistence only when their blocks are all on one worker and that deleted files are skipped when workers poll.

## Important APIs/types/functions
- Mocks `FileSystemMaster` and wraps it in `FileSystemMasterView`.
- Uses `DefaultAsyncPersistHandler.scheduleAsyncPersistence` and `pollFilesToPersist(workerId)`.
- Builds `FileBlockInfo`, `BlockInfo`, `BlockLocation`, `FileInfo`, and expects `PersistFile` block IDs.

## Control flow
- `scheduleAsyncPersist` sets one block on one worker, schedules the path, polls that worker, and expects one `PersistFile` with the block id.
- `persistenceFileWithBlocksOnMultipleWorkers` creates two blocks on different workers and verifies neither worker receives a persist assignment.
- `persistenceFileAfterDeletion` schedules a file, then makes `getFileInfo(fileId)` throw `FileDoesNotExistException`; poll returns no work.

## State and persistence behavior
- Handler stores scheduled file ids internally until polled; the test verifies it consults current master view at poll time.
- No real UFS persistence is performed; output is a `PersistFile` work description.

## Dependencies and integration points
- Integrates async persist handler with FileSystemMaster block metadata and path/id lookup APIs.
- Depends on completed, non-empty `FileInfo` as persistence eligibility signal.

## Risks and edge cases
- Tests do not cover incomplete files, zero-length files, repeated polling, or multiple eligible files.
- Multi-worker behavior assumes a file with blocks split across workers should not be assigned, which is a key scheduling invariant.

## Test signals
- Good signal for avoiding impossible worker assignments and for pruning deleted scheduled files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/async/DefaultAsyncPersistHandlerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/BaseTaskTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/BaseTaskTest.java

## Purpose
Unit tests for `BaseTask.pathIsCovered`, validating how a metadata sync task's requested base path and `DescendantType` cover later sync/wait requests.

## Important APIs/types/functions
- Builds `TaskInfo` with mocked `MetadataSyncHandler`, base path `/path`, and each descendant type.
- Creates tasks through `BaseTask.create`.
- Calls `pathIsCovered(AlluxioURI, DescendantType)` for exact, parent, prefix-lookalike, sibling, child, and grandchild paths.

## Control flow
- `PathIsCoveredNone` expects only exact path with `NONE` request to be covered.
- `PathIsCoveredOne` expects exact and direct children to be covered for `NONE`, exact path for `ONE`, and no `ALL` coverage.
- `PathIsCoveredAll` expects all descendants and descendant-type requests under the base path to be covered.

## State and persistence behavior
- No persistence; test state is a mock UFS client supplier and task metadata.
- Path boundary correctness is central: `/path2` must not be treated as under `/path`.

## Dependencies and integration points
- Uses `DirectoryLoadType.SINGLE_LISTING`, `MockUfsClient`, and `TaskInfo` construction matching TaskTracker call sites.

## Risks and edge cases
- Method names start uppercase, unusual for Java style but valid JUnit tests.
- Covers common path cases but not trailing slash normalization or root path behavior.

## Test signals
- Strong signal for task de-duplication/wait coverage semantics, preventing overbroad reuse of in-flight sync tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/BaseTaskTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/BatchPathWaiterTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/BatchPathWaiterTest.java

## Purpose
Tests `BatchPathWaiter` behavior used by single-listing metadata sync tasks. It verifies when waiters on paths are released as sorted/truncated UFS batches complete, including in-order, out-of-order, and final task completion cases.

## Important APIs/types/functions
- Creates `BaseTask` with `DirectoryLoadType.SINGLE_LISTING`; casts root tasks to `BatchPathWaiter` for completed range assertions.
- Uses `SyncProcessResult` and `PathSequence` to feed completed path intervals to `nextCompleted`.
- Mocks `MetadataSyncHandler.onPathLoadComplete` to call `path.onComplete`.
- Uses executor futures around `waitForSync`.

## Control flow
- Waiter tests submit blocking waits, call `nextCompleted` with partial/final batches, assert timeout or release, and finally call `getPathLoadTask().onProcessComplete`.
- In-order and out-of-order tests inspect `getLastCompleted()` range merging, proving contiguous intervals collapse and disjoint intervals remain separate.
- Single path task completion verifies `isCompleted` becomes present only after process completion.

## State and persistence behavior
- State under test is in-memory completed path ranges and waiter queues.
- Final task completion releases remaining waiters even when their path was not passed by a non-truncated completed range.

## Dependencies and integration points
- Integrates BaseTask, PathLoadTask completion callbacks, MetadataSyncHandler, and DefaultFileSystemMaster journal context stubbing.

## Risks and edge cases
- Timeout-based assertions can be slow/flaky under heavy load.
- Test method `TestBaseTackSinglePath` has a typo in the name only.
- Range comparison depends on lexical path ordering.

## Test signals
- Strong signal for concurrent metadata sync wait semantics and completed-range merging.
- Regression indicators: waiters released on truncated batches, not released on final completion, or completed intervals merging incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/BatchPathWaiterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/DirectoryPathWaiterTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/DirectoryPathWaiterTest.java

## Purpose
Parameterized tests for directory-load path waiters with `DirectoryLoadType.BFS` and `DFS`. It validates release rules for exact path, child path, nested path, parent path, truncated directory loads, and final task completion.

## Important APIs/types/functions
- Parameterized `directoryLoadTypes()` returns BFS and DFS.
- Creates `BaseTask` for `DescendantType.ALL` with the chosen directory load type.
- Uses `waitForSync`, `nextCompleted`, `SyncProcessResult`, `PathSequence`, and `PathLoadTask.onProcessComplete`.

## Control flow
- `TestWaiter` waits on the base path and releases it after a non-truncated root result.
- `TestMultiWaiter` releases a child when its own non-truncated directory result completes but not when truncated.
- `TestNestedWaiter` proves completing an unrelated nested path does not release waiters, while completing the parent releases direct children.
- `TestParentWaiter` shows root completion releases direct child `/path`, `/path` completion releases `/path/nested`, and final task completion releases deeper `/path/nested/1`.

## State and persistence behavior
- In-memory waiter coordination only.
- Truncated results intentionally keep waiters blocked until a full result or task completion.

## Dependencies and integration points
- Uses mocked DefaultFileSystemMaster for journal context and MetadataSyncHandler callback wiring.
- Complements `BatchPathWaiterTest` by exercising directory-load strategies rather than single-listing sorted ranges.

## Risks and edge cases
- Timeout-based future assertions may be environment-sensitive.
- Does not compare BFS vs DFS ordering differences beyond shared waiter release contract.

## Test signals
- Strong signal for metadata sync clients waiting on directory traversal under BFS/DFS load modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/DirectoryPathWaiterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/DummySyncProcess.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/DummySyncProcess.java

## Purpose
Test-only `SyncProcess` implementation that consumes UFS load results, optionally schedules nested directory loads, and returns a compact `SyncProcessResult`. It is used by mdsync task tests to isolate task/load orchestration from real inode mutation.

## Important APIs/types/functions
- Implements `SyncProcess.performSync(LoadResult, UfsSyncPathCache)`.
- Reads `loadResult.getUfsLoadResult().getItems()`.
- For directory-load tasks, calls `syncPathCache.shouldSyncPath` and `loadResult.getTaskInfo().getMdSync().loadNestedDirectory`.
- Returns `SyncProcessResult` with optional `PathSequence`, truncated flag, and root-file flag.

## Control flow
- Streams UFS statuses and peeks each item; directory statuses in dir-load mode may create nested load tasks after sync-cache approval.
- Collects the stream to a list so it can inspect first/last items.
- Empty loads return a result with null path sequence.
- Non-empty loads derive a path sequence from the first and last status names and mark root-file when the root load contains exactly one file.

## State and persistence behavior
- Stateless except for side effect of scheduling nested directory loads through MetadataSyncHandler.
- Does not write Alluxio metadata or UFS state.

## Dependencies and integration points
- Integrates UFS status streams, task metadata, sync path cache, `PathSequence`, and nested directory loading.
- Converts `InvalidPathException` to `InvalidArgumentRuntimeException` inside stream processing.

## Risks and edge cases
- Assumes status names can be converted directly to `AlluxioURI` for path sequence comparisons.
- Collecting streams consumes the UFS load result; tests relying on later stream reuse would fail.
- Only approximates real sync behavior, so it is suitable for orchestration tests but not metadata mutation validation.

## Test signals
- Provides deterministic sync-process behavior for TaskTracker and waiter tests, especially nested directory scheduling and truncated batch propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/DummySyncProcess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/MockUfsClient.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/MockUfsClient.java

## Purpose
Test `UfsClient` implementation for metadata sync task tests. It can return scripted listings, function-generated listings, get-status results, injected errors, and a configurable rate limiter.

## Important APIs/types/functions
- Implements `UfsClient.performListingAsync` and `getRateLimiter`.
- Adds test helper methods `setError`, `setRateLimiter`, `setResult`, `setGetStatusItem`, and `setListingResultFunc`.
- Provides `performGetStatusAsync` helper with the same callback shape used by tests.

## Control flow
- `performGetStatusAsync` returns either empty or singleton `UfsLoadResult` based on fixed or function-derived status.
- `performListingAsync` first injects `mError` if present; otherwise uses `mResultFunc`; otherwise consumes the next scripted stream from `mItems`.
- Listing results are collected, last item becomes continuation/start-after marker, truncation is controlled by function boolean or whether more scripted batches exist.
- `getRateLimiter` returns configured limiter or unlimited zero-rate limiter.

## State and persistence behavior
- Mutable test state controls future callback behavior.
- No asynchronous threads are created here; callbacks are invoked synchronously by the test mock.

## Dependencies and integration points
- Integrates with `TaskTracker`, `BaseTask`, `UfsLoadResult`, `UfsStatus`, `DescendantType`, and rate limiter tests.

## Risks and edge cases
- Function/script listing paths assume non-empty item lists when constructing `lastItem`; empty listing through those paths can throw.
- Fields are package-private and mutable, fitting tests but not thread-safe beyond controlled scenarios.
- `mGetStatusFunc` has no setter in the shown file, so tests would need package access or direct field access to use it.

## Test signals
- Central scaffold for deterministic UFS load success, retry, truncation, concurrency, and failure scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/MockUfsClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/TaskTrackerTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/TaskTrackerTest.java

## Purpose
Comprehensive concurrency and error-handling tests for `TaskTracker`, the orchestrator for Metadata Sync V2 UFS load requests and sync processing. It validates rate limiting, concurrent loading/processing, directory nested loads, retries, failure propagation, stats accounting, and duplicate in-flight task blocking.

## Important APIs/types/functions
- Creates `TaskTracker(concurrentProcessing, concurrentUfsLoads, ..., UfsSyncPathCache, UfsAbsentPathCache, SyncProcess, clientSupplier)`.
- Uses `MetadataSyncHandler.checkTask` flow via `mTaskTracker.checkTask`.
- `MockUfsClient` supplies listings, errors, and rate limiter.
- `DummySyncProcess` simulates sync result processing and nested directory scheduling.
- `checkStats` validates `TaskStats`: batches, statuses, load errors, load requests, load/process failure flags, and first-load-was-file.

## Control flow
- Setup creates one-thread defaults, mocked sync/absent caches, mocked file master journal context, and a metadata sync handler.
- Rate limit test uses a fake ticker and semaphore to prove each load acquires permits.
- Concurrent tests configure multiple UFS load and processing lanes, block processing with latches/semaphores, and wait until the expected number of loads/processes are active.
- Error tests inject IO/runtime failures in processing or listing under single-listing and directory-load modes, then assert `waitComplete` throws and stats mark load/process failures.
- Directory load test returns both file and directory statuses and verifies nested `/dir` load happens only when `UfsSyncPathCache.shouldSyncPath` permits it.
- Basic/multi-batch/retry tests validate successful stats under scripted single and multiple truncated batches.
- Blocking sync test submits two same-path tasks while processing is blocked and expects one execution to satisfy both callers.

## State and persistence behavior
- State under test is TaskTracker's running task registry, executor queues, retry counters, and stats.
- No real Alluxio metadata persistence; `NoopJournalContext` is used and `DummySyncProcess` avoids inode writes.
- Teardown asserts no running tasks remain before closing the tracker.

## Dependencies and integration points
- Integrates task tracking with rate limiter, UFS client callbacks, sync path cache, absent path cache, MetadataSyncHandler, and `BaseTask` completion.
- Uses `CommonUtils.waitForResult` and `WaitForOptions` for concurrency synchronization.

## Risks and edge cases
- Heavy loops repeat many tests 100 times, increasing runtime but catching races.
- Timeout/latch-based concurrency checks can be flaky under severe scheduler delays.
- Exact load error count expectations encode retry policy details.
- Some comments are inaccurate copy-pastes, but assertions are specific.

## Test signals
- Very strong signal for mdsync task orchestration correctness under concurrency and failure.
- Regression indicators: over/under-parallel loading, duplicate same-path task execution, nested directory loads ignored, retry counts changed, or tasks left running after failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/TaskTrackerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/TestSyncProcessor.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/TestSyncProcessor.java

## Purpose
Test subclass of `DefaultSyncProcess` that adds hooks around `performSyncOne` for concurrency and mutation-race tests. It can invoke callbacks before each inode sync and block/release when the nth sync operation is reached.

## Important APIs/types/functions
- Extends `DefaultSyncProcess`.
- Functional interfaces: `Callback` and `SyncOneCallback`.
- Overrides protected `performSyncOne(SyncProcessState, UfsItem, InodeIterationResult)`.
- Public hook methods: `beforePerformSyncOne` and `blockUntilNthSyncThenDo`.
- Uses a `Semaphore` to coordinate the blocking callback.

## Control flow
- On every `performSyncOne`, optional pre-sync callback receives the `SyncProcessContext`.
- Sync count increments; when it reaches configured `mBlockOnNth`, the callback runs and the semaphore is released.
- After hook logic, delegates to `super.performSyncOne`.
- `blockUntilNthSyncThenDo` sets the target count/callback and waits until the sync thread reaches that point.

## State and persistence behavior
- Adds mutable hook state (`mBlockOnNth`, `mSyncCount`, callbacks, semaphore) around real DefaultSyncProcess behavior.
- Persistence and inode mutations are still performed by the superclass when used with real master/inode dependencies.

## Dependencies and integration points
- Constructor mirrors DefaultSyncProcess dependencies: file master, inode store, mount table, inode tree, sync path cache, and absent path cache.
- Intended for tests that need precise synchronization with individual inode sync operations.

## Risks and edge cases
- Callback exceptions are converted to generic `RuntimeException`, losing original detail.
- `blockUntilNthSyncThenDo` acquires the semaphore after setting callbacks; if nth sync already passed, it can block forever.
- State is not reset between uses except by replacing callbacks/target.

## Test signals
- Useful scaffold for race-condition tests involving metadata sync and concurrent namespace changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/TestSyncProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/UfsLoadsTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/UfsLoadsTest.java

## Purpose
Early or skeletal tests for UFS load behavior in Metadata Sync V2. The current file sets up a full TaskTracker/MetadataSyncHandler test scaffold and contains a minimal `singleFileSync` test that only configures get-status state.

## Important APIs/types/functions
- Uses `TaskTracker`, `MetadataSyncHandler`, `MockUfsClient`, `DummySyncProcess`, `UfsSyncPathCache`, and `UfsAbsentPathCache`.
- Spies on `SyncProcess.performSync` to collect processed UFS items into `mProcessedItems`.
- `getClient` wraps `mUfsClient` in a `CloseableResource`.

## Control flow
- `before()` creates a cached thread pool, spy mock UFS client and sync process, mocks caches, constructs `TaskTracker`, and creates handler.
- The sync process spy peeks each load result's item stream to collect processed items before calling the real dummy process.
- `after()` asserts no running tasks, closes task tracker, and shuts down executor.
- `singleFileSync` currently only calls `mUfsClient.setGetStatusItem(mFileStatus)` and performs no sync assertion.

## State and persistence behavior
- Maintains in-memory processed item list; no real metadata or UFS persistence.
- Teardown still validates TaskTracker is idle.

## Dependencies and integration points
- Same mdsync scaffolding as TaskTracker tests, but underused in current test body.

## Risks and edge cases
- The single test has no assertion and does not trigger a task, so it provides almost no regression signal.
- The setup is heavier than the test behavior and may mask intended future work.

## Test signals
- Current signal is limited to fixture construction/teardown. It should be expanded or removed if no behavior is intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/mdsync/UfsLoadsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/AbstractInodeTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/AbstractInodeTest.java

## Purpose
Shared base class for inode-related tests. It provides common owner/group/mode constants, an `ExpectedException` rule, and helper factories for mutable directory/file inodes.

## Important APIs/types/functions
- Constants: `TEST_OWNER`, `TEST_GROUP`, `TEST_DIR_MODE`, `TEST_FILE_MODE`.
- `createInodeFileId(long containerId)` uses `BlockId.createBlockId` and max sequence number.
- `createInodeDirectory()` creates a `MutableInodeDirectory` with id 1, parent 0, name `test1`, owner/group/mode.
- `createInodeFile(long id)` creates a `MutableInodeFile` under parent 1 with KB block size and file mode.

## Control flow
- No tests in this abstract class; subclasses call helpers to build repeatable inode fixtures.

## State and persistence behavior
- Factory methods return mutable inode objects but do not write them to an inode store.
- File id helper encodes container id into Alluxio block id format.

## Dependencies and integration points
- Integrates inode constructors with create contexts, grpc options, block id utilities, constants, and authorization modes.

## Risks and edge cases
- Fixed ids/parent ids are convenient but can collide if subclasses combine multiple fixtures without care.
- `ExpectedException` is legacy JUnit style and may be unused by some subclasses.

## Test signals
- Infrastructure only; value comes through consistency of inode fixtures in subclass tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/AbstractInodeTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/AsyncUfsAbsentPathCacheTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/AsyncUfsAbsentPathCacheTest.java

## Purpose
Unit tests for `AsyncUfsAbsentPathCache`, validating detection and caching of absent UFS paths under a mount, cache invalidation on mount/path changes, capacity-limited metrics, and hit/miss counters.

## Important APIs/types/functions
- Sets `MASTER_UFS_PATH_CACHE_CAPACITY` to 3 with `ConfigurationRule`.
- Builds `MasterUfsManager`, `MountTable`, and `AsyncUfsAbsentPathCache`.
- `before()` mounts a temporary local UFS at `/mnt`.
- Helper `process(path)` calls `processPathSync(path, Collections.emptyList())`.
- Helper `checkPaths(firstAbsent)` asserts descendants of first absent path are cached absent while ancestors are not.
- Nested `TestAsyncUfsAbsentPathCache` overrides cached gauge timeout for metrics tests.

## Control flow
- `isAbsent` checks unknown path, processes absent path, verifies descendant absence, then creates a UFS folder and verifies it is not absent.
- Root/directory tests process paths where different ancestor levels are the first missing UFS component.
- Add/remove UFS directory tests show processing adapts when UFS directories appear or disappear.
- `removeMountPoint` unmounts and remounts the same UFS and expects old cache entries to be gone.
- `removePath` creates previously absent paths and reprocesses to clear cached absence.
- Metric tests reset metrics, add paths, wait for cached gauge refresh, and assert cache size/hit/miss values.

## State and persistence behavior
- Uses real local filesystem directories under a temporary folder as UFS state.
- Cache state is in-memory, capacity-bounded, and tied to mount table/mount ids.
- Metrics are global and reset before gauge tests.

## Dependencies and integration points
- Integrates absent path cache, mount table resolution, UFS manager, local UFS configuration, Alluxio metrics registry, and path normalization.

## Risks and edge cases
- Metrics tests rely on sleeps around cached gauges; they can be timing-sensitive.
- Capacity is small and intentional, so eviction behavior affects metric expectations.
- Mount id changes on remount are important for invalidation; tests would catch stale mount-scoped cache keys.

## Test signals
- Strong signal for absent-path cache correctness, especially first-missing-ancestor detection and invalidation after UFS/mount changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/AsyncUfsAbsentPathCacheTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/BaseInodeLockingTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/BaseInodeLockingTest.java

## Purpose
Base fixture for inode locking tests. It builds a small inode tree `/a/b/c`, provides assertions for inode and edge lock state, and verifies teardown leaves no locks held.

## Important APIs/types/functions
- Fields: `InodeLockManager`, `HeapInodeStore`, `mRootDir`, `mDirA`, `mDirB`, `mFileC`, and `mAllInodes`.
- `after()` checks no node or edge read/write locks remain.
- Assertion helpers: `checkOnlyNodesReadLocked`, `checkOnlyNodesWriteLocked`, `checkOnlyIncomingEdgesReadLocked`, `checkOnlyIncomingEdgesWriteLocked`, `checkIncomingEdgeReadLocked`, and `checkIncomingEdgeWriteLocked`.
- Factory helpers: `inodeDir` and `inodeFile` write mutable inodes into the store and link children.

## Control flow
- Fixture construction writes root, `/a`, `/a/b`, and `/a/b/c` to the heap inode store.
- Lock checks build expected sets, assert specified locks are held by current thread, then assert all other fixture inodes/edges are unlocked.
- Subclasses perform locking and call superclass teardown to enforce cleanup.

## State and persistence behavior
- Uses in-memory heap inode store only.
- Lock state is thread-local/current-thread observable through `InodeLockManager` methods.

## Dependencies and integration points
- Supports tests for `SimpleInodeLockList`, `CompositeInodeLockList`, and related lock-list classes.
- Integrates inode store child relationships with lock manager edge identity.

## Risks and edge cases
- Fixture is fixed-depth and does not cover wide trees unless subclasses add more.
- `after()` can obscure a test's original failure if cleanup also fails, but it is valuable for leak detection.

## Test signals
- Infrastructure signal: catches lock leaks in subclasses and provides precise lock-state diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/BaseInodeLockingTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/CheckpointedIdHashSetTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/CheckpointedIdHashSetTest.java

## Purpose
Parameterized checkpoint/restore test for `CheckpointedIdHashSet` implementations used by file master metadata sets.

## Important APIs/types/functions
- Parameterized data covers `PinnedInodeFileIds`, `ReplicationLimitedFileIds`, and `ToBePersistedFileIds`.
- Uses `writeToCheckpoint(OutputStream)` and `restoreFromCheckpoint(CheckpointInputStream)`.
- Temporary file stores serialized checkpoint bytes.

## Control flow
- Adds ids from 0 to 1,000,000 stepping by 5,762.
- Copies the set contents to a list, writes checkpoint to a temp file, clears the set, restores from checkpoint, and asserts all copied ids are present.

## State and persistence behavior
- Directly exercises durable checkpoint serialization and restoration for id sets.
- Does not verify order or absence of extra ids, only containment of original values.

## Dependencies and integration points
- Integrates checkpoint stream wrappers with concrete file metadata id set classes.

## Risks and edge cases
- Because it asserts `containsAll` but not size equality, extra restored ids would not fail this test.
- Does not test empty set checkpoint, duplicate additions, or corrupt checkpoint handling.

## Test signals
- Good basic persistence signal for checkpointed metadata id sets used in pinned, replication-limited, and to-be-persisted file tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/CheckpointedIdHashSetTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/CompositeInodeLockListTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/CompositeInodeLockListTest.java

## Purpose
Unit tests for `CompositeInodeLockList`, which extends an existing base lock list while preserving ownership boundaries. The tests validate extension, lock mode reporting, locked inode list views, and close/unlock behavior.

## Important APIs/types/functions
- Extends `BaseInodeLockingTest`.
- Uses `SimpleInodeLockList` as `mBase` and `CompositeInodeLockList` as `mComposite`.
- Exercises `lockRootEdge`, `lockInode`, `lockEdge`, `unlockLastInode`, `unlockLastEdge`, `close`, `getLockMode`, `getLockedInodes`, `numInodes`, `isEmpty`, and `get`.

## Control flow
- `unlockOnlyExtension` locks part of the path in the base, extends in composite, closes composite, and verifies only base locks remain.
- `extendFromEdge` starts from base locked through an edge, then locks inode/edge in composite and checks list contents and write-mode promotion.
- `extendFromInode` starts with only root inode locked, then extends edge/inode and validates similar state.
- `extendFromWriteLocked` verifies a base write-locked root edge makes composite lock mode WRITE.
- `doubleWriteLock` locks and unlocks a write-locked inode while retaining WRITE mode.
- `unlockIntoBase` calls `unlockLastEdge` when only base owns the edge, validating boundary handling.

## State and persistence behavior
- In-memory lock state only; no inode metadata persistence.
- Teardown closes composite/base and then asserts all locks released through the base class.

## Dependencies and integration points
- Integrates composite lock-list semantics with `InodeLockManager`, `LockMode`, and fixed inode tree fixture.

## Risks and edge cases
- Some tests do not assert exceptions for boundary unlocks, implying current behavior may be no-op/tolerant.
- Does not cover mixed read/write upgrades on every possible node/edge sequence.

## Test signals
- Strong signal that composite lock lists do not release locks they do not own and report lock mode/list state correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/CompositeInodeLockListTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InodeLockManagerTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InodeLockManagerTest.java

## Purpose
Concurrency tests for `InodeLockManager` node and edge locks. It verifies read/write compatibility and blocking semantics for inode locks and edge locks.

## Important APIs/types/functions
- Tests `lockInode` and `lockEdge` with combinations of `LockMode.READ` and `LockMode.WRITE`.
- Uses `LockResource` to hold/release locks.
- Uses a second thread plus `AtomicBoolean` to observe whether a competing lock acquisition finishes.

## Control flow
- `lockInode` runs four combinations: WRITE/READ, READ/WRITE, WRITE/WRITE should block; READ/READ should not.
- `lockEdge` runs the same combinations for `Edge(10, "name")`.
- Helpers acquire first lock, start a thread that tries to acquire a logically equivalent copied inode or new edge instance, sleep briefly if blocking is expected, then release and wait for completion.

## State and persistence behavior
- Lock state only; no inode store or filesystem persistence.
- Inode copy via journal entry proves locks are keyed by inode identity/id rather than Java object reference.
- Edge test proves locks are keyed by edge value rather than object reference.

## Dependencies and integration points
- Integrates `InodeLockManager`, `MutableInodeFile`, `CreateFileContext`, `Edge`, and `CommonUtils.waitFor`.

## Risks and edge cases
- Uses a 20 ms sleep to detect blocking, which is pragmatic but timing-sensitive.
- Does not test reentrancy, fairness, or lock cleanup after exceptions.

## Test signals
- Clear signal for core lock compatibility matrix and key equality semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InodeLockManagerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InodeTreeBufferedIteratorTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InodeTreeBufferedIteratorTest.java

## Purpose
Unit tests for `InodeTreeBufferedIterator`, which creates a closeable iterator over inode journal entries from an inode store. It verifies empty/root-only iteration and exception propagation from asynchronous buffering.

## Important APIs/types/functions
- Uses `HeapInodeStore` and `InodeTreeBufferedIterator.create(mInodeStore, rootDirectory)`.
- Iterates through `CloseableIterator<Journal.JournalEntry>`.
- Builds `MutableInodeDirectory` and `MutableInodeFile` fixtures and child links.
- Defines `MutableInodeFileDelegate` abstract mock base to inject `toJournalEntry` failure.

## Control flow
- `noRoot` passes null root and expects no iterator entries.
- `singleItem` writes root inode, creates iterator, expects one inode-directory journal entry with id 0 and no more entries.
- `bufferingFailure` builds root with 100 child dirs and files, randomly chooses one mocked file whose `toJournalEntry` throws, then iterates until it observes a wrapped runtime exception with the injected cause/message.

## State and persistence behavior
- In-memory heap inode store is populated and cleared/closed around each test.
- Iterator output is journal-entry serialization of inode state, but no checkpoint file is written.
- Failure test validates exceptions raised in buffering are surfaced through iterator consumption.

## Dependencies and integration points
- Integrates inode store child traversal, inode-to-journal serialization, closeable iterator contract, and Mockito failure injection.

## Risks and edge cases
- `@Rule public ExpectedException mExpected;` is initialized in `before()` instead of at field declaration, unusual but not central.
- Random failed inode index can be 0, while loop creates dirs/files from 1..100, so occasionally no failure inode is injected and the test could fail. `new Random().nextInt(dirCount)` returns 0..99; index 0 is never matched.
- Does not assert full traversal ordering or complete entry count in success case beyond root-only.

## Test signals
- Useful signal for iterator close/empty/basic behavior and error surfacing, with a notable flakiness risk from random failure selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InodeTreeBufferedIteratorTest.java -->
