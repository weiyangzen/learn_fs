# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRootDirectory.java

This class adapts `AbstractContractRootDirectoryTest` to the non-secure Router RPC filesystem. It starts the standard Router cluster and returns `RouterHDFSContract`, but overrides several inherited root-directory tests as no-ops.

The disabled methods are `testListEmptyRootDirectory`, `testRmEmptyRootDirNonRecursive`, `testRecursiveRootListing`, `testRmRootRecursive`, and `testRmEmptyRootDirRecursive`. The reason is that the Router root contains mount points, so generic assumptions about an empty root or deleting root do not apply to RBF.

State is the mini federation root mapping installed by `MiniRouterDFSCluster.installMockLocations()`. Dependencies are JUnit lifecycle hooks and the base contract suite. Integration points are Router root listing and mount-point semantics.

The main risk is reduced coverage for root behavior; disabling tests is appropriate for RBF but can hide regressions in root listing/deletion protections unless covered elsewhere. The test signal is explicit documentation that generic root-directory expectations differ for Router federation.
