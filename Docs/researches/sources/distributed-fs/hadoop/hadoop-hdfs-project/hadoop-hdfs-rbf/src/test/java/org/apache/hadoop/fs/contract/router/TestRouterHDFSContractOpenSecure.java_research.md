# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractOpenSecure.java

This secure variant runs `AbstractContractOpenTest` against a Kerberized Router RPC filesystem. It calls `RouterHDFSContract.createCluster(true)` and otherwise inherits all open/read test logic.

The contract factory returns `RouterHDFSContract`; teardown releases the mini cluster and security context. State includes secure mini-cluster data, generated keytabs and SSL config, UGI state, and inherited test files.

Dependencies include the Hadoop contract suite, `SecurityConfUtil`, MiniKdc, and Router RPC clients. Integration points are secure open/read forwarding, block-token-enabled data reads, and authenticated Router-to-namenode access.

Risks include secure test flakiness and insufficient direct coverage for token expiration or WebHDFS read differences. The test signal is that standard file open/read contract behavior works through a secure Router RPC endpoint.
