<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/NoLockManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/NoLockManager.java

## Purpose

`NoLockManager` is a no-op `DataNodeLockManager` for tests or temporary DataNode data structures that do not require real dataset locking.

## Important APIs and types

It returns a singleton `NoDataSetLock`, a private subclass of `AutoCloseDataSetLock` with no-op `lock` and `close`. All manager methods `readLock`, `writeLock`, `addLock`, `removeLock`, and `hook` are no-ops.

## Control flow

Callers can use it through the same try-with-resources lock API as a real manager, but no synchronization occurs.

## State and persistence behavior

The only state is a reusable no-op lock object. There is no persistence and no resource registry.

## Dependencies and integration points

It integrates with code paths parameterized by `DataNodeLockManager`, especially unit tests and temporary replica maps that want to avoid lock setup.

## Risks and edge cases

Using it in production shared mutable dataset paths would remove mutual exclusion. Because the same lock object is returned for all resources, tests that assert distinct lock identity should not use this manager.

## Test signals

Tests should verify API compatibility, no thrown exceptions under try-with-resources, no side effects from add/remove/hook, and clear separation from real lock-manager tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/NoLockManager.java -->
