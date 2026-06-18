# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractOpen.java

This class runs most of `AbstractContractOpenTest` through Router WebHDFS, but overrides two inherited directory-open tests as no-ops.

Setup and teardown use `RouterWebHDFSContract`. `createContract` returns the WebHDFS contract. `testOpenReadDir()` and `testOpenReadDirWithChild()` are intentionally empty because WebHDFS itself allows open-read on directories, so the generic contract expectation does not hold.

State is WebHDFS mini-cluster file state and static cluster state. Dependencies are JUnit, the Hadoop open contract suite, and Router WebHDFS. Integration points are WebHDFS `OPEN`, datanode read redirects, Router path resolution, and downstream HDFS reads.

Risks include reduced coverage for directory-open error behavior and WebHDFS-specific behavior diverging from RPC. The test signal is file-open compatibility through Router WebHDFS while documenting inherited cases that do not apply.
