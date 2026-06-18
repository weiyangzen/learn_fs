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
