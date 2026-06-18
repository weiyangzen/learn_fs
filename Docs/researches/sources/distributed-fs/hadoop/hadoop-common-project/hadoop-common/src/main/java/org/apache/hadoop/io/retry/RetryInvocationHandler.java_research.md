<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryInvocationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryInvocationHandler.java

## Purpose
`RetryInvocationHandler` is the dynamic-proxy invocation handler that applies Hadoop retry and failover policies around method calls, including RPC call-id propagation and asynchronous RPC integration.

## Important APIs and Types
The main public contract is `InvocationHandler.invoke`, `close`, `getConnectionId`, and `getProxyProvider`. Internal `Call` tracks one logical invocation, retry/failover counters, policy, call ID, and pending `RetryInfo`. `ProxyDescriptor` owns the active `FailoverProxyProvider.ProxyInfo` and failover count. `RetryInfo` captures selected retry action, delay, expected failover count, and failure exception.

## Control Flow
`invoke` determines whether the current proxy is an RPC proxy, allocates a call ID for RPC, creates either a synchronous `Call` or async `AsyncCall`, then loops until the call returns, throws, or async mode reports submitted. `Call.invokeOnce` invokes the method, catches exceptions, refuses retry if the thread is interrupted, asks `handleException` for retry info, sleeps or returns wait state, applies retry counters, and performs failover when needed. Failover is synchronized and only occurs if the provider failover count still equals the count observed before the attempt, preventing multiple concurrent failed calls from each causing separate failovers.

## State and Persistence
Instance state includes proxy descriptor, default and method-specific policies, successful-call flag, a set of proxy strings that have failed at least once for logging suppression, and an `AsyncCallHandler`. Per-call state includes counters and retry info. No persistent state exists, but RPC call ID and retry count are pushed to `Client` for server-side retry semantics.

## Dependencies and Integration Points
It integrates with `RetryProxy`, `FailoverProxyProvider`, `RetryPolicy`, `Idempotent`, `AtMostOnce`, Hadoop IPC `Client`, `RPC`, `RpcInvocationHandler`, `ProtocolTranslator`, and `AsyncCallHandler`.

## Risks and Edge Cases
Method policy mapping is by method name only, not signature. `method.setAccessible(true)` may be restricted on newer runtimes. `failedAtLeastOnce` is a plain `HashSet` accessed without synchronization, so concurrent invocations may race in logging state. Annotation lookup requires the provider interface to expose the exact method. MultiException aggregation depends on non-empty exception collections. Interrupted threads stop retry by rethrowing. Async mode changes control flow by returning null for submitted calls and storing the real result in a thread-local async handle.

## Test Signals
Tests should cover retry budgets, delay handling, interruption, failover count suppression under concurrency, method-specific policies, idempotent/at-most-once annotation effects, RPC call-id retry counts, async submission/completion, logging suppression after successful calls, and closing provider resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/RetryInvocationHandler.java -->
