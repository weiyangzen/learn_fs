<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSafeMode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSafeMode.java

Purpose: Adapts safe-mode contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractSafeMode` extends `AbstractContractSafeModeTest`.
Control flow: Starts HDFSContract, runs inherited safe-mode interface tests, and destroys cluster.
State and persistence behavior: Static cluster safe-mode state is manipulated by inherited tests.
Dependencies and integration points: Integrates HDFS safe mode APIs with generic filesystem contract tests.
Risks and edge cases: Safe mode transitions can be timing-sensitive and must leave the cluster usable afterward.
Test signals: Signals are inherited safe-mode enter/leave and operation behavior assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSafeMode.java -->
