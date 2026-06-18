# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSlowDatanodeReport.java

Purpose: Verifies that DataNode peer outlier metrics propagate to NameNode slow-datanode reports and are visible through client-facing `DistributedFileSystem.getSlowDatanodeStats` and NameNode slow peer report strings.

Important APIs and types: `DataNode.getPeerMetrics().setTestOutliers`, `OutlierMetrics`, `DistributedFileSystem.getDataNodeStats`, `DistributedFileSystem.getSlowDatanodeStats`, `NameNode.getSlowPeersReport`, `GenericTestUtils.waitFor`, and slow-node DFS config keys.

Control flow: `@BeforeEach` creates a three-datanode cluster with peer stats enabled, low report interval, and one-node/one-sample outlier thresholds. `testSingleNodeReport` injects one outlier map entry from datanode 0 about datanode 1, waits until exactly one slow node appears, then asserts the report includes hostname and metric values. `testMultiNodesReport` injects two outlier entries from different reporters about datanodes 1 and 2, waits for two slow nodes, and checks report contents.

State and persistence behavior: State is in-memory peer metrics and NameNode aggregated slow-peer reports. There is no persistence check; cluster shutdown clears state.

Dependencies and integration points: Integrates datanode peer metrics, outlier detection thresholds, NameNode reporting aggregation, DFS client admin stats, and async report timing.

Risks and test signals: Uses long waits up to 180-200 seconds because reports are asynchronous. Passing signals slow peer metrics are consumed, aggregated, and surfaced with expected outlier values and host identities.
