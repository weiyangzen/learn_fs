# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/AsyncCallLimitExceededException.java

## Purpose

`AsyncCallLimitExceededException` signals that the client-side asynchronous RPC call limit has been exceeded.

## Important APIs, control flow, and state

It is a simple `IOException` subclass with a message constructor and `serialVersionUID`. `Client.checkAsyncCall()` throws it when asynchronous mode is enabled and `asyncCallCounter.incrementAndGet()` exceeds `ipc.client.async.calls.max`.

## Dependencies and integration points

It integrates directly with `Client` asynchronous RPC mode. Application code can catch it as an `IOException` and drain or wait for outstanding async responses before issuing more calls.

## Risks and test signals

`Client.checkAsyncCall()` increments before throwing, and the caller's catch path releases the async call only when async call checking is enabled. Tests should verify counter accounting at limit boundaries, exception type propagation through async callers, and recovery after completing outstanding futures.
