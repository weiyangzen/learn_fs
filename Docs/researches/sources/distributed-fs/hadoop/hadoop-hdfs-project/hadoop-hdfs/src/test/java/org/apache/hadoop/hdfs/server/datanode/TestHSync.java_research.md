# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestHSync.java

Purpose: integration-tests HDFS `hflush`/`hsync` semantics and DataNode `FsyncCount` metrics, including append, exact block boundaries, SequenceFile wrappers, and replicated pipelines.

Important APIs and types: `MiniDFSCluster`, `FSDataOutputStream`, `DistributedFileSystem`, `CreateFlag.SYNC_BLOCK`, `SequenceFile.Writer`, `RandomDatum`, `DefaultCodec`, `AppendTestUtil`, and metrics assertions against DataNode `FsyncCount`.

Control flow: `checkSyncMetric` reads each DataNode metric record. `testHSync` and `testHSyncWithAppend` call `testHSyncOperation`, which creates or appends a SYNC_BLOCK file, verifies `hflush` and empty `hsync` do not increment, writes data, verifies each `hsync` increments, verifies close increments for SYNC_BLOCK, then repeats without SYNC_BLOCK where close does not sync. `testHSyncBlockBoundary` writes exactly one block, observes sync on full-block `hflush`, then verifies further sync and close increments. `testSequenceFileSync` wraps an output stream in `SequenceFile.Writer`, checks writer `hflush` versus `hsync`, append plus `hsync`, writer close, and stream close. `testHSyncWithReplication` writes with replication 3 and verifies all three DNs increment on each `hsync`.

State and persistence behavior: files are written to a mini HDFS cluster and DataNode metrics persist for cluster lifetime. Integration points include DFS output stream flags, append path, sync-block packet handling, SequenceFile delegation, and replicated DataNode pipelines. Risks include metric naming stability and cleanup through explicit cluster shutdown. Signals are exact `FsyncCount` values after each operation.
