# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractConcat.java

This class runs `AbstractContractConcatTest` through Router WebHDFS. Setup starts `RouterWebHDFSContract.createCluster()` and performs a `getDefaultBlockSize(new Path("/"))` readiness probe through the WebHDFS filesystem.

The contract factory returns `RouterWebHDFSContract`; teardown destroys the static cluster. State is WebHDFS mini-cluster state and inherited test files. Dependencies are JUnit, `Path`, Hadoop contract tests, and Router WebHDFS.

Integration points are WebHDFS concat support, Router HTTP handling, redirect behavior, and downstream namenode concat. Risks include WebHDFS API differences from RPC and inherited tests not covering cross-nameservice concat constraints. The signal is non-secure Router WebHDFS concat contract compatibility.
