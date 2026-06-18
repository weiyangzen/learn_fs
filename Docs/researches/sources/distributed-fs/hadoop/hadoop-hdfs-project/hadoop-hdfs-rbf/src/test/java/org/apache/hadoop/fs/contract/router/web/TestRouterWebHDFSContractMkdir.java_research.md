# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractMkdir.java

This class runs `AbstractContractMkdirTest` through Router WebHDFS. Setup starts the non-secure WebHDFS Router cluster and teardown destroys it.

The only local behavior is `createContract(Configuration)`, returning `RouterWebHDFSContract`. Inherited tests drive WebHDFS `MKDIRS` behavior through the Router HTTP endpoint.

State is the static mini cluster and created directory metadata. Dependencies are JUnit, Hadoop contract tests, and Router WebHDFS. Integration points are WebHDFS directory operations, Router HTTP service, mount table resolution, and downstream HDFS directory creation.

Risks include HTTP-specific error mapping and lack of secure coverage. The test signal is non-secure mkdir compatibility via Router WebHDFS.
