# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/RamDiskReplicaLruTracker.java

## Purpose

`RamDiskReplicaLruTracker` is the default `RamDiskReplicaTracker` implementation. It tracks RAM_DISK replicas, queues them for lazy persistence, and chooses persisted replicas for eviction using least-recently-used ordering.

## Important APIs, Control Flow, and State

State is split across `replicaMaps` (`bpid -> blockId -> RamDiskReplicaLru`), `replicasNotPersisted` FIFO queue, and `replicasPersisted` `TreeMultimap` keyed by last-used time. `addReplica` inserts a new record and queues it for persistence. `touch` increments read count and, if the block has been persisted, updates its LRU timestamp. `recordStartLazyPersist` records the target persistent volume; `recordEndLazyPersist` records saved files, removes the replica from the not-persisted queue, assigns last-used time, inserts it into the persisted LRU map, and marks it persisted.

`dequeueNextReplicaToPersist` lazily skips stale queue entries whose replica map entry was discarded. `getNextCandidateForEviction` removes oldest persisted entries until it finds one still present. `discardReplica` optionally deletes saved persistent copies, removes the in-memory map entry, and removes persisted LRU state while leaving not-persisted queue cleanup lazy.

## Dependencies, Integration, Risks, and Tests

The class depends on Guava `TreeMultimap`, `Time.monotonicNow`, and the abstract `RamDiskReplicaTracker` contract. It integrates with lazy writer scheduling, RAM_DISK eviction, read-hit accounting, and block deletion paths in `FsDatasetImpl`.

Risks include synchronized coarse locking, stale queue growth if many unpersisted replicas are discarded, `recordStartLazyPersist` assuming the replica exists, and LRU timestamp collisions handled by replica comparability. Tests should cover FIFO persistence ordering, failed persist reenqueue, LRU update on touch, eviction candidate selection, discard with and without saved-copy deletion, and stale-entry skipping.
