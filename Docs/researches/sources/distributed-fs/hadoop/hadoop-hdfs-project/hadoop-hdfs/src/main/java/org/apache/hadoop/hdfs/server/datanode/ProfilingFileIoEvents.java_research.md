# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ProfilingFileIoEvents.java

Purpose: `ProfilingFileIoEvents` records sampled latency and error metrics for DataNode metadata and data-file IO operations. `FileIoProvider` calls it before and after each wrapped operation.

Important APIs: `beforeMetadataOp` and `afterMetadataOp` time metadata operations. `beforeFileIo` samples data IO according to `sampleRangeMax`; `afterFileIo` records aggregate data IO latency plus operation-specific latencies for sync, flush, read, write, transfer, and native copy. `onFailure` records IO error latency. `setSampleRangeMax`, `getDiskStatsEnabled`, and `getSampleRangeMax` expose configuration/test behavior.

Control flow and state: the constructor reads `DFS_DATANODE_FILEIO_PROFILING_SAMPLING_PERCENTAGE_KEY`. `setSampleRangeMax` enables profiling through `Util.isDiskStatsEnabled`, caps percentages above 100 with a warning, and converts percentage to an `Integer.MAX_VALUE` sampling threshold. Metadata operations are not sampled once enabled; file IO is sampled by `ThreadLocalRandom`.

State and persistence: state is volatile `isEnabled` and `sampleRangeMax`. Metrics persist externally in each `DataNodeVolumeMetrics` instance reachable from the operation volume. A begin timestamp of `0` marks an unsampled or disabled operation and suppresses after-file metrics.

Dependencies and integration points: it depends on `FsVolumeSpi`, `DataNodeVolumeMetrics`, `FileIoProvider.OPERATION`, `DFSConfigKeys`, `Util`, and `Time`. It is created by `FileIoProvider` and therefore affects all provider-mediated disk operations.

Risks: `onFailure` records `Time.monotonicNow() - begin` even when `begin` is `0`, so disabled/unsampled failures can produce a large duration if `isEnabled` is true but begin was not captured. Null volumes silently skip metrics. Percentages below or equal to zero disable stats through `Util`.

Test signals: validate percentage-to-threshold conversion for 0, normal, and >100 values; metadata latency when enabled; sampled and unsampled file IO; per-operation latency routing; null-volume no-op; and failure metrics when begin is zero/non-zero.
