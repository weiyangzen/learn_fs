# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotRename.java

## Purpose
`TestSnapshotRename` verifies snapshot rename behavior and interactions with snapshot lists, snapshot file status, invalid names, shell argument validation, and quota accounting for file renames in or around snapshotted directories.

## Important APIs, Types, and Functions
Important APIs include `DistributedFileSystem.renameSnapshot`, `SnapshotTestHelper.createSnapshot/getSnapshotRoot`, `FsShell -renameSnapshot`, `FSDirectory`, `INodeDirectory`, `DirectoryWithSnapshotFeature.DirectoryDiff`, `DiffList`, `ReadOnlyList`, `NSQuotaExceededException`, `SnapshotException`, `RemoteException`, and `LambdaTestUtils.intercept`. `checkSnapshotList` inspects internal snapshot lists sorted by name and directory diffs ordered by creation time.

## Control Flow
Snapshot list tests create three snapshots and rename them to values that change lexical order, asserting both sorted-name and time-order lists. File status tests compare snapshot file metadata before and after rename, allowing only the path to differ. Exception tests verify renaming non-existing snapshots, renaming to an existing name, reserved `.snapshot` names, slash-containing names, and wrong shell argument counts. Quota tests create snapshotted directories under tight namespace quotas and verify when create/rename operations should fail or still succeed across same-directory, cross-directory, and snapshottable-source scenarios.

## State and Persistence Behavior
The suite does not restart, but it inspects mutable namespace state through FSDirectory internals. Snapshot rename updates visible `.snapshot/<name>` path resolution and metadata while retaining underlying snapshot contents and creation-time diff ordering.

## Dependencies and Integration Points
Coverage integrates NameNode snapshot manager RPCs, FSDirectory internal inode/diff structures, HDFS shell command validation, quota enforcement, and general filesystem rename semantics under snapshot retention.

## Risks and Edge Cases
High-risk areas are maintaining two snapshot orderings, rejecting illegal target names, preserving snapshot file metadata under path rename, and quota calculations where snapshots retain deleted or renamed inodes. The quota tests particularly protect against double-counting or under-counting namespace space during rename operations involving snapshotted parents.

## Test Signals
Signals include exact snapshot list order, `FileStatus` string comparison after path normalization, exception type/message checks, shell return code and output checks, and successful/failed rename behavior under quota pressure.
