# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AOpContext.java

## Purpose
`S3AOpContext` is a base operation context struct for S3A filesystem operations, carrying retry invocation, optional filesystem statistics, instrumentation context, and destination file status.

## Important APIs, Types, and Functions
The main API is the constructor plus `getInvoker()`, `getStats()`, and `getDstFileStatus()`. It extends `ActiveOperationContext`, which contributes an operation id and statistics context.

## Control Flow and State
Construction creates a new operation id, validates `Invoker`, `S3AStatisticsContext`, and destination status, then stores them for downstream operation code. There is no behavior beyond accessors; operation-specific context belongs in subclasses such as `S3AReadOpContext`.

## State and Persistence Behavior
State is per-operation and in-memory. It does not persist changes but carries references to shared retry/statistics infrastructure and the destination status captured during preflight checks.

## Dependencies and Integration Points
Dependencies include `Invoker`, `FileSystem.Statistics`, `FileStatus`, `S3AStatisticsContext`, and `ActiveOperationContext`. It integrates with filesystem operations that need a common bundle of retry, stats, and destination-state information.

## Risks and Test Signals
Risks are mostly null/incorrect context wiring and stale destination status if callers reuse a context across changing remote state. Tests should assert constructor validation, unique operation ids, correct stat/invoker propagation, and subclass behavior using `dstFileStatus`.
