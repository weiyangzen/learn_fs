# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/VolumeChoosingPolicy.java

Purpose: generic policy interface for selecting a volume on which to place a replica.

Important APIs/types/functions: single method `chooseVolume(List<V> volumes, long replicaSize, String storageId)` returns a chosen `FsVolumeSpi` subtype or throws `IOException` when storage is unavailable or full. The `storageId` parameter carries a NameNode-nominated storage ID that policies may use or ignore.

Control flow: dataset write paths pass candidate volumes and expected replica size to an implementation. The interface explicitly states that callers should synchronize access to the volume list.

State and persistence: no state or persistence in the interface. Implementations may maintain in-memory selection cursors, available-space thresholds, or storage-id mappings.

Dependencies and integration points: implemented by `RoundRobinVolumeChoosingPolicy` and potentially other storage policies. Used by `FsVolumeList`/dataset allocation code when creating temporary or RBW replicas.

Risks: implementations must handle empty, stale, or concurrently modified volume lists. Misinterpreting `replicaSize` can overcommit space. Ignoring `storageId` may conflict with NameNode placement nominations in specialized deployments.

Test signals: implementation contract tests should cover empty candidate lists, full volumes, storage ID hints, concurrency around shared candidate lists, and propagation of IO exceptions from volume availability checks.
