<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractLeaseRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractLeaseRecovery.java

Purpose: Adapts lease-recovery contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractLeaseRecovery` extends `AbstractContractLeaseRecoveryTest`.
Control flow: HDFSContract cluster wraps inherited lease recovery cases.
State and persistence behavior: State includes open files/leases created by base tests.
Dependencies and integration points: Integrates HDFS lease recovery with generic filesystem contracts.
Risks and edge cases: Lease timing and recovery can be asynchronous; cluster cleanup must close outstanding clients.
Test signals: Signals are inherited lease recovery and file visibility assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractLeaseRecovery.java -->
