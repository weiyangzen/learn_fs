# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileCorruption.java

## Purpose

`TestFileCorruption.java` tests HDFS and local filesystem behavior when block or checksum corruption is reported or introduced. The complete 330-line file was read. It covers deleted replicas, local checksum corruption, corrupt reports for unknown blocks, disk-failure storage state, and replication accounting during batched incremental block reports.

## Important APIs, Types, and Functions

Key APIs are `DFSTestUtil`, `BlockListAsLongs`, `BlockReportReplica`, `ExtendedBlock`, `BlockManager.findAndMarkBlockAsCorrupt`, `DatanodeStorageInfo`, `DatanodeStorage`, `FSNamesystem` write locks, `ChecksumException`, and `GenericTestUtils.waitFor`. Helpers include `markAllBlocksAsCorrupt`, `updateAllStorages`, and `getFirstBlock`.

## Control Flow

`testFileCorruption` creates 20 files on a three-node cluster, deletes all blocks from one DataNode's materialized replicas, and verifies files remain readable through other replicas. `testLocalFileCorruption` overwrites a local file after Hadoop created its checksum and expects a logged `ChecksumException` rather than null-pointer fallout. `testArrayOutOfBoundsException` has a third DataNode report a corrupt block not present in the block map and then opens the file to catch indexing regressions. `testCorruptionWithDiskFailure` marks storages failed, marks all block storages corrupt, and verifies open does not crash. `testSetReplicationWhenBatchIBR` delays incremental block reports, raises replication above live DataNode count, and checks low-redundancy and missing-block counts.

## State and Persistence Behavior

State includes DataNode block files, local checksum files, NameNode corrupt-replica maps, storage states, block report queues, and low-redundancy counters. Changes are cluster-local and cleaned by shutdown.

## Dependencies and Integration Points

It integrates DataNode block reports, NameNode block manager corruption tracking, local filesystem checksum verification, storage failure metadata, and replication monitor accounting.

## Risks and Edge Cases

Risks include crashes on corrupt reports from non-holder DataNodes, treating failed storages as missing blocks incorrectly, stale block reports hiding under-replication, and local checksum exceptions masking other errors.

## Test Signals

Signals are `util.checkFiles` success after replica deletion, caught/ignored `ChecksumException`, successful file opens after corrupt marking, low-redundancy count `1`, missing-block count `0`, and no array-index failures.
