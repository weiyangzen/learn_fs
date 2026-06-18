<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractRootDirectory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractRootDirectory.java

Purpose: Adapts root-directory contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractRootDirectory` extends `AbstractContractRootDirectoryTest`.
Control flow: Cluster setup/teardown brackets inherited root directory tests.
State and persistence behavior: State is the root and test path of the HDFSContract cluster.
Dependencies and integration points: Integrates HDFS root behavior with contract suite.
Risks and edge cases: Root listing/status/deletion protections must match contract expectations.
Test signals: Signals are inherited root directory operation assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractRootDirectory.java -->
