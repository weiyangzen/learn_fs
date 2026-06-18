<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestClientBlockVerification.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestClientBlockVerification.java

Purpose: Verifies when `BlockReaderRemote` sends `Status.CHECKSUM_OK` back to the DataNode after client reads.

Important APIs/types/functions: Static `BlockReaderTestUtil`, Mockito `spy`/`verify`, `BlockReaderRemote.sendReadResult`, `Status.CHECKSUM_OK`, and `readAndCheckEOS`.

Control flow: `setupCluster` writes a 256 KiB file and stores the first `LocatedBlock`. Tests open spied remote readers for full-block, incomplete, partial-range, and unaligned-range reads. Full completion of the requested range must call `sendReadResult(CHECKSUM_OK)`; incomplete reads must not.

State and persistence behavior: Uses a shared MiniDFS cluster and file for all tests. The persistent signal is not filesystem mutation but the reader-to-DataNode verification message.

Dependencies and integration points: Integrates DFS client block reading, DataTransferProtocol checksum verification, and DataNode read-result signaling.

Risks: Mockito spies couple the test to `BlockReaderRemote` internals. The shared static cluster means setup failure affects every test.

Test signals: Passing indicates checksum success is acknowledged exactly when the requested byte range is fully consumed, including unaligned checksum-boundary ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestClientBlockVerification.java -->
