# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/RunnableRaisingIOE.java

`RunnableRaisingIOE` is a Java `Runnable` variant whose primary operation can throw `IOException`. It is useful when code should be passable to executor APIs while still being implemented in checked-IO form.

The abstract method is `apply()`. The inherited `run()` method is implemented as a default method: it invokes `apply()` and wraps any `IOException` in `UncheckedIOException`. Runtime exceptions from `apply()` pass through unchanged. There is no object state or persistence.

Dependencies are Java `IOException`, `UncheckedIOException`, and `Runnable`. It integrates with the package's broader checked-IO lambda strategy and is an executor-friendly counterpart to `InvocationRaisingIOE`. Risks are straightforward: executor/future callers see unchecked IO wrappers and must unwrap them if the original IO type matters; because it implements `Runnable`, lambdas may be target-typed differently than `InvocationRaisingIOE` in overloaded APIs. Test signals are indirect through the package's wrapping tests and any executor callers that observe `UncheckedIOException` behavior.
