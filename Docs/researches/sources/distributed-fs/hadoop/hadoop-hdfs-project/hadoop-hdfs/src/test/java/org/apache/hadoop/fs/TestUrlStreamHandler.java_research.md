<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestUrlStreamHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestUrlStreamHandler.java

Purpose: Validates Hadoop URL stream handler support for HDFS and file URLs while leaving unrelated protocols to default handlers.
Important APIs/types/functions: `TestUrlStreamHandler`, static `FsUrlStreamHandlerFactory`, `setupHandler()`, `testDfsUrls()`, `testFileUrls()`, and protocol handler tests.
Control flow: Before all tests, the JVM-global URL stream handler factory is installed. HDFS test creates a file through `FileSystem`, builds an `hdfs://` URL from cluster URI, opens it as a stream, and compares bytes. File test does the same for a local `file://` URL. HTTP/HTTPS/unknown protocols should return null handlers from the Hadoop factory.
State and persistence behavior: State includes a JVM-global URL handler factory that can be set only once, a MiniDFSCluster for HDFS URL testing, and a local temp file.
Dependencies and integration points: Integrates Java `URL`, Hadoop `FsUrlStreamHandlerFactory`, HDFS FileSystem, local FileSystem, and MiniDFSCluster.
Risks and edge cases: Global factory installation can conflict with other tests in the same JVM. Byte reads assume the first read returns all 1024 bytes. Local temp directory creation and cleanup must succeed.
Test signals: Signals are non-null URL streams, exact byte equality for HDFS and file URLs, and null handlers for http, https, and unknown protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestUrlStreamHandler.java -->
