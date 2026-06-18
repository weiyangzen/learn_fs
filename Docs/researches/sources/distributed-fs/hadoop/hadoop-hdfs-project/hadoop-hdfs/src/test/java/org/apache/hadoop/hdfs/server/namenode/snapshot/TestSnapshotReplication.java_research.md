# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotReplication.java

## Purpose
`TestSnapshotReplication` verifies how replication factors are represented for live files, snapshot file inodes, and shared block metadata. It ensures block preferred replication reflects the maximum required replication across live and retained snapshot states.

## Important APIs, Types, and Functions
The suite uses `DistributedFileSystem.setReplication`, `DFSTestUtil.createFile`, `SnapshotTestHelper.createSnapshot`, `FSDirectory.getINode`, `INodeFile`, `BlockInfo`, `INodesInPath`, and `FSDirectory.DirOp.READ`. Helpers are `checkFileReplication`, `getINodeFile`, and `checkSnapshotFileReplication`.

## Control Flow
`testReplicationWithoutSnapshot` creates a normal file and verifies both `FileStatus` replication and block replication change when the live replication factor changes. `testReplicationWithSnapshot` creates a file with replication 1, takes snapshots between incremental replication increases up to the number of DataNodes, records expected snapshot inode replication, and verifies each shared block reports the highest needed replication. It then lowers live replication to 3 and expects block replication to remain at 4 due to prior snapshots. `testReplicationAfterDeletion` snapshots a file three times, deletes the live file, and verifies snapshot inodes and blocks still retain the expected replication.

## State and Persistence Behavior
There is no restart, but the tests inspect snapshot-retained inode state after live metadata changes and live deletion. The key state behavior is shared block metadata preserving enough replication for all snapshot references.

## Dependencies and Integration Points
The file bridges client-level replication APIs and internal NameNode block/inode state. It relies on snapshot inode lookup through snapshot paths and `getPathSnapshotId` to compute per-snapshot file replication.

## Risks and Edge Cases
The risk is lowering live replication incorrectly reducing block replication needed by snapshots, or deleting the live file losing snapshot replication state. Another subtle risk is `checkFileReplication(Path file, ...)` ignores its `file` parameter and always checks `file1`, which is harmless in current tests but weakens helper generality.

## Test Signals
Signals are exact assertions on `FileStatus.getReplication`, `INodeFile.getFileReplication`, `INodeFile.getFileReplication(snapshotId)`, and `BlockInfo.getReplication` across live, snapshot, changed, and deleted states.
