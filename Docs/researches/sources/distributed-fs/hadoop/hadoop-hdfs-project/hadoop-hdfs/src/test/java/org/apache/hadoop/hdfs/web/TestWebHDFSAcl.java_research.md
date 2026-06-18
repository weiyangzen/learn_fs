# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSAcl.java

Purpose: runs the shared NameNode ACL base test suite through WebHDFS.

Important APIs/types/functions: `FSAclBaseTest`, `WebHdfsTestUtil.createConf`, `startCluster`, `createFileSystem`, `createFileSystem(UserGroupInformation)`, `WebHdfsConstants.WEBHDFS_SCHEME`.

Control flow: class initialization creates WebHDFS test configuration and starts the inherited ACL test cluster. It overrides filesystem factories so base ACL tests operate via `WebHdfsFileSystem` as superuser or a specified UGI. One inherited test, `testDefaultAclNewSymlinkIntermediate`, is disabled because WebHDFS cannot currently resolve symlinks for that scenario.

State and persistence behavior: cluster and filesystem state are managed by `FSAclBaseTest`. This subclass contributes WebHDFS client selection and class-level configuration.

Dependencies and integration points: integrates WebHDFS with the generic HDFS ACL conformance suite, including user-specific clients.

Risks: most behavior is inherited, so this file's direct content is small but its executed surface is broad. The disabled symlink ACL case documents a known WebHDFS limitation and prevents false failure.

Test signals: all enabled base ACL operations must pass over WebHDFS, confirming parity with direct HDFS ACL behavior except the explicitly skipped symlink intermediate case.
