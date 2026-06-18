# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeECN.java

## Purpose
`TestDataNodeECN` verifies that enabling the DataNode pipeline ECN configuration produces a non-disabled `PipelineAck.ECN` mode in a running DataNode.

## Important APIs, Types, and Functions
- `DFSConfigKeys.DFS_PIPELINE_ECN_ENABLED` controls the feature.
- `MiniDFSCluster` starts the DataNode.
- `DataNode#getECN` returns the selected `PipelineAck.ECN` value.

## Control Flow and Behavior
The test sets pipeline ECN enabled in a plain `Configuration`, starts a one-DataNode MiniDFSCluster, gets the first DataNode's ECN mode, and asserts it is not `PipelineAck.ECN.DISABLED`. The cluster is shut down in a finally block.

## State and Persistence
Only transient MiniDFSCluster state is created. No files are written.

## Dependencies and Integration Points
The test integrates DataNode startup configuration with the data-transfer protocol's `PipelineAck.ECN` enum.

## Risks and Edge Cases
It covers the positive enablement path only. It does not assert a specific non-disabled mode or test the disabled default.

## Test Signals
The signal is a single non-equality assertion that `getECN()` does not return `DISABLED` when the feature flag is true.
