<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractRename.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractRename.java

Purpose: Adapts rename contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractRename` extends `AbstractContractRenameTest`.
Control flow: Starts the HDFSContract cluster, runs inherited rename cases, then destroys it.
State and persistence behavior: Shared cluster namespace under the contract test path.
Dependencies and integration points: Integrates HDFS rename behavior with generic contracts.
Risks and edge cases: Overwrite, directory, root, and cross-path rename semantics are high-risk contract areas.
Test signals: Signals are inherited rename existence/status/error assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractRename.java -->
