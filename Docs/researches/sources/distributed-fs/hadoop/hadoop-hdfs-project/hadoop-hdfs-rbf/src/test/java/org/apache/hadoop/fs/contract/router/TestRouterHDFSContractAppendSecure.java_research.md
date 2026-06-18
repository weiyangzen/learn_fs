# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractAppendSecure.java

This class runs the inherited append contract suite over a secure Router RPC cluster. It is structurally identical to the non-secure append test, but calls `RouterHDFSContract.createCluster(true)`.

The lifecycle delegates to `RouterHDFSContract` and `SecurityConfUtil`: MiniKdc, HTTPS-only DFS HTTP policy, block access tokens, authenticated data transfer, Router principals, and mock delegation-token manager are initialized before inherited append operations run. The contract factory returns `RouterHDFSContract`.

State is the static federated mini cluster plus process-wide UGI Kerberos state. Dependencies are JUnit 5, `AbstractContractAppendTest`, `RouterHDFSContract`, and `SecurityConfUtil`.

The key integration signal is that Router RPC append behavior works when Hadoop security is enabled. Risks include MiniKdc flakiness, global security settings affecting adjacent tests, and inherited append cases not explicitly checking every token-renewal path. This test is valuable because append combines write pipeline behavior with authentication and block tokens.
