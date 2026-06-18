# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractCreateSecure.java

This class runs `AbstractContractCreateTest` over a secure Router RPC filesystem. Its setup calls `RouterHDFSContract.createCluster(true)`, enabling the Kerberos and HTTPS settings from `SecurityConfUtil`.

Inherited test methods perform the actual create-contract assertions. The only local API is `createContract(Configuration)`, which returns a `RouterHDFSContract`. Teardown destroys both the mini cluster and security context.

State includes MiniKdc, generated keytabs/keystores, UGI global security configuration, router/namenode/datanode mini-cluster state, and files created by inherited tests. Dependencies are JUnit, `AbstractContractCreateTest`, and the secure Router contract harness.

The integration signal is that authenticated clients can create files through the Router and receive normal HDFS behavior. Risks include fixture flakiness, static security state leaking, and limited Router-specific assertions around delegation-token or per-nameservice authorization.
