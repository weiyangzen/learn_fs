# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSStripedOutputStream.java

## Purpose

`DFSStripedOutputStream` implements HDFS client writes for erasure-coded striped files. It extends `DFSOutputStream` but replaces the single replicated `DataStreamer` with one `StripedDataStreamer` per data/parity unit, coordinates block-group allocation, generates parity cells, handles partial final stripes, and performs EC-aware pipeline recovery.

## Important APIs, Types, and Functions

Nested `MultipleBlockingQueue` provides one bounded queue per streamer. `Coordinator` distributes following blocks, end-block notifications, updated blocks, and streamer-update results. `CellBuffers` holds one cell buffer per data/parity unit plus checksum arrays for parity chunks. Core methods include constructors, `setCurrentStreamer`, `encode`, `writeChunk`, `writeParityCells`, `writeParity`, `allocateNewBlock`, `enqueueAllCurrentPackets`, `flushAllInternals`, `checkStreamerFailures`, `markExternalErrorOnStreamers`, `updateBlockForPipeline`, `updatePipeline`, `getAckedLength`, `generateParityCellsForLastStripe`, `closeImpl`, `closeThreads`, and `logCorruptBlocks`. `hflush`, `hsync`, and `hasCapability` are overridden to indicate sync is not supported.

## Control Flow

Writes fill the current data cell in `CellBuffers` and also call the parent `writeChunk` for the current data streamer if it is healthy. When a data cell fills, the stream advances to the next data streamer. When all data cells in a stripe are full, it flips data buffers, encodes parity buffers with the configured raw encoder, writes parity chunks through parity streamers, clears cell buffers, and either ends a full block group or checks streamer failures. New block groups are allocated only after all healthy streamers have ended the previous group; the returned `LocatedStripedBlock` is split into internal blocks and queued to each streamer. Close flushes upper buffers, pads and encodes a final partial stripe if needed, enqueues all current packets, flushes all streamers in parallel, sends final empty close packets, force-closes streamer threads, completes the block group at the NameNode, logs corrupt-block-group risk, releases the encoder, and shuts down the flush executor.

## State and Persistence Behavior

Runtime state includes the EC policy, raw encoder, cell size, data/parity counts, streamers, current packet per streamer, current and previous block groups, failed streamers, corrupt-block counts per block group, coordinator queues, flush executor, datanode restart timeout, and configured failed-block tolerance. Persistent HDFS metadata is updated through inherited `addBlock`, NameNode `updateBlockForPipeline`, `updatePipeline`, and `complete` calls. `currentBlockGroup.numBytes` represents logical block-group bytes sent and is temporarily reduced to acked length during NameNode pipeline updates.

## Dependencies and Integration Points

It depends on `DFSOutputStream`, `StripedDataStreamer`, `ClientProtocol`, `StripedBlockUtil`, `LocatedStripedBlock`, `ErasureCodingPolicy`, `RawErasureEncoder`, `CodecUtil`, `DataChecksum`, `ByteBufferPool`, datatransfer construction stages, and HDFS EC write failure-tolerance configuration. It shares packet construction, checksum calculation, caching strategy, block allocation, lease handling, and completion behavior with the replicated output stream but coordinates many internal streams through `Coordinator`.

## Risks and Edge Cases

The class must preserve the invariant that at least the configured tolerated number of failed blocks is not exceeded; otherwise it closes all streamers and fails the write. Partial-stripe parity pads shorter cells to the parity cell size, and parity lengths must match EC layout expectations. `getAckedLength` is subtle: it computes durable full stripes and at most one partial stripe from per-streamer block lengths, unhealthy streamers, and expected parity lengths. `hflush`/`hsync` are unsupported even though the base class supports them, so callers must check capabilities. Recovery relies on external-error signaling, block generation-stamp bumps, streamer update queues, and timeouts; slow streamer updates can be force-closed. Parity block allocation can be missing when the cluster lacks enough topology, leaving parity streamers failed but possibly within tolerance.

## Test Signals

Tests should exercise EC stream creation and append, full-stripe parity generation, partial final-stripe padding and parity, block-group rollover, unsupported sync capability, parity-streamer absence, failed-streamer tolerance boundaries, block group pipeline update with acked length, concurrent flush-all error propagation, close with good streamers >= data units, corrupt-block risk logging, direct-buffer encoder preference, and replacement of failed streamers on new block groups.
