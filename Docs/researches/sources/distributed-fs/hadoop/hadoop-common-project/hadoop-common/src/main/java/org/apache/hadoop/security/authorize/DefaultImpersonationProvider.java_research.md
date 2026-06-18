# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/DefaultImpersonationProvider.java

## Purpose

`DefaultImpersonationProvider` implements Hadoop's standard proxy-user authorization. It reads `hadoop.proxyuser.<superuser>.users`, `.groups`, and `.hosts` style settings, then validates whether a real user may impersonate an effective user from a remote address.

## Important APIs, Types, and Functions

The class implements `ImpersonationProvider` with `setConf`, `getConf`, `init`, and `authorize`. It exposes key builders `getProxySuperuserUserConfKey`, `getProxySuperuserGroupConfKey`, and `getProxySuperuserIpConfKey`, plus testing accessors for loaded groups/hosts and a singleton `getTestProvider`.

## Control Flow

`init` normalizes the prefix, uses regex-based configuration scans to collect user/group ACLs and host lists, builds one `AccessControlList` per proxy superuser, and one `MachineList` per hosts key. `authorize` returns immediately for non-proxy UGI, otherwise loads the real user, checks the effective user against the real user's ACL, then checks the remote `InetAddress` against the configured host `MachineList`.

## State and Persistence Behavior

Loaded ACLs and host lists are in mutable maps on the provider instance. There is no file persistence; refresh is achieved by constructing/reinitializing provider instances through `ProxyUsers`.

## Dependencies and Integration Points

It depends on `Configuration.getValByRegex`, `AccessControlList`, `MachineList`, `UserGroupInformation`, and `ProxyUsers.CONF_HADOOP_PROXYUSER`. It is the default implementation selected by `ProxyUsers` unless configuration names another `ImpersonationProvider`.

## Risks and Edge Cases

Missing ACLs or missing hosts deny proxy authorization. The prefix regex uses non-whitespace superuser key matching, so malformed keys may be skipped. Host checks use resolved `InetAddress`, so DNS/address normalization matters. `getTestProvider` is shared mutable global test state.

## Test Signals

Tests should cover wildcard users/groups/hosts, user-only and group-only proxy permissions, denied host, denied effective user, non-proxy UGI bypass, custom prefixes, refresh replacement via `ProxyUsers`, and unresolved/malformed host settings.
