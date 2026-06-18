# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractCreate.java

This class runs `AbstractContractCreateTest` against the non-secure Router RPC filesystem. It validates inherited file creation behavior such as overwrite, parent handling, stream semantics, and metadata expectations through RBF.

Setup starts the standard two-nameservice HA `MiniRouterDFSCluster` via `RouterHDFSContract.createCluster()`. Teardown calls `RouterHDFSContract.destroyCluster()`. `createContract` returns `RouterHDFSContract`.

State lives in the static mini cluster, its mock mount locations, and the files/directories created by inherited tests. Dependencies are JUnit 5 lifecycle hooks and Hadoop's contract test base.

Integration points are Router RPC create forwarding, mount-table path resolution, active namenode selection, and HDFS write pipeline creation behind the Router. Risks include random-router coverage gaps and inherited tests mainly validating general HDFS semantics rather than Router-specific multi-destination edge cases. The test signal is baseline non-secure create compatibility for Router-backed HDFS.
