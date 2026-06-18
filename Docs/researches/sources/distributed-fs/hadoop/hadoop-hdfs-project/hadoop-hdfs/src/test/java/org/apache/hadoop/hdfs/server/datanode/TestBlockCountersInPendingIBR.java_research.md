# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockCountersInPendingIBR.java

## Purpose
This test validates DataNode metrics that count pending incremental block report entries by total and by block status: receiving, received, and deleted.

## Important APIs, Types, and Functions
- `BPServiceActor#getIbrManager().addRDBI` adds fake pending IBR entries.
- `ReceivedDeletedBlockInfo` and `BlockStatus` model pending block notifications.
- `DataNode#triggerBlockReport` with `BlockReportOptions#setIncremental(true)` sends the queued IBR.
- `verifyBlockCounters` asserts gauges `BlocksInPendingIBR`, `BlocksReceivingInPendingIBR`, `BlocksReceivedInPendingIBR`, and `BlocksDeletedInPendingIBR`.

## Control Flow and Behavior
The test starts a one-DataNode cluster with long heartbeat and block report intervals so no IBR is sent automatically. It spies on the DataNode-to-NameNode protocol, obtains a `BPServiceActor`, selects a storage from the dataset, adds three pending notifications with different statuses, verifies metrics before send, manually triggers an incremental block report, waits for one `blockReceivedAndDeleted` RPC, then verifies all pending counters return to zero.

## State and Persistence
Pending IBR state lives in the actor's `IncrementalBlockReportManager`. The backing cluster storage is real but the added blocks are fake notification entries rather than files created through DFS. Metrics are sampled from the live DataNode metrics record.

## Dependencies and Integration Points
The test integrates `MiniDFSCluster`, `InternalDataNodeTestUtils.spyOnBposToNN`, `FsDatasetSpi`, `DatanodeStorage`, block-report options, Mockito timeouts, and Hadoop metrics assertions.

## Risks and Edge Cases
It covers manual triggering with background reports disabled and verifies status-specific accounting. The fake block IDs are not backed by actual replicas, so the test is about queue counters and send/drain behavior rather than NameNode block acceptance.

## Test Signals
Signals are absence of pre-existing IBR RPCs, gauge values `3/1/1/1` before send, one observed `blockReceivedAndDeleted` RPC after trigger, and all four gauges returning to zero.
