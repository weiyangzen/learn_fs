<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractBulkDelete.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractBulkDelete.java

Purpose: Adapts generic bulk-delete contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractBulkDelete` extends `AbstractContractBulkDeleteTest` and overrides `createContract()`.
Control flow: Cluster setup/teardown bracket inherited bulk delete tests.
State and persistence behavior: State is the shared HDFSContract cluster and files created by inherited tests.
Dependencies and integration points: Integrates HDFS with bulk delete contract coverage.
Risks and edge cases: Bulk delete semantics must match HDFS capabilities advertised in contract options.
Test signals: Signals are inherited bulk delete result and error assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractBulkDelete.java -->
