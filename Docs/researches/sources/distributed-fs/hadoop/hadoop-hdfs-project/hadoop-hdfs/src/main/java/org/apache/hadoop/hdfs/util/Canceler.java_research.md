<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Canceler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Canceler.java

## Purpose
`Canceler` is a simple cross-thread cancellation flag with a human-readable reason.

## APIs and Types
It exposes `cancel(String reason)`, `isCancelled()`, and `getCancellationReason()`.

## Control Flow
Calling `cancel` stores the reason in a volatile field. Polling code checks non-null reason with `isCancelled` and may retrieve the reason.

## State and Persistence
State is a single volatile `String`. Cancellation is one-way unless callers pass `null`, which the method does not prevent but would effectively clear cancellation.

## Dependencies and Integration
It has no runtime dependencies beyond annotations. `DataTransferThrottler` accepts an optional `Canceler` to stop sleeping early.

## Risks
There is no synchronization beyond volatile visibility and no compare-and-set semantics for competing cancellation reasons. Passing null is not guarded. Consumers must poll; cancellation does not interrupt waiting threads by itself.

## Test Signals
Tests should cover initial state, cancellation visibility across threads, reason retrieval, and null reason behavior if supported or prohibited by future changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Canceler.java -->
