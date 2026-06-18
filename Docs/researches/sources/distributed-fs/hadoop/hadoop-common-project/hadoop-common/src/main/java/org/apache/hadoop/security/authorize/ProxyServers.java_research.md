# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ProxyServers.java

## Purpose

`ProxyServers` maintains the trusted HTTP proxy server allowlist used by Hadoop proxy-related security code.

## Important APIs, Types, and Functions

It defines `CONF_HADOOP_PROXYSERVERS`, `refresh()`, `refresh(Configuration)`, and `isProxyServer(String)`.

## Control Flow

`refresh` reads trimmed host strings from configuration, resolves each through `InetSocketAddress(host, 0)`, stores resolved IP addresses, and publishes the collection through a volatile static field. `isProxyServer` lazily refreshes with default configuration if needed and checks membership by remote address string.

## State and Persistence Behavior

State is a process-wide volatile collection of resolved IP address strings. There is no persistence beyond configuration reload.

## Dependencies and Integration Points

It depends on Hadoop `Configuration` and Java network address resolution. `ProxyUsers.refreshSuperUserGroupsConfiguration` refreshes proxy servers alongside proxy-user rules.

## Risks and Edge Cases

Unresolved hosts are ignored. Matching is by resolved IP string, so hostname aliases and DNS changes require refresh. The lazy default refresh can use an unexpected classpath configuration if callers did not explicitly refresh.

## Test Signals

Tests should cover resolved and unresolved hosts, explicit refresh replacement, lazy refresh behavior, and matching by IP address rather than hostname.
