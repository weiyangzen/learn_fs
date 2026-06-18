# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSetTimes.java

This class runs `AbstractContractSetTimesTest` against a non-secure Router RPC filesystem. The inherited suite checks modification/access time updates and expected metadata behavior.

The local code follows the standard contract adapter pattern: class-level Router cluster startup, class-level teardown, and `createContract(Configuration)` returning `RouterHDFSContract`.

State is filesystem metadata in the mini HDFS cluster and static Router cluster state. Dependencies are JUnit and Hadoop contract tests. Integration points are Router RPC forwarding for `setTimes`, status reads after mutation, and mount resolution.

Risks include inherited tests not covering all federation cache-refresh edge cases or multiple routers observing the changed metadata. The test signal is baseline non-secure timestamp mutation compatibility through RBF.
