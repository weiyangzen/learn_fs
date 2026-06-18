<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestDFSWrappedIO.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestDFSWrappedIO.java

Purpose: Runs WrappedIO tests against HDFS, especially ByteBuffer positioned reads.
Important APIs/types/functions: `TestDFSWrappedIO` extends `TestWrappedIO` and overrides `createContract()` while using `HDFSContract.createCluster()/destroyCluster()`.
Control flow: Before all tests it starts the shared HDFS contract cluster, base tests run WrappedIO cases, and after all it destroys the cluster.
State and persistence behavior: State is the static HDFSContract cluster and test namespace.
Dependencies and integration points: Integrates `org.apache.hadoop.io.wrappedio.impl.TestWrappedIO` with HDFS contract.
Risks and edge cases: Failures can come from the generic WrappedIO suite or HDFS contract cluster lifecycle.
Test signals: Signals are inherited WrappedIO assertions for HDFS reads and positioned ByteBuffer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestDFSWrappedIO.java -->
