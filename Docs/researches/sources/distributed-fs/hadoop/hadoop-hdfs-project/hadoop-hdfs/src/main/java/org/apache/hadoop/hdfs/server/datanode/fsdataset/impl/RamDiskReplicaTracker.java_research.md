# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/RamDiskReplicaTracker.java

## Purpose

`RamDiskReplicaTracker` defines the pluggable policy contract for tracking replicas stored on transient RAM_DISK volumes and coordinating their lazy persistence and eviction. It also provides the shared `RamDiskReplica` state object used by implementations.

## Important APIs, Control Flow, and State

`getInstance(Configuration, FsDatasetImpl)` loads the configured tracker class from `DFS_DATANODE_RAM_DISK_REPLICA_TRACKER_KEY`, instantiates it with `ReflectionUtils`, and initializes it with the dataset. The nested `RamDiskReplica` stores block pool id, block id, RAM disk volume, optional lazy-persist volume, saved block/meta files, creation time, read count, locked bytes reservation, and persisted flag. It can record saved files, delete them, compare by block-pool id and block id, and expose the locked reservation.

The abstract operations define the lifecycle: `addReplica`, `touch`, `dequeueNextReplicaToPersist`, `reenqueueReplicaNotPersisted`, `recordStartLazyPersist`, `recordEndLazyPersist`, `getNextCandidateForEviction`, `numReplicasNotPersisted`, `discardReplica`, and `getReplica`. Persistent state exists only as saved block/meta files; the tracker state itself is memory-resident and rebuilt from dataset events.

## Dependencies, Integration, Risks, and Tests

Dependencies include `FsDatasetImpl`, `FsVolumeImpl`, `FsVolumeSpi`, `DFSConfigKeys`, `ReflectionUtils`, and `Time`. The contract is used by DataNode lazy-persist code to schedule writes, account read/eviction metrics, and decide what can be evicted from RAM_DISK.

Risks include policy implementations not honoring synchronization, saved-file deletion being best-effort, proxy policy misconfiguration causing startup failure, and `setLazyPersistVolume` only checking the target is non-transient. Tests should cover reflective construction, base `RamDiskReplica` equality/comparison, saved-file recording/deletion, invalid transient checkpoint volume rejection, and implementation-specific lifecycle behavior.
