# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRename.java

This class runs `AbstractContractRenameTest` over a non-secure Router RPC filesystem. It verifies inherited rename behavior through RBF, including file and directory rename cases covered by the base contract suite.

Setup and teardown use `RouterHDFSContract.createCluster()` and `destroyCluster()`. `createContract` returns a Router HDFS contract.

State is class-level mini-cluster state plus filesystem entries created during inherited rename tests. Dependencies are JUnit and the Hadoop contract framework. Integration points are Router rename forwarding, path resolution through mock mount locations, active namenode selection, and HDFS rename semantics.

Risks include inherited tests generally covering same-filesystem renames, while RBF has additional cross-nameservice rename behavior configured separately by federation rename options. Random Router selection may miss per-router cache issues. The test signal is baseline non-secure rename compatibility through Router RPC.
