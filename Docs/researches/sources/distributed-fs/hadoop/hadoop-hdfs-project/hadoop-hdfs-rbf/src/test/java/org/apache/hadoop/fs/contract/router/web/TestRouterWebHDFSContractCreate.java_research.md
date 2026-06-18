# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractCreate.java

This class runs `AbstractContractCreateTest` against Router WebHDFS. It starts the WebHDFS Router mini cluster, returns `RouterWebHDFSContract`, and destroys the cluster after inherited tests finish.

State is the static WebHDFS contract cluster, independent datanodes, mock mount mappings, and files created by the base suite. Dependencies are JUnit and Hadoop contract tests.

Integration points are WebHDFS `CREATE` handling through the Router HTTP server, datanode write redirects, mount resolution, and HDFS create semantics. Risks include redirect and permission behavior differing from RPC tests, and no secure SPNEGO WebHDFS variant in this subset. The test signal is baseline create compatibility for Router WebHDFS.
