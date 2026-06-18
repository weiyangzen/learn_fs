# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractDeleteSecure.java

This secure variant runs `AbstractContractDeleteTest` through a Kerberized Router RPC cluster. It differs from the non-secure class only by calling `RouterHDFSContract.createCluster(true)`.

Control flow is class setup, inherited delete tests, and teardown. State includes the secure mini HDFS/RBF cluster, KDC and SSL artifacts, UGI security mode, mock state-store/delegation-token settings, and inherited test paths.

Dependencies are JUnit 5, Hadoop FS contract tests, `RouterHDFSContract`, and `SecurityConfUtil`. Integration points are authenticated Router RPC delete calls and downstream namenode authorization.

Risks are secure fixture cost and global security-state leakage; inherited delete tests may not cover all read-only mount or cross-namespace delete semantics. The test signal confirms secure Router delete behavior follows the HDFS contract.
