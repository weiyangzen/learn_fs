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
