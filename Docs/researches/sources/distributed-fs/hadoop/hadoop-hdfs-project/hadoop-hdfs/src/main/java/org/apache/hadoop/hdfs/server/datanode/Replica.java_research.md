<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/Replica.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/Replica.java

## Purpose

`Replica` is the private DataNode interface for block replica metadata. It defines the common read-only contract that local, in-pipeline, recovery, and provided replicas expose to the dataset, scanner, and protocol code.

## Important APIs, Types, And Functions

- Identity and version APIs: `getBlockId()`, `getGenerationStamp()`, and `getState()`.
- Length APIs distinguish received bytes, bytes durable on disk, and bytes visible to readers through `getNumBytes()`, `getBytesOnDisk()`, and `getVisibleLength()`.
- Placement APIs expose `getStorageUuid()`, `isOnTransientStorage()`, and `getVolume()`.
- The state type is `HdfsServerConstants.ReplicaState`; the volume type is `FsVolumeSpi`.

## Control Flow

The interface has no implementation flow. It standardizes how higher-level code can branch on replica state and length without knowing whether the implementation is finalized, being written, under recovery, waiting recovery, temporary, or provided.

## State And Persistence

Implementations back the interface with in-memory block map entries plus local files, remote file regions, reservation counters, or recovery wrappers. The interface itself persists nothing.

## Dependencies And Integration Points

`ReplicaInfo` implements this interface and adds storage URI, stream, mutation, scanner, and recovery operations. Dataset maps, volume scanners, block senders, and recovery code depend on this lightweight contract to inspect replicas safely.

## Risks And Edge Cases

The three length methods intentionally mean different things; misuse can expose unacknowledged bytes or under-report recoverable data. `getVolume()` and storage UUID access assume an attached volume, which can be false in some test or checksum utility paths for lower-level subclasses.

## Test Signals

Tests should assert each replica subtype reports the correct `ReplicaState`, visible length, bytes-on-disk semantics, storage UUID, and transient-storage flag, especially across transitions from temporary/RBW to finalized/RWR/RUR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/Replica.java -->
