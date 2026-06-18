<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedReader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedReader.java

## Purpose

`StripedReader` coordinates source reads for EC reconstruction. It keeps a set of source block readers, reads the minimum number of live internal blocks required for decoding, retries slow or failed sources, pads zero-length stripes, and exposes decoder input buffers.

## Important APIs, Types, And Functions

- Constructor computes data/parity counts, minimum required sources, xmits, live sources, and read service.
- `init()` initializes readers, buffer size, and zero-stripe buffers.
- `readMinimumSources(int)` reads enough source data and reports corrupted blocks.
- `doReadMinimumSources` schedules preferred reads, consumes completions, retries failed/time-out reads, and returns the updated success list.
- `getInputBuffers(int)` returns decoder input buffers indexed by internal block index, including padded zero stripes.
- `close`, `clearBuffers`, `getChecksum`, `getBufferSize`, and `getMinRequiredSources` manage lifecycle and metadata.

## Control Flow

Initialization opens readers for the first usable minimum source set and verifies checksums match. Each iteration tries the previous success list first, submits read callables, waits for completions with timeout, replaces failed or slow sources from unused sources, and cancels stale reads once enough successes are available.

## State And Persistence

State includes source indices and datanodes, `StripedBlockReader` list, current success list, read futures, checksum, buffer size, zero-stripe buffers/indices, and completion service. It reads existing block data and does not persist output.

## Dependencies And Integration Points

It integrates `StripedReconstructor`, `StripedBlockReader`, `StripedBlockUtil` read-result helpers, `DFSUtilClient.CorruptedBlocks`, `DataChecksum`, DataNode reporting, and EC policy geometry.

## Risks And Edge Cases

Minimum sources can be less than data units for short block groups, requiring zero padding. Timeout handling schedules replacement reads but stale futures must be canceled and drained. Checksum mismatch is asserted, not gracefully handled. Padding mutates buffer positions/limits for decoder expectations.

## Test Signals

Tests should cover minimum-source calculation for short groups, source fallback after failure and timeout, corruption reporting, zero-stripe padding, buffer-size alignment to checksum chunks, stale future cleanup, checksum initialization, and close/free behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedReader.java -->
