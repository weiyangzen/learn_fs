# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRedudantBlocks.java

Purpose: Regression-tests processing of over-replicated and redundant internal blocks in an erasure-coded striped block group. The class name contains the same misspelling as the source file, but the behavior under test is redundant block cleanup plus reconstruction.

Important APIs and functions: `setup()` configures block size, short redundancy/heartbeat intervals, `SimulatedFSDataset`, a MiniDFSCluster, and an EC directory. `testProcessOverReplicatedAndRedudantBlock()` uses `DFSTestUtil.createStripedFile`, `cluster.injectBlocks`, `triggerBlockReports`, `triggerHeartbeats`, `BlockManager.countNodes`, and `StripedBlockUtil.parseStripedBlockGroup`.

Control flow: The test creates a full striped file, injects all but one internal block into the first DataNodes, reports them, then injects a duplicate internal block as a redundant copy. It triggers block reports and heartbeats so the NameNode deletes redundancy, then triggers reconstruction for the missing internal block and waits until live replicas reach full group size.

State and persistence behavior: State is transient BlockManager block-map membership for `BlockInfoStriped`, live replica counts, redundant internal block tracking, and DataNode simulated block reports. No fsimage/edit-log restart path is exercised.

Dependencies and integration points: Integrates EC located-block parsing, simulated DataNode storage, block reports, heartbeats, BlockManager redundancy cleanup, and reconstruction scheduling.

Risks: Redundant internal blocks can mask a missing index if counting tracks only live replica count rather than unique block indices. The test's waits depend on block reports/heartbeats being processed promptly.

Test signals: The final signal is that parsed internal block IDs form a set of exactly `groupSize` unique IDs after redundant deletion and reconstruction.
