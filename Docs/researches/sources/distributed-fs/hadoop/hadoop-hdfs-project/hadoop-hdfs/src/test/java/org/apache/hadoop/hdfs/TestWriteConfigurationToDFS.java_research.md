# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestWriteConfigurationToDFS.java

Purpose: Regression test for HDFS-1542, a deadlock between `Configuration.writeXml` holding the configuration monitor and `DFSOutputStream.DataStreamer` writing to DFS.

Important APIs and types: `Configuration.writeXml`, `MiniDFSCluster`, `FileSystem.create`, `OutputStream`, `IOUtils.cleanupWithLogger`, and JUnit `@Timeout`.

Control flow: `testWriteConf` creates a configuration with small 4096 block size, starts a one-datanode cluster, creates `/testWriteConf.xml`, stores a large `foobar` property around 500 KB, writes the configuration XML directly to an HDFS output stream, closes the stream and filesystem, and always cleans up resources in `finally`.

State and persistence behavior: The HDFS file `/testWriteConf.xml` contains serialized configuration XML only for the lifetime of the MiniDFSCluster. The main observable state is absence of timeout/deadlock rather than file contents.

Dependencies and integration points: Integrates Hadoop `Configuration` serialization, DFS client output stream, DataStreamer thread behavior, block creation, and close semantics.

Risks and test signals: The 60-second timeout is the primary failure detector. Passing signals writing large synchronized configuration XML to DFS no longer deadlocks with the DataStreamer path.
