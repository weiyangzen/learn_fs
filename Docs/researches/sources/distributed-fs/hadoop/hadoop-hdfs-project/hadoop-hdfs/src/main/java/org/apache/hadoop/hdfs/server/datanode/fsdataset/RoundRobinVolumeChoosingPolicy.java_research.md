# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/RoundRobinVolumeChoosingPolicy.java

Purpose: implements `VolumeChoosingPolicy` by selecting volumes in round-robin order among volumes of the same storage type, while ensuring enough available space exists.

Important APIs/types/functions: `setConf` reads `DFS_DATANODE_ROUND_ROBIN_VOLUME_CHOOSING_POLICY_ADDITIONAL_AVAILABLE_SPACE_KEY`; `chooseVolume(List<V>, long, String)` validates non-empty volume list, picks a storage-type-specific lock/cursor, and calls the private chooser. The private `chooseVolume` scans volumes once from the current cursor and returns the first with `available > blockSize + additionalAvailableSpace`.

Control flow: one cursor and lock are maintained per `StorageType.ordinal()`. On success, the cursor advances to the next volume. On failure, it logs each insufficient volume and throws `DiskOutOfSpaceException` with the largest available space observed.

State and persistence: `curVolumes` and `syncLocks` are in-memory arrays sized to `StorageType.values().length`. There is no persistence. The configured additional-space threshold is stored as a long.

Dependencies and integration points: used by dataset volume selection for new replicas. Depends on Hadoop `Configurable`, `StorageType`, `DFSConfigKeys`, and `DiskChecker.DiskOutOfSpaceException`.

Risks: the `storageId` hint is ignored. Volumes must all share a storage type as assumed by the comment. The strict `>` comparison rejects exactly equal available space. StorageType enum changes affect array indexing. Caller must synchronize mutations to the volume list.

Test signals: empty list exception, cursor advancement, per-storage-type independent cursors, additional-space threshold behavior, wraparound, and failure message with max available space.
