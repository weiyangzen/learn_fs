<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractUnbuffer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractUnbuffer.java

Purpose: Adapts unbuffer contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractUnbuffer` extends `AbstractContractUnbufferTest`.
Control flow: Contract cluster wraps inherited unbuffer tests.
State and persistence behavior: State includes streams and client resources created by the base tests.
Dependencies and integration points: Integrates HDFS stream unbuffer support with generic contract coverage.
Risks and edge cases: Resource cleanup and capability advertisement must be consistent.
Test signals: Signals are inherited unbuffer support and post-unbuffer read behavior assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractUnbuffer.java -->
