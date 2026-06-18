# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/RouterWebHDFSContract.java

`RouterWebHDFSContract` adapts Hadoop's `HDFSContract` to a Router WebHDFS endpoint. It is the shared contract factory for the WebHDFS Router tests.

Important APIs are `createCluster()`, `createCluster(Configuration)`, `destroyCluster()`, `getCluster()`, `getFileSystem()`, `getTestFileSystem()`, and `getScheme()`. The constructor adds `contract/webhdfs.xml` to the inherited HDFS contract configuration.

Control flow starts an HA two-nameservice `MiniRouterDFSCluster`, switches to independent datanodes, sets three datanodes per nameservice, starts the cluster and routers, registers namenodes, installs mock mount locations, transitions one namenode active per nameservice, and waits for active namespaces. `getFileSystem()` builds a `webhdfs://<router-http-address>` URI from a random `RouterContext` and creates a WebHDFS `FileSystem`.

State is a static `MiniRouterDFSCluster`; no secure setup is included. Dependencies include `WebHdfsConstants`, `WebHdfsFileSystem`, `MiniRouterDFSCluster`, and JUnit assertions. Integration points are Router HTTP/WebHDFS, mock mount resolution, and the contract webhdfs XML. Risks include returning null on URI syntax errors, random router selection, and using only non-secure WebHDFS. Test signal is shared by all WebHDFS Router contract subclasses.
