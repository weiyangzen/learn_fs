<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractDelete.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractDelete.java

Purpose: Adapts delete contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractDelete` extends `AbstractContractDeleteTest`.
Control flow: Cluster setup/teardown surrounds inherited delete tests.
State and persistence behavior: Shared HDFSContract cluster and inherited namespace.
Dependencies and integration points: Integrates HDFS delete semantics with contract suite.
Risks and edge cases: Recursive and missing-path delete semantics must align with advertised contract.
Test signals: Signals are inherited delete behavior assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractDelete.java -->
