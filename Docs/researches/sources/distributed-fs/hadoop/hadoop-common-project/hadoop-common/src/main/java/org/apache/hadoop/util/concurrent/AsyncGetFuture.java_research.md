# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/AsyncGetFuture.java

Purpose: `AsyncGetFuture<T,E>` adapts an `AsyncGet` into Guava's `AbstractFuture`, performing lazy polling when `get`, timed `get`, or `isDone` is invoked.

Important APIs/types/functions: constructor stores the `AsyncGet`. `callAsyncGet(long, TimeUnit)` is the core polling method. Overrides `get()`, `get(timeout, unit)`, and `isDone()` trigger polling before delegating to `AbstractFuture`.

Control flow: `called` is an `AtomicBoolean` that allows only one in-flight call to `asyncGet.get`. If polling times out, the flag resets so later calls can retry. If polling returns a value, `set` completes the future. Any non-timeout throwable completes the future exceptionally. Timed `get` polls with the supplied timeout and then calls `super.get(0, MILLISECONDS)`.

State and persistence behavior: in-memory future state comes from `AbstractFuture`, plus `called` and the underlying async object. No persistence.

Dependencies and integration points: depends on shaded Guava `AbstractFuture`, Java `Future` semantics, and SLF4J trace logging.

Risks: `isDone()` can perform a nonblocking poll and has side effects. Timed `get` may spend the entire timeout in `asyncGet.get`, then immediately time out on the future if no result was set. Catching `Throwable` means severe errors are captured as future failures. Concurrent callers that lose the `called` CAS delegate immediately to `AbstractFuture`, which may block or time out independently.

Test signals: tests should cover retry after timeout, exception propagation, cancellation behavior, concurrent callers, null successful results, and side effects from `isDone`.
