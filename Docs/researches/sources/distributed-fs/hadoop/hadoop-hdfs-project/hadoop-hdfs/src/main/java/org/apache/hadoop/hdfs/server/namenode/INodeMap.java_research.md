<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeMap.java

## Purpose

`INodeMap` stores the global mapping from inode id to in-memory inode object. It is a lightweight id index used by the NameNode for fast lookups independent of path traversal.

## Important APIs and Types

`newInstance` creates a `LightWeightGSet` sized from one percent of memory and inserts the root directory. `put` indexes only `INodeWithAdditionalFields`, `remove` deletes by inode, `get` resolves an id, `getMapIterator` exposes iteration, `size` returns count, and `clear` empties the map.

## Control Flow, State, and Persistence

The map is explicitly synchronized by an external lock; methods themselves are not synchronized. Lookup constructs a temporary anonymous `INodeWithAdditionalFields` with the target id and stub behavior so `GSet` equality/hash semantics can locate the real entry. The map is memory-resident and rebuilt from namespace/image state.

## Dependencies and Integration Points

It depends on `LightWeightGSet`, `GSet`, inode equality, root `INodeDirectory`, permissions for the temporary lookup key, and `BlockStoragePolicySuite` stubs. It is used by `FSDirectory` and systems that resolve inode ids, including leases and block ownership checks.

## Risks and Test Signals

Risks include external-lock misuse, id equality regressions, and stale map entries during deletion or snapshot cleanup. Tests should cover insert/replace/remove/get behavior, root insertion, iteration during namespace scans, and lookup of missing ids without side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeMap.java -->
