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
