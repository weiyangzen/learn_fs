# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/CachedBlock.java

## Purpose
`CachedBlock` is the compact in-memory identity and linkage object for a block known to NameNode cache tracking. It serves both as a `LightWeightGSet.LinkedElement` keyed by block ID and as an `IntrusiveCollection.Element` that can belong to multiple DataNode cached-block lists.

## Important APIs and Types
The main fields are immutable `blockId`, GSet `nextElement`, packed `replicationAndMark`, and `triplets`, an array of repeated `(CachedBlocksList, prev, next)` references. Public APIs expose identity, replication/mark bits, presence checks, DataNode listing by `CachedBlocksList.Type`, intrusive list operations, and GSet next-link operations.

## Control Flow
Insertion rejects duplicate membership in the same list, appends a triplet, and later `setPrev`/`setNext` mutate that triplet. Removal copies the array minus the removed triplet. `equals` and `hashCode` intentionally use only `blockId`, allowing lookup by temporary `CachedBlock` instances.

## State and Persistence
This object is non-persistent. It is reconstructed from cache reports and cache directive scans, and its membership is in-memory only. The replication and mark bits guide cache replication monitor scan decisions rather than fsimage content.

## Dependencies and Integration
It is consumed by `CacheManager`, `CacheReplicationMonitor`, `DatanodeDescriptor.CachedBlocksList`, `LightWeightGSet`, and `IntrusiveCollection`.

## Risks and Test Signals
The packed bit layout assumes non-negative replication within 15 bits; assertions do not run in production. The triplet array favors low allocation overhead but relies on exact list object identity and throws runtime exceptions on misuse. Tests should stress adding/removing one block across cached, pending-cached, and pending-uncached lists, GSet lookup equality, and DataNode filtering by list type.
