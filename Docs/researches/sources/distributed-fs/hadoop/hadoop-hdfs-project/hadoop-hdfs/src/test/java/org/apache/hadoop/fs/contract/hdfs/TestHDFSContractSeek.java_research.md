<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSeek.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSeek.java

Purpose: Adapts seek contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractSeek` extends `AbstractContractSeekTest`.
Control flow: HDFSContract lifecycle wraps inherited seek tests.
State and persistence behavior: State includes test files and input stream positions.
Dependencies and integration points: Integrates HDFS seek/read semantics with generic contracts.
Risks and edge cases: Boundary seeks, negative seeks, EOF, and closed-stream behavior are key risks.
Test signals: Signals are inherited seek position and read-content assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSeek.java -->
