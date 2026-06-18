# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractGetFileStatus.java

This class runs `AbstractContractGetFileStatusTest` over a non-secure Router RPC filesystem. It validates inherited file-status behavior such as metadata lookup, nonexistent paths, directory/file distinctions, and permission/ownership reporting as exposed through the Router.

The local code is only lifecycle and contract construction: `createCluster()`, `teardownCluster()`, and `createContract(Configuration)`. Cluster setup uses the standard non-secure `RouterHDFSContract` path.

State is the static mini cluster and HDFS metadata created by inherited tests. Dependencies are JUnit 5 and the Hadoop contract framework. Integration points are Router `getFileInfo`/status forwarding, mock mount resolution, and active namenode selection.

Risks include limited direct assertions for mount-table entries at root and random-router selection. The test signal is baseline status/metadata compatibility for non-secure RBF.
