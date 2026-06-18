# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeVolumeMetrics.java

Purpose: validates per-volume file I/O profiling metrics for DataNode volumes. It uses one DataNode, two storage types (`RAM_DISK`, `DISK`), two storages per DN, and 100 percent sampling to make metric increments observable.

Important APIs and types: `DataNodeVolumeMetrics`, `FsVolumeSpi`, `MiniDFSCluster`, `SimulatedFSDataset`, `ExtendedBlock`, `DFSOutputStream`, `FSDataOutputStream`, metrics asserts, and DataNode volume departure/arrival utilities.

Control flow: `setupClusterForVolumeMetrics` enables `dfs.datanode.fileio.profiling.sampling.percentage`, installs `SimulatedFSDataset`, and builds a storage-typed cluster. `testVolumeMetrics` creates a file larger than `Integer.MAX_VALUE`, appends data, calls `hsync`, then resolves the first block to its volume and validates metric counters/tags. `testVolumeMetricsWithVolumeDepartureArrival` repeats the workload, injects a second-volume failure, validates metrics while a volume is failed, restores/reconfigures the volume, and validates again. `testWriteIoVolumeMetrics` checks sample-count relationships before and after append plus `hflush`.

State and persistence behavior: metric state lives on each `FsVolumeSpi` via `DataNodeVolumeMetrics`; cluster data is transient. Integration points include append, flush, sync, block-to-volume lookup, and volume reconfiguration. Risks include metric sampling configuration, simulated dataset behavior versus real disks, huge logical file lengths, and assumptions about count ordering. Test signals include `TotalDataFileIos`, `VolumeName`, nonzero write counts, zero sync before explicit sync, and monotonic write sample growth after append.
