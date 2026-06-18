# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/AsyncGet.java

Purpose: `AsyncGet<R,E>` defines a pollable asynchronous result abstraction whose `get` can time out before the underlying computation is complete.

Important APIs/types/functions: `get(long, TimeUnit)` returns a possibly null result or throws implementation exception `E`, `TimeoutException`, or `InterruptedException`. `isDone()` reports completion. Nested `Util.wait(Object,long,TimeUnit)` maps timeout semantics to `Object.wait`.

Control flow: implementations provide actual completion logic. Utility wait blocks indefinitely for negative timeout, returns immediately for zero, and waits `unit.toMillis(timeout)` for positive values.

State and persistence behavior: interface only; no state.

Dependencies and integration points: used by `AsyncGetFuture` to adapt pollable operations to a `Future` API.

Risks: `Util.wait` requires the caller to hold the object's monitor and truncates sub-millisecond timeouts through `toMillis`. Zero timeout means no wait. Implementations must consistently throw `TimeoutException` rather than blocking beyond timeout.

Test signals: tests should verify timeout semantics, indefinite waits, interrupt propagation, and `isDone` consistency for implementations.
