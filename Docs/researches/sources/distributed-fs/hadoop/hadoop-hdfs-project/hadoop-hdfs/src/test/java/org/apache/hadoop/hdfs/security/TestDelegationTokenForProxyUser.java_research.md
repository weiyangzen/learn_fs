# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/TestDelegationTokenForProxyUser.java

Purpose: Tests delegation token and WebHDFS behavior when a real user impersonates a proxy user.

Important APIs/types/functions: `UserGroupInformation.createProxyUserForTesting`, `ProxyUsers.refreshSuperUserGroupsConfiguration`, `DefaultImpersonationProvider`, `MiniDFSCluster`, `DelegationTokenIdentifier`, `WebHdfsTestUtil`, `Whitebox.setInternalState`, and WebHDFS create/append/status operations.

Control flow: `setUp()` configures token lifetimes, proxy superuser group and IP allowlists, starts MiniDFSCluster, refreshes proxy-user rules, and creates real/proxy UGIs. One test obtains delegation tokens in `proxyUgi.doAs`, decodes the identifier, and checks effective and real users. The WebHDFS test opens WebHDFS as the real user, swaps internal UGI to proxy UGI, and verifies home directory, create, append, and ownership.

State and persistence behavior: Filesystem state includes a test file owned by the proxy user. Token identifiers encode real/effective user identity.

Dependencies and integration points: Proxy authorization, local network address discovery, HDFS delegation tokens, WebHDFS doAs behavior, permissions, and UGI propagation.

Risks: Proxy regressions can issue tokens to the wrong identity or write WebHDFS files as the real user instead of the effective user.

Test signals: Passing confirms token identifiers preserve real/effective user relationship and WebHDFS operations use proxy ownership.
