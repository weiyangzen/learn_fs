# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractAppend.java

This class runs `AbstractContractAppendTest` against the Router WebHDFS filesystem. It starts the WebHDFS Router contract cluster, destroys it afterward, and returns `RouterWebHDFSContract`.

The inherited suite performs append behavior checks through `webhdfs://<router-http-address>`, not direct Router RPC. State is the static WebHDFS mini cluster and files created by inherited tests. Dependencies include JUnit, Hadoop contract tests, and WebHDFS client classes through the contract.

Integration points are Router HTTP service, WebHDFS operation translation, mount resolution, and downstream HDFS append. Risks include WebHDFS-specific redirect behavior and lack of secure WebHDFS coverage here. The test signal is non-secure append compatibility via Router WebHDFS.
