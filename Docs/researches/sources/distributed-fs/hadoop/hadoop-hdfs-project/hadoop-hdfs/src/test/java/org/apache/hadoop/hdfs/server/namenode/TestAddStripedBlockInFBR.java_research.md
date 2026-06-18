<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddStripedBlockInFBR.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddStripedBlockInFBR.java

Purpose: verifies that full block reports can establish NameNode block-to-DataNode mappings for striped blocks when an incremental block report is ignored.

Important APIs/types/functions: uses `MiniDFSCluster`, default EC policy, Mockito spy on `BlockManager`, `Whitebox.setInternalState()`, `processIncrementalBlockReport()`, `cluster.triggerBlockReports()`, `BlockInfoStriped`, and `NumberReplicas`.

Control flow: setup starts `groupSize` DataNodes and enables EC. The test spies the block manager and suppresses one DataNode's incremental block report processing, creates replicated files plus one EC file, then repeatedly triggers full block reports until the striped block has zero excess replicas and `groupSize` live replicas.

State and persistence: state is the live in-memory block map updated by full block reports. No edit-log or fsimage persistence is exercised.

Dependencies and integration points: covers DataNode FBR handling, EC block-group replica accounting, Mockito/Whitebox internals, and `GenericTestUtils.waitFor()`.

Risks and test signals: risks are relying only on IBRs for striped mappings or marking FBR-added striped replicas as excess. Signal is `NumberReplicas.liveReplicas() == groupSize` and `excessReplicas() == 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddStripedBlockInFBR.java -->
