<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractMkdir.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractMkdir.java

Purpose: Adapts mkdir contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractMkdir` extends `AbstractContractMkdirTest`.
Control flow: Creates HDFSContract cluster, runs inherited mkdir tests, tears down.
State and persistence behavior: Shared static cluster and contract test directory.
Dependencies and integration points: Integrates HDFS mkdir behavior with the contract suite.
Risks and edge cases: Parent creation, root handling, and existing-file collisions are key risks.
Test signals: Signals are inherited mkdir status and exception assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractMkdir.java -->
