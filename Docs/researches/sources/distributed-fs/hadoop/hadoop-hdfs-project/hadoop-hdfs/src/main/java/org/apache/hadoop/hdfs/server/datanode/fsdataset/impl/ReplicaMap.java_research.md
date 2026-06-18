# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ReplicaMap.java

## Purpose

`ReplicaMap` is the DataNode's block-pool-partitioned in-memory index from block id to `ReplicaInfo`. It is the primary fast lookup structure for finalized, in-progress, provided, and other replica records managed by `FsDatasetImpl`.

## Important APIs, Control Flow, and State

The map is `ConcurrentHashMap<String, LightWeightResizableGSet<Block, ReplicaInfo>>`, with operations protected by a `DataNodeLockManager` or a `NoLockManager` for tests and temporary maps. Public package APIs include `get` by `Block` or block id, `add`, `addAndGet`, `addAll`, `mergeAll`, `remove`, `size`, `replicas`, `initBlockPool`, and `cleanUpBlockPool`. Generation-stamp-sensitive `get/remove` variants verify the stored replica's generation stamp before returning or deleting it.

State is entirely in memory and keyed by block pool. `mergeAll` carefully copies another GSet into a temporary `HashSet` before inserting to avoid iterator corruption or endless loops. `replicas(String)` returns an unsynchronized collection, while `replicas(String, Consumer<Iterator<ReplicaInfo>>)` runs under the lock manager and uses the GSet iterator callback.

## Dependencies, Integration, Risks, and Tests

Dependencies include `Block`, `ReplicaInfo`, `LightWeightResizableGSet`, and the DataNode dataset lock abstractions. It integrates with volume scanning, block reports, replica recovery, provided volume population, and cache/space accounting.

Risks include using read locks around mutating operations in several methods, unsynchronized collection exposure, null block-pool errors, and `addAll` replacing entire block-pool maps without per-pool merging. Tests should cover generation-stamp checks, add-and-get semantics, merge behavior, block-pool init/cleanup, concurrent access under lock manager, and iterator callback safety.
