<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/FailoverProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/FailoverProxyProvider.java

## Purpose
`FailoverProxyProvider` defines how retry proxies obtain the current backend proxy and switch to another backend when retry policy chooses failover.

## Important APIs and Types
`ProxyInfo<T>` carries the proxy and a debug string, with `getString(methodName)` and `toString` helpers. Interface methods are `getProxy`, `performFailover`, and `getInterface`; the provider is also `Closeable`.

## Control Flow
`RetryInvocationHandler.ProxyDescriptor` calls `getProxy` during construction and after failover, calls `performFailover(currentProxy)` under synchronization, and uses `getInterface` to reflect `Idempotent`/`AtMostOnce` annotations on declared methods.

## State and Persistence
The interface does not define state, but implementations normally hold one or more backend proxies and current selection. No persistence is required by the contract.

## Dependencies and Integration Points
It integrates with `RetryPolicy`, `RetryInvocationHandler`, annotations, and Hadoop RPC client lifecycle management.

## Risks and Edge Cases
Implementations must be thread-safe enough for concurrent retry calls. `ProxyInfo.proxyInfo` may be null, so logging should tolerate it. `getInterface` must return the actual annotated interface, not only a generated proxy class, or retry safety checks will be wrong.

## Test Signals
Tests should cover provider failover sequencing, annotation lookup through `getInterface`, concurrent failover suppression, close propagation, and logging/debug strings for null and non-null proxy info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/FailoverProxyProvider.java -->
