# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ThreadLocalContext.java

## Purpose
`ThreadLocalContext` captures thread-local RPC and metrics context so asynchronous Router work can restore the original caller context on worker threads.

## Important APIs and Types
The constructor captures `Server.getCurCall().get()`, `CallerContext.getCurrent()`, `FederationRPCPerformanceMonitor.getStartOpTime()`, and `getProxyOpTime()`. `transfer()` installs those values into the current thread. `toString()` reports captured fields.

## Control Flow
Async code creates an instance on the caller thread before scheduling work. Worker code calls `transfer()`, which clears the current `Server.Call` and `CallerContext`, restores captured values when non-null, and restores metrics timestamps when they are not `-1L`.

## State and Persistence
The object is immutable after construction and persists only in memory long enough to cross async execution boundaries. It does not clear metrics values when captured timestamps are `-1L`.

## Dependencies and Integration Points
It depends on Hadoop IPC `Server.Call`, `CallerContext`, and `FederationRPCPerformanceMonitor`. It supports async router RPC implementations and performance metrics attribution.

## Risks
Restoring stale context on reused worker threads can corrupt attribution if `transfer()` is called at the wrong time or without later cleanup. The method clears call/context before restoration but only conditionally sets metric timestamps, so existing worker-thread metric values can remain when captured values are absent.

## Test Signals
Tests should cover transfer of non-null and null call/context, metric timestamp propagation, worker-thread reuse, and async RPC metrics attribution.
