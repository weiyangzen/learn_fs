# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestProxyServers.java

Purpose: validates the `ProxyServers` allow-list loaded by `ProxyUsers.refreshSuperUserGroupsConfiguration`.

Important APIs and types: `ProxyServers.isProxyServer`, `ProxyServers.CONF_HADOOP_PROXYSERVERS`, `ProxyUsers.refreshSuperUserGroupsConfiguration`, and `Configuration`.

Control flow: the test first asserts an arbitrary IP is not a proxy server with default state. It then configures `2.2.2.2, 3.3.3.3`, refreshes proxy-user configuration, and asserts the original IP is still false while both configured IPs are true.

State and persistence: mutates static proxy server configuration maintained by `ProxyServers`/`ProxyUsers`. No files are written.

Dependencies and integration points: integrates proxy server list parsing with the global proxy-user refresh path used by Hadoop HTTP and RPC impersonation features.

Risks: static allow-list can leak to other tests if not refreshed. Only exact IP strings are tested; no hostname or whitespace-edge coverage appears here.

Test signals: concise regression signal that configured proxy server IPs are recognized after refresh and unrelated IPs remain denied.
