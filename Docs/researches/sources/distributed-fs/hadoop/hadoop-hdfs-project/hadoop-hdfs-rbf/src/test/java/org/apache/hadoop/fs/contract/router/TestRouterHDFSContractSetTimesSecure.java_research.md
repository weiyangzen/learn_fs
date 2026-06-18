# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSetTimesSecure.java

This secure variant runs `AbstractContractSetTimesTest` over a Kerberized Router RPC filesystem. Setup calls `RouterHDFSContract.createCluster(true)` and teardown destroys the cluster/security context.

Inherited tests perform the timestamp behavior checks. The contract factory returns `RouterHDFSContract`.

State includes secure mini-cluster metadata, generated security artifacts, UGI state, and Router mount mappings. Dependencies are JUnit, Hadoop FS contract classes, and the secure Router contract harness.

Integration points are authenticated `setTimes` forwarding, downstream namenode permission checks, and status reads through the Router. Risks include fixture leakage and limited explicit coverage for cache propagation across multiple routers. The test signal is secure timestamp mutation compatibility.
