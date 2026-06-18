# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestIncrementalBlockReports.java

Purpose: This JUnit 5 integration test verifies DataNode incremental block report generation and NameNode/standby handling for received, deleted, duplicate, stale, and HA-delayed block notifications.

Important APIs/types/functions: `MiniDFSCluster`, `DataNode`, `BPOfferService`, `BPServiceActor`, `IncrementalBlockReportManager`, `ReceivedDeletedBlockInfo`, `StorageReceivedDeletedBlocks`, `DatanodeProtocolClientSideTranslatorPB.blockReceivedAndDeleted`, `HATestUtil`, `BlockManager.getPendingDataNodeMessageCount`, and `numCorruptReplicas`.

Control flow: The single-NameNode tests spy on the DataNode-to-NameNode protocol, inject fake received/deleted reports into a selected storage, and assert immediate versus heartbeat-delayed RPC behavior. The HA tests rebuild the cluster with two NameNodes, intercept IBRs sent to the standby with Mockito `doAnswer`, coordinate delayed delivery with a `Phaser`, write and append a file to create generation-stamp changes, wait for edit-log catch-up, then replay selected IBRs before failover.

State and persistence behavior: Tests mutate BPOS IBR queues, DataNode storage identity, real HDFS file blocks, standby pending DataNode message queues, and NameNode corrupt-replica accounting. Cluster instances are explicitly shut down and rebuilt for HA scenarios.

Dependencies and integration points: Coverage spans DataNode asynchronous IBR scheduling, block report RPCs, HA edit tailing, standby block-op queues, block generation stamps, and failover promotion behavior.

Risks and test signals: Signals are Mockito RPC counts, `sendImmediately()` clearing, pending-message counts reaching zero or three, and corrupt-replica counts after failover. Timing risks come from sleeps, phaser coordination, async RPC delivery, and standby catch-up assumptions.
