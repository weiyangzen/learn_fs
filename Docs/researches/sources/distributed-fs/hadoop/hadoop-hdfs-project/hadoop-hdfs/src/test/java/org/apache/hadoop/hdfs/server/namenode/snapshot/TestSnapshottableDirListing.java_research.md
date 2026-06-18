# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshottableDirListing.java

## Purpose
`TestSnapshottableDirListing` verifies `getSnapshottableDirListing` results for root, normal directories, nested snapshottable directories, deletion/rename effects, snapshot counts, and user-based filtering.

## Important APIs, Types, and Functions
The file uses `DistributedFileSystem.getSnapshottableDirListing`, `allowSnapshot`, `disallowSnapshot`, `createSnapshot`, `rename` with `Rename.OVERWRITE`, `SnapshottableDirectoryStatus`, `UserGroupInformation`, `DFSTestUtil.getFileSystemAs`, `FsPermission`, and superuser group configuration keys.

## Control Flow
`testListSnapshottableDir` enables nested snapshots, starts with no listing, allows/disallows root, allows `dir1` and `dir2`, verifies status local names/full paths/snapshot counts, overwrites `dir2` to ensure its snapshottable status is removed, re-enables and creates two snapshots on `dir2`, creates nested snapshottable subdirectories under `dir1`, disallows one, and finally deletes `dir1` to ensure descendant snapshottable entries disappear. `testListWithDifferentUser` creates snapshottable directories as user1 and user2, then verifies the superuser sees all six while each normal user sees only owned directories.

## State and Persistence Behavior
The test manipulates live namespace state without restart. It verifies that snapshottable status follows inode lifecycle, not just path strings, and that listing authorization filters reflect owner/superuser state.

## Dependencies and Integration Points
It integrates snapshot manager listing, permission/UGI handling, root permissions, nested snapshot configuration, and rename/delete namespace operations.

## Risks and Edge Cases
Risks include returning null versus empty arrays inconsistently, stale snapshottable entries after overwrite/delete, wrong full paths after mutations, incorrect snapshot counts, and leaking other users' snapshottable directories to non-superusers.

## Test Signals
Signals are exact null/length checks, ordered full-path assertions, snapshot-number assertions, and user-specific visibility counts.
