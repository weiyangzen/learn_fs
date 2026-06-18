# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ProxyUsers.java

## Purpose

`ProxyUsers` is the static facade for Hadoop proxy-user authorization. It selects an `ImpersonationProvider`, refreshes proxy-user rules, and delegates doAs authorization checks.

## Important APIs, Types, and Functions

It defines `CONF_HADOOP_PROXYUSER`, refresh overloads, `authorize` overloads for string and `InetAddress`, deprecated `authorize(..., Configuration)`, and `getDefaultImpersonationProvider` for tests. It uses `hadoop.security.impersonation.provider.class` to select custom implementations.

## Control Flow

Refresh validates the prefix, creates a provider with `ReflectionUtils`, initializes it with the prefix, stores it in volatile `sip`, and refreshes `ProxyServers`. Authorization lazily refreshes if `sip` is null, then delegates to the current provider.

## State and Persistence Behavior

The current provider is a process-wide volatile singleton. Reconfiguration is atomic at the reference level; old provider instances may still be used by in-flight calls.

## Dependencies and Integration Points

It depends on `DefaultImpersonationProvider`, `ImpersonationProvider`, `Configuration`, `UserGroupInformation`, `ProxyServers`, and common security configuration keys. It is called by RPC, HTTP, and service components that support doAs.

## Risks and Edge Cases

Lazy default refresh can load default configuration unexpectedly. The test accessor assumes the active provider is `DefaultImpersonationProvider` and will fail for custom providers. Deprecated overload ignores the passed configuration except through already refreshed state.

## Test Signals

Tests should verify provider replacement, custom provider configuration, prefix validation, lazy refresh, string/address authorization parity, and proxy server refresh coupling.
