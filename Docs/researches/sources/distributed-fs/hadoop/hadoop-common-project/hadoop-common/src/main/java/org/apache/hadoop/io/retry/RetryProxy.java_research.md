<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryProxy.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryProxy.java

## Purpose
`RetryProxy` is a factory for dynamic proxies that apply `RetryInvocationHandler` to an interface implementation or failover proxy provider.

## Important APIs and Types
It has four `create` overloads: implementation plus single policy, provider plus single policy, implementation plus method-policy map with default fail, and provider plus method-policy map plus explicit default policy.

## Control Flow
Overloads that receive a concrete implementation wrap it in `DefaultFailoverProxyProvider`. All paths create a JDK dynamic proxy with the provider interface class loader, the requested interface, and a new `RetryInvocationHandler`.

## State and Persistence
`RetryProxy` is stateless. Generated proxy instances hold their invocation handler state.

## Dependencies and Integration Points
It depends on Java `Proxy`, `RetryInvocationHandler`, `DefaultFailoverProxyProvider`, `FailoverProxyProvider`, and `RetryPolicy`. It is the usual entry point shown in retry package docs.

## Risks and Edge Cases
The class loader comes from `proxyProvider.getInterface()`, not necessarily the `iface` argument. Method-policy maps key by method name and cannot distinguish overloads. Returned type is `Object`, so callers must cast correctly.

## Test Signals
Tests should create proxies with all overloads, verify interface/classloader behavior, method-policy routing, default policy fallback, provider close propagation, and overloaded method handling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryProxy.java -->
