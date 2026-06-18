# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataTransferThrottler.java

Purpose: integration test for read-side DataNode transfer throttling controlled by `dfs.datanode.data.read.bandwidthPerSec`.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `DataXceiverServer#getReadThrottler`, `DFSTestUtil`, `Path`, `HdfsConfiguration`, and `Time.monotonicNow`.

Control flow: the test starts a default cluster, writes an 80 MiB file, waits for replication, and asserts the DataNode read throttler is null under default bandwidth 0. It reads the file unthrottled, sets read bandwidth to 8 MiB/s, restarts the DataNode with the new conf, verifies the throttler bandwidth, then reads the full file again and asserts elapsed time is at least roughly 10 seconds with a 1 second margin.

State and persistence behavior: the test persists one HDFS file across DataNode restart; throttle state is in the restarted `DataXceiverServer`. Integration points include DataNode restart, DataXceiver read path, configuration propagation, and client read helpers. Risks include wall-clock timing variability, slow CI environments, cache effects, and the confusing comment naming acceptable error as "1 milliseconds" while the value is 1000 ms. Test signals are throttler null/non-null state, configured bandwidth, full byte-count reads, and elapsed-time lower bound.
