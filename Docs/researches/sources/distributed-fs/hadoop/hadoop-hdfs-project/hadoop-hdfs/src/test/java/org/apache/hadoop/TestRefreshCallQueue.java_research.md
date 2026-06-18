<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/TestRefreshCallQueue.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/TestRefreshCallQueue.java

Purpose: Validates live NameNode IPC call queue refresh behavior and FairCallQueue queue-size reconfiguration in a MiniDFSCluster.
Important APIs/types/functions: `TestRefreshCallQueue`, `setUp(Class<?>)`, `MockCallQueue`, `canPutInMockQueue()`, `testRefresh()`, and `testRefreshCallQueueWithFairCallQueue()`.
Control flow: Setup picks a random NameNode RPC port, installs `ipc.<port>.callqueue.impl`, and starts the cluster. The first test verifies the mock queue is active, runs `DFSAdmin -refreshCallQueue`, then verifies RPC puts stop hitting the mock. The second starts with `FairCallQueue`, disables mini-cluster metrics mode to expose duplicate registration failures, calls `refreshCallQueue(config)`, and checks max queue size changes.
State and persistence behavior: The test mutates static counters for queue construction and puts, cluster lifecycle state, the default HDFS URI, and `DefaultMetricsSystem` mini-cluster mode. Persistence is limited to MiniDFSCluster metadata and metrics registrations during the test.
Dependencies and integration points: Integrates NameNode RPC server, `DFSAdmin`, `FileSystem.exists()`, `CommonConfigurationKeys` queue sizing, `FairCallQueue`, and metrics lifecycle.
Risks and edge cases: Random port selection can collide and has only five retries. Metrics mode restoration is crucial after failures. Static counters make parallel execution unsafe. The test assumes refresh swaps queues without dropping RPC availability.
Test signals: Successful signals are admin exit code 0, no new `MockCallQueue` construction after refresh, mock put counts no longer increasing, no duplicate `DecayRpcSchedulerMetrics2` source, and updated server max queue size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/TestRefreshCallQueue.java -->
