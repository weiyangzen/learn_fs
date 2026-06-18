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
