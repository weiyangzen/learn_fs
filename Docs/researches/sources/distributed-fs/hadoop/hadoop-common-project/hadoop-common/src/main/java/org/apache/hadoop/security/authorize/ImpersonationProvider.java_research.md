# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/ImpersonationProvider.java

## Purpose

`ImpersonationProvider` is the extension point for Hadoop proxy-user authorization policy. Implementations load proxy-user configuration and authorize doAs requests.

## Important APIs, Types, and Functions

It extends `Configurable`, defines `init(String configurationPrefix)`, `authorize(UserGroupInformation, InetAddress)`, and a default `authorize(UserGroupInformation, String)` that resolves the string to an `InetAddress`.

## Control Flow

The default string-address method performs DNS/address resolution and wraps `UnknownHostException` in `AuthorizationException`. Implementations own the policy-specific flow after initialization.

## State and Persistence Behavior

The interface owns no state. Implementations typically keep loaded configuration in memory and refresh by replacement.

## Dependencies and Integration Points

It depends on `UserGroupInformation`, `InetAddress`, Hadoop `Configurable`, and `AuthorizationException`. `ProxyUsers` instantiates implementations from `hadoop.security.impersonation.provider.class`.

## Risks and Edge Cases

The string overload can introduce DNS lookup cost or resolution failure; callers with an existing `InetAddress` should prefer the address overload. Custom providers must define refresh-safe state behavior.

## Test Signals

Tests should verify provider selection, init prefix handling, the string overload's unknown-host conversion, and parity between string and `InetAddress` authorization paths.
