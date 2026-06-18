# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProxyCombiner.java

## Purpose
`ProxyCombiner` builds one dynamic proxy for an interface whose methods are implemented by multiple underlying protocol proxies.

## Important APIs, Types, and Functions
`combine(Class<T>, Object... proxies)` verifies method coverage, then returns a proxy backed by `CombinedProxyInvocationHandler`. The handler implements `RpcInvocationHandler`, delegates calls, returns the first proxy's connection id, formats `toString`, and closes all closeable delegates with `MultipleIOException`.

## Control Flow
Build-time coverage scans every method in the combined interface against delegate classes. Invocation loops through delegates and calls `Method.invoke`; target exceptions are unwrapped. Close loops through delegates and accumulates IO failures.

## State and Persistence Behavior
State is only the combined interface and delegate proxy array. No persistence is performed.

## Dependencies and Integration Points
It depends on Java dynamic proxies, `RpcInvocationHandler`, `RPC.getConnectionIdForProxy`, Guava `Joiner`, and `MultipleIOException`.

## Risks and Test Signals
Risks include invoking a method on a delegate that does not implement it after only partial reflective checking, ambiguous duplicate methods choosing the first proxy, and assuming all connection ids match. Tests should cover complete/incomplete method coverage, duplicate methods, exception propagation, and close aggregation.
