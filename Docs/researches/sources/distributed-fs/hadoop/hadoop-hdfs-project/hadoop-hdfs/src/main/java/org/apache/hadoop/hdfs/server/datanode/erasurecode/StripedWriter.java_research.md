<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedWriter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedWriter.java

## Purpose

`StripedWriter` manages all target writers for a striped reconstruction task. It chooses which missing internal block indices to reconstruct, initializes target streams, provides decoder output buffers, packet/checksum workspace, and sends data/end packets to still-healthy targets.

## Important APIs, Types, And Functions

- Constructor validates target count, computes target indices from missing live-bitset entries and exclusion bitset, and sets maximum target length in the reconstructor.
- `init()` derives packet sizing from checksum settings, allocates packet/checksum buffers, and initializes target streams.
- `transferData2Targets()` sends current buffers to active targets and disables failed targets.
- `getRealTargetIndices`, `getRealTargetBuffers`, and `updateRealTargetBuffers` expose active decode outputs and trim buffers for short final internal blocks.
- `endTargetBlocks`, `clearBuffers`, and `close` manage lifecycle.

## Control Flow

Target index initialization scans all data and parity positions, selecting missing, positive-length, non-excluded indices in target order. During each reconstruction loop, active target buffers become decoder outputs; after decode, limits are adjusted to actual remaining block length; then packets are sent and failed targets are marked inactive.

## State And Persistence

State includes targets, target indices, storage types/ids, active-status booleans, per-target `StripedBlockWriter`s, packet buffer, checksum buffer, bytes-per-checksum, checksum size, and chunks-per-packet. Persistent effects are delegated to per-target writers.

## Dependencies And Integration Points

It integrates `StripedBlockWriter`, `StripedReconstructor`, DataNode networking, EC policy geometry, `PacketHeader`, `DataChecksum`, `StorageType`, and target storage ids from the NameNode command.

## Risks And Edge Cases

Target indices must align with the target datanode/storage arrays. Excluded reconstructed indices can make some missing blocks intentionally skipped. All-target failure aborts reconstruction. Buffer limits must be restored/cleared between rounds to avoid stale data.

## Test Signals

Tests should cover target index selection, exclusion handling, max target length, packet/checksum buffer sizing, partial final block limits, failed target deactivation, all-target failure, end packets, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedWriter.java -->
