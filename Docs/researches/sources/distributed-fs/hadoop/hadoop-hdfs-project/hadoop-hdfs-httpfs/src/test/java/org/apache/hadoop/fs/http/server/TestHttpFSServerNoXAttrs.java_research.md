# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServerNoXAttrs.java

Purpose: Negative integration suite for HTTPFS when HDFS extended attributes are disabled. It verifies xattr REST operations are rejected by HDFS and reported through HTTPFS.

Important APIs/types/functions: `startMiniDFS`, `createHttpFSServer`, `getStatus`, `putCmd`, `MiniDFSCluster`, `DFS_NAMENODE_XATTRS_ENABLED_KEY`, `TestHttpFSServer.setXAttrParam`, `HttpFSAuthenticationFilter`, and Jetty webapp setup.

Control flow: setup mirrors the no-ACL test but explicitly disables `dfs.namenode.xattrs.enabled`. The test creates a file directly in MiniDFS, then sends `GETXATTRS`, `SETXATTR`, and `REMOVEXATTR` requests through HTTPFS. All three must return HTTP 500 and error payloads mentioning `RemoteException`, `XAttr`, and `rejected`.

State and persistence: uses per-test local HTTPFS config/secret files and a per-test MiniDFS cluster. It writes HDFS state for `/noXAttr/file` and uses `nnConf` as the direct cluster client configuration.

Dependencies/integration: integrates HTTPFS request handling, HDFS xattr feature gates, and the shared xattr parameter encoder from the main server test.

Risks and test signals: good signal that optional xattr support does not accidentally appear enabled. It is sensitive to HDFS exception text and HTTP status mapping. The test does not explicitly shut down `miniDfs` at the end, so process/test extension cleanup is important if failures occur.
