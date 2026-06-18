# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractConcat.java

This class runs `AbstractContractConcatTest` against a non-secure Router RPC filesystem. It verifies that concat operations routed through RBF still satisfy HDFS contract expectations.

The setup starts the standard non-secure Router cluster, then performs a simple `getDefaultBlockSize(new Path("/"))` call through the Router-backed filesystem as an early readiness check. Teardown destroys the static cluster, and `createContract` returns `RouterHDFSContract`.

State and persistence are inherited from the mini HDFS cluster and mock mount mappings. Dependencies include `Path`, JUnit lifecycle annotations, and the HDFS contract framework.

Integration points are Router RPC concat forwarding, block-size metadata lookup, and active nameservice routing. Risks include concat restrictions around block sizes and same-filesystem constraints being tested only through inherited scenarios, and readiness being sampled through a random router. The test signal is non-secure Router compatibility with HDFS concat semantics.
