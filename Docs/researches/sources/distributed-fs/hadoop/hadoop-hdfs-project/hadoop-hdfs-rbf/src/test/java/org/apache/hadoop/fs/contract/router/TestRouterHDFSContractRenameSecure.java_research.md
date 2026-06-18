# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRenameSecure.java

This secure variant runs `AbstractContractRenameTest` over a Kerberized Router RPC filesystem. It initializes the secure cluster with `RouterHDFSContract.createCluster(true)` and returns `RouterHDFSContract` from the contract factory.

State includes static Router cluster state, MiniKdc, generated keytabs/keystores, secure UGI settings, and test paths. Dependencies include the Hadoop contract suite, JUnit, and `SecurityConfUtil`.

Integration points are authenticated Router rename RPCs, downstream namenode permission checks, and mount-table path resolution. Risks are similar to the non-secure rename class plus secure fixture leakage; it does not directly exercise the federation rename DistCp procedure or cross-nameservice policy options. The signal is secure baseline rename compatibility through Router RPC.
