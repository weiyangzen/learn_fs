<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ExecutingStoreOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ExecutingStoreOperation.java

## Purpose

`ExecutingStoreOperation` is a base class for S3A operations that can be submitted as `CallableRaisingIOE` and must execute at most once.

## Important APIs, Types, and Functions

It extends `AbstractStoreOperation`, implements `CallableRaisingIOE<T>`, provides final `apply()`, abstract `execute()`, and protected `executeOnlyOnce()`.

## Control Flow

`apply()` delegates to `execute()`. Subclasses are required to call `executeOnlyOnce()` at the start of `execute()`. That method atomically flips an `AtomicBoolean`, rejects re-entry, and activates the captured audit span.

## State and Persistence Behavior

State is the inherited context/span and one atomic executed flag. There is no persistence.

## Dependencies and Integration Points

It integrates with Hadoop functional utilities, audit spans, and operations such as delete, mkdir, content summary, and copy-from-local.

## Risks and Edge Cases

The single-execution contract is cooperative: subclasses must call `executeOnlyOnce()`. If they omit it, re-entry is not prevented and audit span activation is not guaranteed.

## Test Signals

Test `apply()` delegation, second-execution rejection in subclasses that call `executeOnlyOnce()`, audit activation, and concurrent double invocation against a test subclass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ExecutingStoreOperation.java -->
