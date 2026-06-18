# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/FsVolumeSpi.java

Purpose: defines the storage-volume contract beneath `FsDatasetSpi`. It exposes capacity/location/type, block-pool iteration, directory scan data, space reservation, IO provider, metrics, and health checking.

Important APIs/types/functions: core methods include `obtainReference`, `getStorageID`, `getBlockPoolList`, `getAvailable`, `getBaseURI`, `getStorageLocation`, `getStorageType`, `isTransientStorage`, `reserveSpaceForReplica`, `releaseReservedSpace`, `releaseLockedMemory`, `newBlockIterator`, `loadBlockIterator`, `compileReport`, `loadLastPartialChunkChecksum`, `getFileIoProvider`, and `getMetrics`. Nested `BlockIterator` supports persistent iteration state for scanners. Nested `ScanInfo` compactly represents block/meta files or provided-storage `FileRegion`s.

Control flow: DataNode services obtain a reference before IO, reserve space for writes, scan volumes through `compileReport` and `ScanInfo`, and use `BlockIterator` for incremental block scanning. `ScanInfo` reconstructs full block/meta paths from compact suffixes and compares/equates by block ID.

State and persistence: implementations persist block files, metadata files, iterator checkpoints, and volume health information. `ScanInfo` caches block length at construction time, so later disk changes are not reflected. Block iterators may save their position to the volume.

Dependencies and integration points: connects to `DF`, `StorageLocation`, `StorageType`, `ExtendedBlock`, `FileRegion`, `ReportCompiler`, `FileIoProvider`, `VolumeCheckResult`, `DataNodeVolumeMetrics`, and checksum utilities.

Risks: `ScanInfo` assumes path prefix relationships and throws runtime exceptions if violated. Cached scan lengths can be stale. Iterator staleness is explicit; consumers must handle deleted or changed blocks. Space reservation and locked-memory release must respect OS page rounding in implementations.

Test signals: scan info path reconstruction, generation stamp extraction, provided-storage scan info, block iterator save/load/rewind/staleness behavior, health checks, storage-type predicates, and reservation release accounting.
