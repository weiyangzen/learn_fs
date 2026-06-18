<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractGetFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractGetFileStatus.java

Purpose: Adapts get-file-status contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractGetFileStatus` extends `AbstractContractGetFileStatusTest`.
Control flow: Starts contract cluster, runs inherited status tests, destroys cluster.
State and persistence behavior: Static cluster and test paths.
Dependencies and integration points: Integrates HDFS `FileStatus` behavior with generic contract tests.
Risks and edge cases: Owner, directory/file distinctions, and missing path exceptions are contract-sensitive.
Test signals: Signals are inherited status metadata and error assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractGetFileStatus.java -->
