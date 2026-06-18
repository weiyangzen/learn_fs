# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/FsDatasetSpi.java

Purpose: defines the main service-provider interface for DataNode replica storage. The default implementation is local-disk `FsDatasetImpl`, but the SPI also allows simulated or custom storage backends.

Important APIs/types/functions: nested `Factory` loads `DFS_DATANODE_FSDATASET_FACTORY_KEY` with `ReflectionUtils` and creates datasets. `FsVolumeReferences` is a closeable snapshot of referenced volumes. Core methods cover volume lifecycle (`addVolume`, `removeVolumes`, `getStorageReports`), replica lookup (`getReplica`, `getStoredBlock`, `getLength`, `getBlockInputStream`), write lifecycle (`createTemporary`, `createRbw`, `append`, `recoverAppend`, `recoverRbw`, `recoverClose`, `finalizeBlock`, `unfinalizeBlock`), block reports, cache operations, invalidation, block-pool lifecycle, trash/rolling-upgrade markers, lazy persist callbacks, pinning, block moves, and dataset locking.

Control flow: callers obtain references with `getFsVolumeReferences()` when iterating volumes, use read/write/recovery methods during the DataNode data-transfer pipeline, and use report/cache/invalidation methods from NameNode command handling. `FsVolumeReferences` skips closed volumes, exposes read-only iteration, and releases all references on `close()`.

State and persistence: this file is contractual, not a state holder. Its methods describe persistence responsibilities for implementations: block files, metadata files, block-pool directories, cache state, trash, rolling upgrade markers, and volume maps. `acquireDatasetLockManager()` documents coordination around in-memory replica maps.

Dependencies and integration points: integrates DataNode, DataStorage, `ExtendedBlock`, `ReplicaInfo`, `ReplicaHandler`, `StorageReport`, NameNode protocol types, block scanner scan info, `MountVolumeMap`, `FsVolumeImpl`, and `FSDatasetMBean`. It is the central boundary between DataNode services and physical storage.

Risks: broad SPI changes have large blast radius. Many methods assume correct locking by callers or implementations. Deprecated `getReplica` still exposes mutable replica metadata. Reference leaks from `FsVolumeReferences` can prevent volume removal. Recovery methods must maintain exact generation stamp and length semantics.

Test signals: implementation conformance tests should cover volume add/remove, block write/finalize/recover, invalidation, cache reporting, trash behavior, rolling-upgrade markers, locking during scans, and failure paths for missing replicas or failed volumes.
