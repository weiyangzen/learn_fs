# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractRename.java

This class runs `AbstractContractRenameTest` against Router WebHDFS. It delegates lifecycle to `RouterWebHDFSContract` and returns that contract.

Inherited tests issue WebHDFS rename operations through the Router HTTP endpoint. State is the static WebHDFS mini cluster and test paths. Dependencies are JUnit and Hadoop contract tests.

Integration points are WebHDFS `RENAME`, Router mount resolution, downstream namenode rename, and HTTP error/result translation. Risks include inherited tests not exercising RBF cross-nameservice federation rename behavior and no secure WebHDFS variant. The signal is baseline non-secure rename compatibility for Router WebHDFS.
