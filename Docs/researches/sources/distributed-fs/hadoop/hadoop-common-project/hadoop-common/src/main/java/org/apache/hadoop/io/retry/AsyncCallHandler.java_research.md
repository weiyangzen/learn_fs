<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/AsyncCallHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/AsyncCallHandler.java

## Purpose
`AsyncCallHandler` adapts `RetryInvocationHandler` to Hadoop RPC asynchronous mode. It stores lower-layer async returns in thread-locals, tracks outstanding async retry calls, polls them on a daemon processor, and exposes an `AsyncGet` to the original caller.

## Important APIs and Types
Static APIs are `getAsyncReturn` and `setLowerLayerAsyncReturn`. Internal types include `ConcurrentQueue`, `AsyncCallQueue`, `AsyncCallQueue.Processor`, `AsyncValue`, and `AsyncCall`, which extends `RetryInvocationHandler.Call`.

## Control Flow
When a retry proxy is invoked in asynchronous mode, `RetryInvocationHandler` creates an `AsyncCall`. `AsyncCall.invoke` temporarily enables lower-level RPC async mode, calls the target method, expects a null direct result plus a lower-layer `AsyncGet`, and registers itself on first attempt. The processor daemon repeatedly calls `checkCalls`, removes completed calls, computes the next wait period, and sleeps on the handler monitor. `AsyncCall.isDone` advances the retry state machine: complete returns/exceptions set `AsyncValue`, retries are invoked again, and wait/in-progress states stay queued.

## State and Persistence
State is in thread-local async returns, a concurrent call queue, an atomic processor thread reference, per-call lower-layer async handle, `AsyncValue<CallReturn>`, and a `hasSuccessfulCall` flag used by logging. There is no persistent state.

## Dependencies and Integration Points
It integrates with Hadoop `Client` asynchronous mode and call-id propagation, `Daemon`, `Time`, `AsyncGet`, `Preconditions`, and `RetryInvocationHandler.Call`.

## Risks and Edge Cases
Thread-local returns must be consumed exactly once; missing lower-layer async values fail preconditions. `AsyncValue.set` forbids setting a completed call twice. The processor stop logic depends on queue-empty grace timing and monitor waits, so missed notifications could add up to the max wait period. The `RETRY` state in `isDone` invokes once immediately after processing retry info, which can make state transitions dense. `hasSuccessfulCall` is set when async `get` succeeds, not when lower-layer work finishes.

## Test Signals
Tests should cover successful async calls, delayed lower-layer completion, retry with wait, failover under async mode, exception propagation from `AsyncGet`, timeout behavior, daemon start/stop grace period, and thread-local cleanup after retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/retry/AsyncCallHandler.java -->
