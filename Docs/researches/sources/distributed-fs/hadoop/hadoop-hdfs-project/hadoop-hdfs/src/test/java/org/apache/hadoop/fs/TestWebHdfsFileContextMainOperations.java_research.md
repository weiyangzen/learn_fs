<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestWebHdfsFileContextMainOperations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestWebHdfsFileContextMainOperations.java

Purpose: Runs FileContext main-operation tests through WebHDFS.
Important APIs/types/functions: `TestWebHdfsFileContextMainOperations` extends `FileContextMainOperationsBaseTest`; key methods are `clusterSetupAtBeginning()`, `setUp()`, `testUnsupportedSymlink()`, `testSetVerifyChecksum()`, and `ClusterShutdownAtEnd()`.
Control flow: Setup starts two-Datanode HDFS, builds a `webhdfs://` URI from the NameNode HTTP address, binds FileContext, and creates the user working directory. Per-test setup builds a randomized root URI under the WebHDFS endpoint. The checksum test writes data, enables verify checksum, reads it back, and compares bytes.
State and persistence behavior: Static cluster, WebHDFS URI, FileContext, and test data persist for the class. Per-test roots are randomized; symlink test is intentionally empty because support is partial.
Dependencies and integration points: Integrates WebHDFS scheme handling with the generic FileContext main-operation test suite.
Risks and edge cases: WebHDFS differs from direct HDFS for checksum timing and corrupted-block support. The empty symlink test documents unsupported behavior but provides no assertion.
Test signals: Signals are inherited FileContext operation results over WebHDFS and byte-for-byte checksum readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestWebHdfsFileContextMainOperations.java -->
