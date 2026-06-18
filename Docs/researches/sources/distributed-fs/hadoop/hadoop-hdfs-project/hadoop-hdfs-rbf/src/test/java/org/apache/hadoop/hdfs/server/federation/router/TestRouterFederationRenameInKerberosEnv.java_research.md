# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRenameInKerberosEnv.java

## Purpose

`TestRouterFederationRenameInKerberosEnv.java` verifies router federation rename in a Kerberos-secured mini-cluster. It starts a `MiniKdc`, configures secure namenode/datanode/router principals and keytabs, enables block tokens and delegation-token ZooKeeper settings, and tests a client keytab user renaming a directory across namespaces. The source was read as a complete 298-line JUnit 5 test.

## Important APIs, Types, and Functions

Important types include `MiniKdc`, `ClientBaseWithFixes`, `MiniRouterDFSCluster`, `RouterContext`, `SecurityUtil`, `UserGroupInformation`, `ImpersonationProvider`, `DFSClient`, and `ClientProtocol`. The nested `AllowUserImpersonationProvider` authorizes proxying only when the real user matches the current MiniCluster user. Key methods are `globalSetUp`, `setUp`, `tearDown`, `prepareEnv`, `testRenameDir`, `setRouter`, and `testClientRename`.

## Control Flow

Global setup starts MiniKdc, creates client and server principals in a generated keytab, sets Kerberos authentication and service principals in `baseConf`, configures data-transfer protection and secure-port test overrides, and enables `DistCpProcedure` test mode. Per-test setup creates a secure MiniRouterDFSCluster, starts namenodes and routers, configures router rename and ZK delegation token settings, registers namespaces, lowers datanode heartbeat expiry, installs mock locations, creates test directories, and picks a random router. The actual test prepares permissive parents, creates a source directory/file, logs in as the client principal from keytab, performs `ClientProtocol.rename` through the router, and checks the source disappears and destination file exists.

## State and Persistence Behavior

Static state includes `baseConf`, generated keytab path, MiniKdc, and principal names. Per-test state is the secure mini-cluster and selected router context. Temporary filesystem state is deleted in `testRenameDir`; cluster state is shut down after each test; KDC and DistCp test mode are stopped globally.

## Dependencies and Integration Points

This test integrates Hadoop security, router and namenode Kerberos principals, data-transfer protection, block access tokens, ZK delegation token secret-manager configuration, proxy-user authorization, router federation rename, DistCp scheduling, and MiniRouterDFSCluster.

## Risks and Edge Cases

The server principal uses the `USERNAME` environment variable and `localhost`, making the test sensitive to local environment assumptions. The generated keytab path lives under `test.dir` or `target`. Because it starts KDC, ZooKeeper-backed token configuration, and full mini-clusters, it is heavier and more timing-sensitive than unsecured rename tests. It only covers the successful client rename path, not secure failure cases.

## Test Signals

Signals are successful KDC principal creation, secure cluster startup, router/namenode registration, successful keytab login, no exception during cross-namespace rename, and post-rename source/destination existence checks.
