<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSClientExcludedNodes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSClientExcludedNodes.java

Purpose: Ensures DFSClient excludes failed DataNodes during writes without aborting unnecessarily, and later forgives excluded nodes after the configured expiry interval.

Important APIs, types, and functions: `MiniDFSCluster.stopDataNode/restartDataNode`, `FSDataOutputStream`, `FileSystem.create`, `HdfsClientConfigKeys.Write.EXCLUDE_NODES_CACHE_EXPIRY_INTERVAL_KEY`, `hflush`, `ThreadUtil.sleepAtLeastIgnoreInterrupts`, and `DataNodeProperties`.

Control flow: `testExcludedNodes` starts three DataNodes, stops a random one, creates a replicated file, writes a byte, and asserts close succeeds despite the single DataNode failure. `testExcludedNodesForgiveness` sets exclude cache expiry to 2.5 seconds, writes one block to all three DataNodes, stops two DataNodes to force exclusion, writes another block with one remaining node, restarts the two stopped nodes, waits longer than expiry, stops the last originally good node, and then writes/flushes/closes another block, expecting the forgiven nodes to be usable.

State and persistence behavior: The key state is the DFS client excluded-node cache across multiple block writes on the same output stream. DataNode lifecycle state changes in the cluster simulate failures and recoveries. No NameNode restart persistence is tested.

Dependencies and integration points: Integrates DFS client write pipeline selection, DataNode failure handling, exclude-cache expiry, block-size/checksum configuration, and MiniDFSCluster lifecycle controls.

Risks: The forgiveness test depends on wall-clock sleeps and DataNode restart timing. If expiry semantics or pipeline replacement policy changes, the test can become flaky. The first test uses a random DataNode index, though all three nodes are symmetric.

Test signals: Success means a single failed DataNode does not abort a write, and previously excluded but restarted DataNodes can re-enter the pipeline after cache expiry so later writes still succeed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSClientExcludedNodes.java -->
