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
