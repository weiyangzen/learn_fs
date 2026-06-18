<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractCreate.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractCreate.java

Purpose: Adapts create contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractCreate` extends `AbstractContractCreateTest` and creates `HDFSContract`.
Control flow: HDFSContract cluster brackets inherited create tests.
State and persistence behavior: Static contract cluster; created files live under contract test path until cleanup.
Dependencies and integration points: Integrates HDFS FileSystem with generic create semantics.
Risks and edge cases: Create flags, overwrite behavior, and parent handling depend on contract options.
Test signals: Signals are inherited create/open/status assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractCreate.java -->
