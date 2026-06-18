# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MountVolumeMap.java

`MountVolumeMap` maps filesystem mount strings to `MountVolumeInfo` for same-disk tiering. It lets the dataset select a counterpart storage type on the same mount and apply per-mount capacity ratios.

It owns a `ConcurrentMap<String, MountVolumeInfo>` and `Configuration`. `getVolumeRefByMountAndStorageType` returns a referenced volume or null. `getCapacityRatioByMountAndStorageType` returns the mount/type ratio or 1 for unknown mounts. `addVolume` ignores empty mount strings, creates mount info when needed, and delegates insertion. `removeVolume` removes by storage type and drops empty mount entries. `setCapacityRatio` delegates validation and throws `IOException` when ratios exceed 1. `hasMount` exposes map membership.

All state is runtime-only and derived from active volumes plus configuration. It is created by `FsVolumeList`, exposed through `FsDatasetImpl.getMountVolumeMap`, used by `FsVolumeImpl` capacity/non-DFS calculations, and consulted by `FsDatasetImpl.moveBlockAcrossStorage` for same-mount moves.

Risks include unsynchronized updates inside each `MountVolumeInfo`, empty mount strings disabling tiering, configuration failures during volume add, and null lookups during concurrent removal. Tests should cover add/remove lifecycle, empty-mount no-op behavior, unknown-mount defaults, ratio exception behavior, concurrent lookup/removal tolerance, and `hasMount` visibility.
