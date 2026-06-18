<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractOpen.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractOpen.java

Purpose: Adapts open contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractOpen` extends `AbstractContractOpenTest`.
Control flow: Starts HDFSContract, runs inherited open/read tests, destroys cluster.
State and persistence behavior: Static cluster and files from inherited tests.
Dependencies and integration points: Integrates HDFS open/read semantics with contract suite.
Risks and edge cases: EOF, missing files, directory opens, and buffer sizes are contract-sensitive.
Test signals: Signals are inherited open and read assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractOpen.java -->
