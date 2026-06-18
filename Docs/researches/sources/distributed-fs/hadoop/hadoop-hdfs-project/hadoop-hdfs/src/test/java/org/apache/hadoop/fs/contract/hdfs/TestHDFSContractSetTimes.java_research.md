<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSetTimes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSetTimes.java

Purpose: Adapts set-times contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractSetTimes` extends `AbstractContractSetTimesTest`.
Control flow: Starts HDFSContract, runs inherited timestamp mutation tests, destroys cluster.
State and persistence behavior: State includes file metadata timestamps in the MiniDFSCluster namespace.
Dependencies and integration points: Integrates HDFS mtime/atime behavior with contract tests.
Risks and edge cases: Timestamp precision and unsupported atime settings can cause contract mismatches.
Test signals: Signals are inherited setTimes metadata assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSetTimes.java -->
