# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSeekSecure.java

This secure variant runs `AbstractContractSeekTest` over a Kerberized Router RPC filesystem. It starts the secure cluster with `RouterHDFSContract.createCluster(true)` and returns `RouterHDFSContract`.

Inherited tests perform seek behavior assertions. State includes secure mini-cluster files, KDC state, SSL config, UGI security settings, and Router mount mappings.

Dependencies are the FS contract framework, JUnit, Router cluster harness, and MiniKdc-backed security utility. Integration points are authenticated file open/read/seek operations and block-token-enabled data access behind the Router.

Risks are secure fixture flakiness and limited coverage of token lifecycle during long reads. The test signal is secure seek/read compatibility for Router RPC.
