# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/metrics/TestNNMetricFilesInGetListingOps.java

Purpose: validates the NameNodeActivity metric `FilesInGetListingOps`, which counts the number of file entries returned by getListing operations.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `DFSTestUtil.createFile`, `NameNodeRpcServer.getListing`, `HdfsFileStatus.EMPTY_NAME`, `MetricsAsserts.getMetrics`, and `MetricsAsserts.assertCounter`.

Control flow: setup starts a standard MiniDFSCluster with small block/checksum sizes and fast heartbeat/redundancy intervals. The test creates two files in `/tmp1` and two files in `/tmp2`, invokes the NameNode RPC `getListing` for `/tmp1`, and asserts the counter is 2. It then lists `/tmp2` and asserts the cumulative counter is 4.

State and persistence behavior: filesystem namespace state consists of four files across two directories. The metric is cumulative in the `NameNodeActivity` source and reflects RPC listing result sizes, not persistent metadata.

Dependencies and integration points: integrates NameNode RPC listing implementation, HDFS file creation, metrics2 counters, and direct test metrics assertions.

Risks and test signals: risk is undercounting or overcounting listed entries, especially with multiple calls. The cumulative counter checks after each directory listing provide simple exact signals.
