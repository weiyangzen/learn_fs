<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/AutoCloseDataSetLock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/AutoCloseDataSetLock.java

## Purpose

`AutoCloseDataSetLock` adapts a `Lock` to Hadoop's `AutoCloseableLock` pattern so DataNode dataset locks can be acquired and released with try-with-resources.

## Important APIs and types

The class stores a `Lock`, optional parent `AutoCloseDataSetLock`, and optional `DataNodeLockManager`. `lock` acquires the wrapped lock, `close` releases it, invokes manager `hook`, and closes the parent lock. `setParentLock` assigns a parent only once, and `setDataNodeLockManager` registers the callback manager.

## Control flow

Clients typically receive an already-created lock wrapper from a `DataNodeLockManager`, call `lock`, run protected code, and rely on `close` for release. Parent lock chaining lets lower-level locks release higher-level locks in reverse chain order from a single close call.

## State and persistence behavior

State is in-memory synchronization state only. There is no persistence. The wrapper does not null out the lock after close, so double-close would attempt a second unlock.

## Dependencies and integration points

It integrates with DataNode dataset locking, `DataNodeLockManager`, `DataSetLockManager.LOG`, and Hadoop `StringUtils` stack traces for null-lock misuse diagnostics.

## Risks and edge cases

Null locks are logged rather than throwing, except subclass no-op behavior. Double close and lock/close imbalance depend on underlying `Lock` behavior. Parent chains must be acyclic; no protection exists against cycles.

## Test signals

Tests should cover lock/unlock calls, manager hook invocation, parent close ordering, null-lock logging, no-op subclass behavior, and double-close failure expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/AutoCloseDataSetLock.java -->
