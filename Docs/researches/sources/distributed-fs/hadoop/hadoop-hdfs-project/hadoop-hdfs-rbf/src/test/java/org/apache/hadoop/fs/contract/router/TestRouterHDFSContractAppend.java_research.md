# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractAppend.java

This test class runs Hadoop's shared `AbstractContractAppendTest` suite against the Router RPC `FileSystem`. It provides no local test methods; inherited contract tests drive append behavior.

`@BeforeAll createCluster()` starts a non-secure HA federated Router cluster through `RouterHDFSContract.createCluster()`. `@AfterAll teardownCluster()` destroys it. `createContract(Configuration)` returns a new `RouterHDFSContract`, which supplies a random Router-backed `DistributedFileSystem`.

State is class-level mini-cluster state owned by `RouterHDFSContract`. Dependencies are JUnit 5 lifecycle annotations and the Hadoop FS contract framework. Integration points are Router RPC append forwarding, mock mount locations, active nameservice discovery, and HDFS append semantics behind the router.

Risks are mostly inherited: append tests can pass through one random router while another router is broken, and static cluster reuse means teardown failures affect later suites. The test signal is coverage that Router RPC preserves HDFS append contract behavior in a non-secure federated cluster.
