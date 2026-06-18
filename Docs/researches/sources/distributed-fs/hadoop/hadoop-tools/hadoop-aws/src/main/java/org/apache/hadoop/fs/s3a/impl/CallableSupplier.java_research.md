<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CallableSupplier.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CallableSupplier.java

## Purpose

`CallableSupplier` bridges checked-exception `Callable` work into `CompletableFuture.supplyAsync()` while preserving S3A audit span activation and converting checked failures into future-compatible runtime wrappers.

## Important APIs, Types, and Functions

It implements `Supplier<T>`. Static helpers include `submit(Executor, Callable)`, `submit(Executor, AuditSpan, Callable)`, `waitForCompletion(List<CompletableFuture<T>>)`, `waitForCompletion(CompletableFuture<T>)`, `waitForCompletionIgnoringExceptions()`, and `maybeAwaitCompletion()`.

## Control Flow

`get()` activates the audit span, calls the callable, rethrows runtime exceptions, wraps IOExceptions in `UncheckedIOException`, and wraps other exceptions as IOExceptions inside `UncheckedIOException`. Waiting helpers join futures, unwrap completion failures through `FutureIO.raiseInnerCause()`, and optionally ignore exceptions.

## State and Persistence Behavior

Each instance stores one callable and optional audit span. There is no persistence. Futures represent asynchronous state owned by callers.

## Dependencies and Integration Points

It is used by copy, delete, and other operations that submit audit-aware async work. It depends on `DurationInfo`, `AuditSpan`, and Hadoop future utilities.

## Risks and Edge Cases

`waitForCompletion(CompletableFuture)` does not accept null, while `maybeAwaitCompletion()` does. Cancellation becomes an IOException. Non-IO checked exceptions lose their original checked type.

## Test Signals

Cover successful calls, span activation, runtime exception propagation, IOException unwrapping from futures, cancellation behavior, empty list waiting, ignored exception path, and null future handling in `maybeAwaitCompletion()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CallableSupplier.java -->
