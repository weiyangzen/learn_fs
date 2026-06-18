# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractGetFileStatusSecure.java

This class runs `AbstractContractGetFileStatusTest` through a secure Router RPC cluster. Setup uses `RouterHDFSContract.createCluster(true)` so inherited status tests execute with Kerberos, HTTPS-only HTTP policy, block tokens, and mock Router delegation-token support.

The contract factory returns `RouterHDFSContract`; teardown destroys the static cluster and security context. No local test methods override the inherited metadata suite.

State includes secure mini-cluster metadata, UGI security configuration, generated keytabs/keystores, and files/directories created by inherited tests. Dependencies are JUnit, Hadoop contract tests, and the secure Router harness.

Integration points are authenticated status RPCs, Router-to-namenode metadata forwarding, and permission/ownership visibility under security. Risks include global security state leakage and inherited coverage not checking every Router-specific federation state. The test signal is secure metadata lookup compatibility.
