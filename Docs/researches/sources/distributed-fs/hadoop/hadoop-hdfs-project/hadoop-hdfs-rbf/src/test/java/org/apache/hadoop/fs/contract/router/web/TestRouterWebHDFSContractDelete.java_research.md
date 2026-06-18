# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractDelete.java

This class runs `AbstractContractDeleteTest` over Router WebHDFS. It delegates setup/teardown to `RouterWebHDFSContract` and returns that contract from `createContract`.

Inherited tests issue delete operations through the WebHDFS client and Router HTTP service. State is mini-cluster file state and static contract state. Dependencies are JUnit, Hadoop contract tests, and Router WebHDFS client integration.

Integration points are WebHDFS `DELETE`, Router mount resolution, downstream namenode deletion, and error propagation over HTTP. Risks include HTTP status mapping differences versus RPC exceptions and missing secure WebHDFS coverage. The test signal is non-secure delete compatibility via Router WebHDFS.
