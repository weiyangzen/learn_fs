# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractDelete.java

This class adapts `AbstractContractDeleteTest` to non-secure Router RPC. The inherited contract methods validate delete semantics through the Router, including recursive and non-recursive behavior where covered by the base suite.

Setup and teardown are standard `RouterHDFSContract.createCluster()` and `destroyCluster()`. `createContract` returns a new `RouterHDFSContract`.

State is the class-level mini federated cluster and test-created filesystem entries. Dependencies are the Hadoop contract test framework and JUnit 5. Integration points are Router path resolution, downstream namenode delete RPCs, mount-point behavior, and HDFS error propagation.

Risks include inherited tests not fully exercising deletes across multiple mounted namespaces and random router selection masking router-local cache problems. The test signal is baseline non-secure delete compatibility through RBF.
