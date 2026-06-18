<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AbstractStoreOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AbstractStoreOperation.java

## Purpose

`AbstractStoreOperation` is the small base class for S3A store-side operation objects. It gives operations a common `StoreContext` reference and captures the active `AuditSpan` at construction time so later worker-thread execution can reactivate the same audit context.

## Important APIs, Types, and Functions

The class exposes protected constructors accepting a nullable `StoreContext`, optionally with an explicit `AuditSpan`. Public accessors are `getStoreContext()`, `getAuditSpan()`, and `activateAuditSpan()`.

## Control Flow

Construction pulls `storeContext.getActiveAuditSpan()` when a context is supplied. `activateAuditSpan()` is a null-tolerant guard that calls `AuditSpan.activate()` only when an audit span was captured.

## State and Persistence Behavior

State is immutable after construction: one context reference and one audit-span reference. There is no persistence, synchronization, or close behavior.

## Dependencies and Integration Points

It depends on `StoreContext` and Hadoop audit spans. It is extended by higher-level operation classes such as delete, mkdir, bulk delete, header processing, and executing operations.

## Risks and Edge Cases

The context may be null, so subclasses that assume a non-null store context must enforce that themselves. Capturing the span early is deliberate; failing to use this base in asynchronous operations can lose audit attribution.

## Test Signals

Tests should verify null-context construction, audit-span capture from a mock context, explicit-span construction, and that `activateAuditSpan()` is no-op when the span is null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AbstractStoreOperation.java -->
