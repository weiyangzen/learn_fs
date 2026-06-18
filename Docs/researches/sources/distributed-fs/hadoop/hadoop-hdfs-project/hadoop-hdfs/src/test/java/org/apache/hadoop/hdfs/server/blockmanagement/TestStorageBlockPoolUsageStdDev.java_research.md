# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestStorageBlockPoolUsageStdDev.java

Purpose: this MiniDFSCluster test verifies that the NameNode's live-node JSON exposes `blockPoolUsedPercentStdDev` values that match the DataNode storage reports and `Util.getBlockPoolUsedPercentStdDev`.

Important APIs and types: `MiniDFSCluster`, `FileSystem`, `DFSTestUtil.createFile`, `DataNode`, `FSNamesystem`, `StorageReport`, `Util.getBlockPoolUsedPercentStdDev`, Jetty `JSON`, and HDFS capacity/block-size configuration keys.

Control flow: `setup` builds a five-DataNode cluster with three storages per DataNode and equal capacities. The test writes one single-block file to each DataNode using favored nodes and sizes 1000, 2000, 4000, 8000, and 16000 bytes. It triggers heartbeats, reads the NameNode live-node JSON, independently asks each DataNode dataset for storage reports for the current block pool, and asserts equality with a `0.01d` tolerance.

State and persistence: the cluster creates real temporary HDFS storage volumes. File placement is controlled by favored-node addresses so each DataNode gets a different block-pool usage distribution across its three storages. The observable state is propagated from DataNode datasets to NameNode heartbeat state and then serialized into live-node JSON.

Dependencies and integration points: this is an integration test across client write placement, DataNode storage accounting, heartbeat reporting, NameNode live-node aggregation, and JSON UI/JMX-style output. It assumes one block per file by keeping file sizes below the configured block size.

Risks: there is no explicit `@AfterEach` shutdown in this file, so cleanup relies on test harness behavior or JVM teardown if not handled elsewhere. Favored-node placement could become flaky if placement semantics change. The direct JSON cast assumes stable key types and the exact `DataNode.getDisplayName()` key used in `FSNamesystem.getLiveNodes()`.

Test signals: a failure indicates either standard deviation computation drift, heartbeat/report serialization mismatch, or a regression in storage-report visibility from DataNode to NameNode live-node output.
