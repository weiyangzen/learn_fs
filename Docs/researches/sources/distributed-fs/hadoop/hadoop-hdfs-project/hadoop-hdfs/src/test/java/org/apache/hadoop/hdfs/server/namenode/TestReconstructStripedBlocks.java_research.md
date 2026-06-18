# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReconstructStripedBlocks.java

Purpose: Integration-tests NameNode scheduling and accounting for erasure-coded striped block reconstruction. It covers missing internal blocks, busy source nodes, duplicate recovery suppression for the same block group, live replica counting with redundant/missing internal blocks, pending reconstruction metrics, storage-type/rack constraints, and excess/redundant block avoidance.

Important APIs and functions: Helpers include `initConf`, `doTestMissingStripedBlock`, `getNumberOfBlocksToBeErasureCoded`, and `writeStripedFile`. Tests use `MiniDFSCluster`, `DFSTestUtil.createStripedFile`, `BlockManagerTestUtil.getComputedDatanodeWork`, `BlockManager.countNodes`, `DatanodeDescriptor.getErasureCodeCommand`, `StripedBlockUtil.parseStripedBlockGroup`, and `StripedFileTestUtil.waitForReconstructionFinished`.

Control flow: Tests create EC files, remove DataNodes or mark them busy by filling pending replication streams, update BlockManager state, compute work, then inspect per-DataNode EC reconstruction commands and BlockManager counters. Later tests stop/restart DNs to produce redundant internal blocks, restart the NameNode to force block-report reconstruction of missing indices, and verify all block indices are eventually present.

State and persistence behavior: State lives in `BlockInfoStriped`, `DatanodeDescriptor` pending EC command queues, low-redundancy EC block group queues, pending reconstruction tracking, and block maps rebuilt after block reports or NameNode restart. The storage-type test uses persistent file storage policy `COLD` plus DataNode storage topology.

Dependencies and integration points: Integrates EC policies, BlockManager redundancy monitor logic, DataNodeManager removal/death handling, client located-block APIs, rack/storage-type placement, and client stats verification.

Risks: Reconstruction scheduling is sensitive to busy-node filtering, priority when only data-unit minimum sources remain, duplicate pending work, and internal block index coverage. Timing-based waits and heartbeat/redundancy intervals can be flaky if cluster scheduling stalls.

Test signals: Signals include exact number of EC tasks queued, pending reconstruction counts, source/target DN counts, `liveReplicas`, `excessReplicas`, `redundantInternalBlocks`, low-redundancy EC group counts, successful full index coverage, and successful reconstruction under insufficient preferred storage type.
