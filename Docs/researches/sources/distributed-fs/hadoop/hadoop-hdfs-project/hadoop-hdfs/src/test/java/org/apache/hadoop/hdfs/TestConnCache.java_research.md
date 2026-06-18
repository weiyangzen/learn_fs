<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestConnCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestConnCache.java

Purpose: Verifies DFS client connection caching when repeatedly reading different offsets of a file served entirely by one DataNode.

Important APIs, types, and functions: `BlockReaderTestUtil`, `DFSClient`, `DFSInputStream`, `ClientContext.getFromConf`, `PeerCache`, `HdfsClientConfigKeys.DFS_CLIENT_CONTEXT`, and `DFS_CLIENT_SOCKET_TIMEOUT_KEY`.

Control flow: The test sets a unique client context and very long socket timeout, creates a single-DataNode helper cluster, writes a three-block test file, opens it through a raw `DFSClient`, and calls `pread` at multiple offsets plus one sequential read. After closing the stream and client, it checks that the peer cache size is one.

State and persistence behavior: Client-side connection cache state is keyed by the configured context name. The test file is written by `BlockReaderTestUtil` and authentic bytes are retained in memory for verification. The final assertion observes cached peer state after the stream closes.

Dependencies and integration points: Exercises block reader socket reuse, DFS input seeking/reading, `ClientContext` isolation, and peer-cache retention under a long timeout.

Risks: The helper `pread` appears to reduce `length` to zero before its verification loop, so the content verification loop as written does not iterate; the main signal is connection-cache size and successful reads. Changes to peer-cache eviction timing would affect the assertion, hence the large socket timeout and unique context.

Test signals: Success means multiple seeks/reads against one DataNode do not require multiple cached sockets and leave exactly one cached peer in the client context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestConnCache.java -->
