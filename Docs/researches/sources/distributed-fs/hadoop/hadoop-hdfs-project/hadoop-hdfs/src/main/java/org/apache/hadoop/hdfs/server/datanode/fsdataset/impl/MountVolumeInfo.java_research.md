# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MountVolumeInfo.java

`MountVolumeInfo` stores per-filesystem-mount metadata for same-disk tiering. It maps `StorageType` to `FsVolumeImpl`, stores optional capacity ratios, and computes default DISK/ARCHIVE splits.

State includes `EnumMap<StorageType, FsVolumeImpl>`, `EnumMap<StorageType, Double>`, and `reservedForArchiveDefault` read from `DFS_DATANODE_RESERVE_FOR_ARCHIVE_DEFAULT_PERCENTAGE` and clamped to `[0, 1]`. `getVolumeRef` obtains a referenced volume for a storage type and returns null if absent or closed. `getCapacityRatio` returns an explicit ratio, otherwise leftover capacity when another type has a ratio, otherwise a DISK/ARCHIVE default split when both storage types share a mount, otherwise 1. `addVolume` rejects duplicate storage types, `removeVolume` clears volume and ratio, and `setCapacityRatio` fails if the sum would exceed 1.

The class is runtime-only and persists no state. It influences capacity reporting and same-mount block movement through `MountVolumeMap`, `FsVolumeList`, `FsVolumeImpl`, and `FsDatasetImpl`.

Risks include surprising leftover ratios, duplicate storage type logging without throwing, null references from closed volumes, and partial validation limited to sum <= 1. Tests should cover clamping, explicit/default/leftover ratios, duplicate rejection, closed references, removal cleanup, and ratio sum failures.
