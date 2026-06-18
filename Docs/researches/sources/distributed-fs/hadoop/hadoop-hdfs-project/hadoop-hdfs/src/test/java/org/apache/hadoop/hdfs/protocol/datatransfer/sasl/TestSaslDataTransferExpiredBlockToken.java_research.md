<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestSaslDataTransferExpiredBlockToken.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestSaslDataTransferExpiredBlockToken.java

Purpose: Verifies SASL data-transfer clients can recover from expired block tokens for normal sequential reads, positioned reads, and hedged positioned reads.

Important APIs/types/functions: `SecurityTestUtil.setBlockTokenLifetime`, `SecurityTestUtil.isBlockTokenExpired`, `DFSInputStream.getAllBlocks`, `FSDataInputStream.read`, positioned `read(long, byte[], int, int)`, `HedgedRead.THREADPOOL_SIZE_KEY`, and `Retry.WINDOW_BASE_KEY`.

Control flow: `before` creates random two-block data, starts a secure three-DataNode cluster, writes `/file1`, then shortens block token lifetime to one second. Each test opens a new client `FileSystem`, waits until cached block tokens in the wrapped `DFSInputStream` expire, then reads the full file through a different path: sequential `blockSeekTo`, positioned byte-range fetch, or hedged fetch. Read bytes are compared to original random data.

State and persistence behavior: Persists random file data in HDFS and mutates the NameNode block token secret manager lifetime. Each test shuts down its cluster.

Dependencies and integration points: Covers SASL data transfer, block-token renewal/retry paths, positioned reads, and hedged read client configuration.

Risks: Waiting for expiration polls every 100 ms and depends on token timestamp behavior. Setting `Retry.WINDOW_BASE_KEY` to `Integer.MAX_VALUE` in one client changes retry timing substantially.

Test signals: Passing means expired cached block tokens are refreshed or retried successfully without corrupting read results across all targeted read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestSaslDataTransferExpiredBlockToken.java -->
