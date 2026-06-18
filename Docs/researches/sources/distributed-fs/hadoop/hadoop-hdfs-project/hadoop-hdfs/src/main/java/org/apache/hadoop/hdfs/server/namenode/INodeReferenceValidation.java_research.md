<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeReferenceValidation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeReferenceValidation.java

## Purpose

`INodeReferenceValidation` is an optional validation harness for checking `INodeReference` graph consistency, mainly during FSImage validation or diagnostic runs.

## Important APIs and Types

Static `start` installs a singleton collector, `add` and `remove` track reference objects by class, and `end` drains validation and reports added errors. `ReferenceSet` stores references of one subclass and submits batched `Task` instances. Each `Task` calls `ref.assertReferences()` for up to `100_000` references.

## Control Flow, State, and Persistence

When validation is enabled, constructors and removal paths in `INodeReference` subclasses register or unregister objects. At `end`, the validator creates a fixed thread pool sized to available processors, periodically logs progress with a `Timer`, submits tasks for `DstReference`, `WithCount`, and `WithName`, and increments the shared error count for assertion failures. It is transient only; no namespace state is persisted.

## Dependencies and Integration Points

It depends on `FsImageValidation.Cli` helpers for output and error formatting, `FsImageValidation.Util` for counts, Java executors/futures/timer, and the `assertReferences` methods implemented by each reference subclass.

## Risks and Test Signals

Risks include memory growth when validating very large images, task partitioning behavior caused by removing from iterators while batching, and validation only running when `start` is active. Tests should cover registration/removal identity semantics, task batching, progress completion, and injected malformed reference graphs that increment the error counter rather than aborting the whole validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeReferenceValidation.java -->
