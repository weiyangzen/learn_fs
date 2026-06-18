# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractMkdir.java

This class runs `AbstractContractMkdirTest` against a non-secure Router RPC filesystem. Inherited tests verify directory creation, parent handling, idempotency, and error behavior as implemented through the Router.

Setup starts the standard federated Router cluster, teardown destroys it, and `createContract` returns `RouterHDFSContract`. No local test methods change the inherited suite.

State is the static `MiniRouterDFSCluster` plus directories created by the base tests. Dependencies are JUnit 5 and Hadoop FS contract classes. Integration points are Router path resolution, downstream namenode `mkdirs`, and mock mount locations.

Risks include limited coverage of namespace-boundary directory creation and root mount behavior beyond inherited tests. The test signal is non-secure Router directory-creation contract compatibility.
