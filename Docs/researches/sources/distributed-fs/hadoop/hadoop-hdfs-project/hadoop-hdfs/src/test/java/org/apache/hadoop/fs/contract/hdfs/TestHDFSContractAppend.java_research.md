<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractAppend.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractAppend.java

Purpose: Adapts generic append contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractAppend` extends `AbstractContractAppendTest` and returns `new HDFSContract(conf)`.
Control flow: Starts HDFSContract before the class, executes inherited append tests, and destroys the cluster afterward.
State and persistence behavior: Uses static contract cluster and inherited test paths.
Dependencies and integration points: Integrates HDFS with the append contract suite.
Risks and edge cases: Append behavior depends on contract XML features and MiniDFSCluster lifecycle.
Test signals: Signals are inherited append success/error semantics on HDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractAppend.java -->
