<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/DefaultFailoverProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/DefaultFailoverProxyProvider.java

## Purpose
`DefaultFailoverProxyProvider` adapts a single implementation object to the `FailoverProxyProvider` interface for retry proxies that do not actually fail over to alternate backends.

## Important APIs and Types
The constructor stores the interface class and proxy object. `getInterface` returns the interface, `getProxy` returns a new `ProxyInfo` around the same proxy, `performFailover` is a no-op, and `close` stops the proxy through `RPC.stopProxy`.

## Control Flow
Retry proxies use this provider when callers pass a concrete implementation rather than a custom failover provider. Any policy action requesting failover will call `performFailover`, but the active proxy remains unchanged.

## State and Persistence
The provider stores only the proxy and interface references. No persistent state is written.

## Dependencies and Integration Points
It integrates with `RetryProxy`, `RetryInvocationHandler`, `FailoverProxyProvider`, and Hadoop IPC `RPC.stopProxy`.

## Risks and Edge Cases
Policies that return failover actions with this provider will retry the same backend, which may be intended for local retry but not high availability. `close` assumes `RPC.stopProxy` is appropriate for the wrapped object.

## Test Signals
Tests should verify stable proxy return, no-op failover, interface propagation for annotations, and close behavior for RPC and non-RPC proxy objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/DefaultFailoverProxyProvider.java -->
