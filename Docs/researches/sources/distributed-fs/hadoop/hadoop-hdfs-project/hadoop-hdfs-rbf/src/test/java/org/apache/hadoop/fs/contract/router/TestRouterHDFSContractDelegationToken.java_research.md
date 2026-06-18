# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractDelegationToken.java

This class extends `AbstractContractGetFileStatusTest` but adds an explicit secure Router delegation-token test. It starts a secure Router cluster, returns `RouterHDFSContract` from `createContract`, and destroys the cluster afterward.

The local `testRouterDelegationToken()` obtains the Router-backed `FileSystem`, casts it to `DistributedFileSystem`, calls `getDelegationToken(SecurityConfUtil.getRouterUserName())`, and asserts that the token is not null. This checks that the Router's configured delegation-token secret manager can issue tokens to DFS clients in the secure contract environment.

State includes the secure mini cluster, mock delegation-token manager, KDC artifacts, and the DFS client token cache. Dependencies include `DistributedFileSystem`, Hadoop security `Token`, `DelegationTokenIdentifier`, JUnit assertions, and `SecurityConfUtil`.

Integration points are Router RPC security, the RBF secret-manager configuration, DFS client token APIs, and Kerberos login context. Risks include only checking token issuance, not renewal/cancel or persistence across Router restarts; it also relies on a mock secret manager rather than the default ZooKeeper implementation. Test signal is a direct smoke test for secure Router delegation-token availability.
