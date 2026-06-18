# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeStatusMXBean.java

Purpose: Verifies the `NameNodeStatusMXBean` JMX surface mirrors live `NameNode` state and includes slow disk reporting when DataNode disk profiling reports an outlier.

Important APIs and functions: Tests query the platform `MBeanServer` for `Hadoop:service=NameNode,name=NameNodeStatus`. Attributes checked include `NNRole`, `State`, `HostAndPort`, `SecurityEnabled`, `LastHATransitionTime`, `BytesWithFutureGenerationStamps`, `SlowPeersReport`, and `SlowDisksReport`. Slow disk setup uses `DataNode.getDiskMetrics().addSlowDiskForTesting`.

Control flow: The first test starts a cluster, retrieves the NameNode, reads JMX attributes, and compares every value to the corresponding NameNode getter. The slow-disks test enables DataNode file IO profiling and a short outlier report interval, injects a slow disk path into the single DataNode, waits until `DatanodeManager.getSlowDisksReport` is non-null, then compares and inspects the JMX value.

State and persistence behavior: State is runtime metrics and management data, not persistent namespace data. Slow disk state is injected into DataNode metrics and propagated to NameNode/DatanodeManager reports.

Dependencies and integration points: Integrates JMX, MiniDFSCluster, DatanodeManager, DataNode disk metrics, DFS profiling configuration, GenericTestUtils polling, and NameNode status getters.

Risks: Slow disk propagation is asynchronous and relies on polling up to 100 seconds. JMX object names and attribute names are API-like contracts; renaming them breaks the test. Injected path matching is string-based.

Test signals: Passing requires JMX attributes exactly matching live NameNode getters, slow disk report becoming available, and the JMX slow disk report containing the injected slow volume path.
