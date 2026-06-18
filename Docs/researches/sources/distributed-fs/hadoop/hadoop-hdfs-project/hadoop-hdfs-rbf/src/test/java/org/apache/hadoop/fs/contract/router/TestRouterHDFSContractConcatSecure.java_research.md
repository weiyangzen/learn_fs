# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractConcatSecure.java

This secure variant runs `AbstractContractConcatTest` through a Kerberized Router RPC cluster. It starts the cluster with `RouterHDFSContract.createCluster(true)` and performs the same default-block-size readiness probe as the non-secure variant.

Control flow is class-level setup, inherited concat cases, and class-level teardown. State includes the static `MiniRouterDFSCluster`, MiniKdc artifacts, SSL configuration, and UGI security mode initialized by `SecurityConfUtil`. The contract factory returns `RouterHDFSContract`.

Dependencies are the Hadoop FS contract framework, Router security test utility, and the secure mini HDFS stack. Integration points are Router RPC concat, downstream namenode auth, block-token behavior, and mount resolution.

Risks include Kerberos/HTTPS fixture cost and inherited concat tests not covering all cross-nameservice rename/copy variants. Its test signal is that concat remains compatible with Router forwarding when secure authentication and block access controls are enabled.
