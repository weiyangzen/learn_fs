# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractMkdirSecure.java

This secure variant runs `AbstractContractMkdirTest` against a Kerberized Router RPC filesystem. It delegates setup to `RouterHDFSContract.createCluster(true)` and teardown to `destroyCluster()`.

Inherited tests perform the directory behavior assertions. The contract factory returns `RouterHDFSContract`, so all operations route through a random Router RPC endpoint.

State includes MiniKdc artifacts, UGI security mode, Router and namenode keytab settings, SSL config, and test-created directories. Dependencies are JUnit, the Hadoop contract suite, and `SecurityConfUtil` through `RouterHDFSContract`.

Integration points are secure Router RPC `mkdirs`, downstream namenode authentication, and mount-table resolution. Risks are fixture flakiness and inherited tests not covering all permission-denied cases specific to RBF. Test signal is secure directory operation compatibility.
