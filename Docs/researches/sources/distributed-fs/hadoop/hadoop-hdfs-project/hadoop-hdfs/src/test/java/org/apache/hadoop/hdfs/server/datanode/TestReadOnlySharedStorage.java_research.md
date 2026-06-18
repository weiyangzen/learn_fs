# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestReadOnlySharedStorage.java

Purpose: This integration test verifies `READ_ONLY_SHARED` DataNode storage semantics: read-only replicas are returned as read locations but do not count as live replicas or corrupt replicas for replication accounting.

Important APIs/types/functions: `SimulatedFSDataset`, `DatanodeStorage.State.READ_ONLY_SHARED`, `MiniDFSCluster.dataNodeConfOverlays`, `cluster.injectBlocks`, `DFSClient.getLocatedBlocks`, `BlockManager.countNodes`, `NumberReplicas`, `BlockManagerTestUtil`, and `DFSTestUtil.waitForReplication`.

Control flow: Setup starts three simulated DataNodes, configures one DataNode storage as `READ_ONLY_SHARED`, creates a one-block file with replication one, identifies the normal and read-only nodes, injects the block into the read-only node, and waits for two locations. Tests then raise replication, stop the normal replica host to force recovery from a read-only source, and report a read-only replica as bad.

State and persistence behavior: The test mutates NameNode block maps, DataNode storage reports, simulated dataset block inventory, replication factor, and dead-node/corrupt-replica state. Read-only injected blocks are not counted as normal persistent replicas.

Dependencies and integration points: It covers storage-state propagation, client block-location responses, NameNode replication accounting, inter-DataNode replication from read-only replicas, and bad-block reporting.

Risks and test signals: Signals are location counts, live/corrupt/excess/low-redundancy counts, and successful replication restoration. Risks are retry-loop timing and reliance on simulated storage fidelity.
