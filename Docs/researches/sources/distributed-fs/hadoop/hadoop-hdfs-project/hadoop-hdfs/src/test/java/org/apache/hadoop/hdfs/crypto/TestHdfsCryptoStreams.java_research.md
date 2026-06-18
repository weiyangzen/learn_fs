<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/crypto/TestHdfsCryptoStreams.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/crypto/TestHdfsCryptoStreams.java

Purpose: Adapts the generic `CryptoStreamsTestBase` suite to HDFS-backed streams.

Important APIs/types/functions: Extends `CryptoStreamsTestBase`; overrides `getOutputStream` and `getInputStream` to return `CryptoFSDataOutputStream` and `CryptoFSDataInputStream` wrapping `fs.create` and `fs.open`. Uses `CryptoCodec.getInstance`, `MiniDFSCluster`, `FileSystem.mkdirs`, and `FsPermission`.

Control flow: `init` starts a MiniDFS cluster and initializes the shared crypto codec. Each test method inherited from the base class gets a unique directory and file path in `setUp`, then base tests exercise crypto stream read/write behavior. `cleanUp` deletes the per-test directory, and `shutdown` stops the cluster.

State and persistence behavior: Persists encrypted stream bytes in HDFS files under unique `/pN/file` paths and deletes them after each test.

Dependencies and integration points: Connects Hadoop crypto stream wrappers to HDFS `FSDataInputStream`/`FSDataOutputStream` implementations, verifying the generic crypto contract over distributed storage.

Risks: Actual test methods are inherited, so failures may be reported from the base class. The test depends on a configured crypto codec being available for the current Hadoop configuration.

Test signals: Passing inherited tests indicate HDFS-backed crypto streams honor base stream semantics for buffering, encryption/decryption, position, and close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/crypto/TestHdfsCryptoStreams.java -->
