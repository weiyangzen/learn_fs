<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/DataNodeLockManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/DataNodeLockManager.java

## Purpose

`DataNodeLockManager` defines the DataNode dataset lock hierarchy abstraction used to coordinate block-pool, volume, and directory level operations.

## Important APIs and types

The generic type parameter extends `AutoCloseDataSetLock`. `LockLevel` enumerates `BLOCK_POOl`, `VOLUME`, and `DIR`. Implementations provide `readLock`, `writeLock`, `addLock`, `removeLock`, and `hook`.

## Control flow

Callers request read or write locks for a lock level and resource path, use the returned auto-close wrapper, and release by closing. The documented order is block pool, then volume, then directory when acquiring nested locks.

## State and persistence behavior

The interface owns no state. Implementations maintain lock registries in memory; `addLock` and `removeLock` allow dynamic resource registration.

## Dependencies and integration points

It integrates with DataNode dataset/replica map locking, `AutoCloseDataSetLock`, concrete `DataSetLockManager`, and `NoLockManager` for tests or temporary maps.

## Risks and edge cases

The enum constant `BLOCK_POOl` uses a lowercase final `l`, so string-based references are fragile. Deadlock avoidance depends on implementations and callers honoring the documented order. The `hook` semantics are implementation-specific.

## Test signals

Tests should cover lock hierarchy ordering, dynamic add/remove, read/write mutual exclusion, hook callbacks, resource key construction, and no-op manager compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/DataNodeLockManager.java -->
