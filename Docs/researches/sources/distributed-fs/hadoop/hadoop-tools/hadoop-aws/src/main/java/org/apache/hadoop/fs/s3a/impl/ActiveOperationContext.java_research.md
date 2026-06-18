<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ActiveOperationContext.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ActiveOperationContext.java

## Purpose

`ActiveOperationContext` carries per-operation metadata: an opaque operation id and the `S3AStatisticsContext` used to publish metrics for the active S3A operation.

## Important APIs, Types, and Functions

The constructor requires an operation id and non-null statistics context. `getOperationId()`, `getS3AStatisticsContext()`, and `toString()` expose the fields. `newOperationId()` increments a static `AtomicLong`.

## Control Flow

Callers allocate operation ids through the static counter, then construct an instance with instrumentation. There is no lifecycle beyond object creation and read access.

## State and Persistence Behavior

The operation id and statistics context are final. The only mutable state is the process-local static counter; ids are unique within a JVM but are not persisted or globally unique.

## Dependencies and Integration Points

It depends on `S3AStatisticsContext` and is intended for S3A operation tracing/logging and metric routing.

## Risks and Edge Cases

`newOperationId()` is protected, so only package/subclass code can generate ids. Counter overflow is theoretically possible in very long-lived processes, though unlikely. The `toString()` omits statistics context intentionally.

## Test Signals

Unit tests can assert null statistics rejection, monotonically increasing ids, getter behavior, and stable `toString()` formatting for logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ActiveOperationContext.java -->
