<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddOverReplicatedStripedBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddOverReplicatedStripedBlocks.java

Purpose: tests NameNode handling of over-replicated erasure-coded striped block groups, including partial groups, corrupt internal blocks, and a disabled missing-block scenario.

Important APIs/types/functions: uses default `ErasureCodingPolicy`, `MiniDFSCluster`, `SimulatedFSDataset`, `DFSTestUtil.createStripedFile()`, `LocatedStripedBlock`, `BlockInfoStriped`, `BlockManager.findAndMarkBlockAsCorrupt()`, `cluster.injectBlocks()`, block reports, and heartbeats.

Control flow: setup enables EC on `/striped`, configures simulated storage, short heartbeat/redundancy intervals, and disables replication streams. Tests create striped files, inject duplicate internal blocks into extra DataNodes, trigger block reports/heartbeats so the NameNode schedules invalidations, and verify located striped blocks contain the expected number of live internal blocks. Corrupt-block coverage marks one internal block corrupt and verifies redundant copies are not deleted before reconstruction.

State and persistence: state is in the NameNode block map, corrupt replica map, over-replication invalidation queues, and DataNode simulated block reports. No restart persistence is exercised.

Dependencies and integration points: covers EC block-group accounting, block reports, heartbeat invalidations, corrupt replica tracking, and `StripedFileTestUtil.verifyLocatedStripedBlocks()`.

Risks and test signals: risks are deleting needed redundant EC blocks when a block is corrupt/missing, or retaining excess replicas for complete groups. Signals are located block indices/locations counts and corrupt replica counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddOverReplicatedStripedBlocks.java -->
