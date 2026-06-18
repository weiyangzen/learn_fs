<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractConcat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractConcat.java

Purpose: Adapts concat contract tests to HDFS and verifies the cluster is usable after startup.
Important APIs/types/functions: `TestHDFSContractConcat` extends `AbstractContractConcatTest`; setup calls `getDefaultBlockSize()` after creating the cluster.
Control flow: Before all it starts HDFSContract and performs a simple FS operation, then inherited concat tests run and teardown destroys the cluster.
State and persistence behavior: Uses static contract cluster and inherited test files.
Dependencies and integration points: Integrates HDFS concat implementation with generic contract tests.
Risks and edge cases: Concat is sensitive to block sizes and file closure state; startup smoke operation catches early cluster failures.
Test signals: Signals are inherited concat tests plus successful default block size query.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractConcat.java -->
