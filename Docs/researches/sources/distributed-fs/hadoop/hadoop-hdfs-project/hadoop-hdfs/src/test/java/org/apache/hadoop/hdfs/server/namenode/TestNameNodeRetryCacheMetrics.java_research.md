# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRetryCacheMetrics.java

Purpose: Verifies NameNode retry cache metrics for non-idempotent RPC retries in an HA cluster when client responses are deliberately dropped.

Important APIs and functions: Setup enables `DFS_NAMENODE_ENABLE_RETRY_CACHE_KEY`, disables random failover order, and sets `DFS_CLIENT_TEST_DROP_NAMENODE_RESPONSE_NUM_KEY` to 2. It reads `RetryCacheMetrics` from `FSNamesystem.getRetryCache().getMetricsForTests`. `trySaveNamespace` enters safe mode, calls `saveNamespace`, then leaves safe mode.

Control flow: The test starts a simple HA topology with three DataNodes, transitions NameNode 0 to active, configures failover, and obtains a failover `DistributedFileSystem`. Initial metrics are zero. Saving namespace causes two dropped responses and subsequent retries, so cache hits become 2 and updates become 1. Closing the namesystem clears the retry cache and increments the cleared metric.

State and persistence behavior: The operation being retried, `saveNamespace`, persists namespace state, but the test focuses on retry cache counters. Cache state lives in the active namesystem and is cleared by `namesystem.close`.

Dependencies and integration points: Uses MiniDFSCluster HA topology, `HATestUtil`, client failover configuration, safe mode actions, HDFS client test fault injection, and IPC retry cache metrics. It validates client retry behavior against NameNode metric accounting.

Risks: The exact hit/update counts depend on the configured response drop count and retry behavior. Calling `namesystem.close` directly is a strong lifecycle action and assumes metrics remain readable after close.

Test signals: Passing requires metrics `(0,0,0)` initially, `(2,0,1)` after a retried save namespace, and `(2,1,1)` after namesystem close.
