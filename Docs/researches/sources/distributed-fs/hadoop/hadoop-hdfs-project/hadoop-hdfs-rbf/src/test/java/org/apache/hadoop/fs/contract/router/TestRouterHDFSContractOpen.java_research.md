# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractOpen.java

This class runs `AbstractContractOpenTest` through a non-secure Router RPC filesystem. It validates inherited open/read behavior, including file reads and expected exceptions for invalid open operations where the base suite defines them.

Setup starts a standard `RouterHDFSContract` cluster. Teardown destroys it. `createContract(Configuration)` returns `RouterHDFSContract`.

State is test-file data in the mini HDFS cluster and static Router cluster state. Dependencies are JUnit and the Hadoop contract framework. Integration points are Router open forwarding, block location/read pipeline setup, mount resolution, and active namenode selection.

Risks include random-router selection and inherited read tests not explicitly stressing observer reads, failover, or stale router caches. The test signal is baseline non-secure open/read compatibility for Router-backed HDFS.
