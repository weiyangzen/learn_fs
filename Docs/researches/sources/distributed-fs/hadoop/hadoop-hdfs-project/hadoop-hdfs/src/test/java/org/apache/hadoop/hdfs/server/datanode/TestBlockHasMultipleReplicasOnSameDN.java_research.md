# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockHasMultipleReplicasOnSameDN.java

## Purpose
This test verifies NameNode behavior when a single DataNode reports the same block on multiple storages. The expected behavior is that excess replicas on the same DataNode do not inflate block location counts or break block reports.

## Important APIs, Types, and Functions
- `MiniDFSCluster` is started with two DataNodes.
- `DFSTestUtil.createFile` creates a replicated multi-block file.
- `DFSClient#getLocatedBlocks` retrieves observed block locations.
- `BlockListAsLongs.encode`, `StorageBlockReport`, and `BlockReportContext` build a fake full block report containing duplicate storage reports from one DataNode.
- `NameNodeRpc#blockReport` submits that synthetic report.

## Control Flow and Behavior
The test writes a five-block file with replication equal to the two DataNodes. It obtains the located blocks, creates finalized replica objects for the blocks, then builds one identical `BlockListAsLongs` per storage volume on DataNode 0. It sends a block report in which each DataNode storage reports the same block set. After the report, it fetches block locations again and asserts that each block still has two locations with distinct DataNode UUIDs.

## State and Persistence
The cluster has real block files and block metadata. The synthetic report is not created from actual duplicate files on disk; it is a protocol-level report meant to exercise NameNode replica accounting.

## Dependencies and Integration Points
The test exercises NameNode block report processing, DataNode registrations, storage IDs from `FsDatasetSpi.FsVolumeReferences`, `FinalizedReplica`, `BlockListAsLongs`, and DFS client located-block reporting.

## Risks and Edge Cases
The key edge case is duplicate block sightings under one DataNode identity but different storage IDs. The test guards against over-counting replicas and against assertions in NameNode block report processing.

## Test Signals
Signals are successful synthetic block report submission and post-report located blocks with exactly two replicas on two distinct DataNodes for every block.
