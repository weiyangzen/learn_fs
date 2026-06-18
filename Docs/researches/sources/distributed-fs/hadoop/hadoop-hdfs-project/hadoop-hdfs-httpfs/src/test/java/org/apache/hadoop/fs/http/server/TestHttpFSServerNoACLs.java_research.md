# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSServerNoACLs.java

Purpose: Negative integration suite for HTTPFS when HDFS ACL support is disabled. It proves normal file status/listing operations still work while ACL-specific operations surface HDFS ACL-disabled failures.

Important APIs/types/functions: `startMiniDFS`, `createHttpFSServer`, `getStatus`, `putCmd`, `MiniDFSCluster`, `DFS_NAMENODE_ACLS_ENABLED_KEY`, Jetty `WebAppContext`, `HttpFSAuthenticationFilter`, and `HadoopUsersConfTestHelper`.

Control flow: it builds its own MiniDFS cluster instead of using `TestHdfsHelper` so ACLs remain explicitly disabled. It writes HDFS and HTTPFS configuration files pointing HTTPFS at that cluster, starts Jetty, creates a directory/file directly through `FileSystem`, then calls REST status and ACL operations. `GETFILESTATUS` and `LISTSTATUS` must return OK without `aclBit`; `GETACLSTATUS` and all ACL mutation operations must return HTTP 500 containing `AclException` and the disabled-support message.

State and persistence: state is a per-test MiniDFS cluster plus generated local config/secret files. `miniDfs` and `nnConf` are instance fields; shutdown occurs at the end of the test, so assertion failures before shutdown can leave cleanup to the test framework/process teardown.

Dependencies/integration: exercises HTTPFS with HDFS defaults where ACLs are off and validates error propagation from HDFS through HTTPFS JSON/error streams.

Risks and test signals: strong guard for optional ACL support. Risks are brittle exact error text/status expectations and hand-rolled cluster lifecycle. A regression would show as ACL operations succeeding unexpectedly, status responses leaking `aclBit`, or errors not preserving useful ACL-disabled diagnostics.
