# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LambdaUtils.java

## Purpose

`LambdaUtils` contains a small helper for evaluating a `Callable` and completing a `CompletableFuture` with either its result or the thrown failure.

## Important APIs, Types, And Functions

The public helper is `eval(CompletableFuture<T> result, Callable<T> call)`. It invokes `call.call()`, completes the supplied future normally on success, or completes it exceptionally with any caught `Throwable`.

## Control Flow, State, And Persistence

The utility is stateless. `eval()` always returns the same future instance it was passed after attempting completion.

## Dependencies And Integration Points

It depends on Java `Callable` and `CompletableFuture`. It integrates with async Hadoop code that wants a concise bridge from synchronous callable execution into future completion.

## Risks And Test Signals

The helper catches `Throwable`, so serious errors are captured into the future rather than escaping the evaluating thread. Tests should verify successful completion, checked/runtime/error exceptional completion, returned future identity, callable invocation exactly once, and behavior when the future is already completed.
