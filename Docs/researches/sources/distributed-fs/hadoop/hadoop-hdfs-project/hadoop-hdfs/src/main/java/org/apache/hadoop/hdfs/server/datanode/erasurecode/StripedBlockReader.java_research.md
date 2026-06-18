<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockReader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockReader.java

## Purpose

`StripedBlockReader` reads one source internal block from a source DataNode into a buffer for erasure-code reconstruction. It wraps remote `BlockReader` creation, read execution, corruption reporting, and local/remote byte metrics.

## Important APIs, Types, And Functions

- Constructor captures source index, internal block, source datanode, and starting offset, then attempts to create a block reader.
- `createBlockReader` obtains a read token, opens a peer socket, performs SASL/encryption setup, and creates a `BlockReaderRemote`.
- `readFromBlock(int, CorruptedBlocks)` returns a `Callable<BlockReadStats>`.
- `actualReadFromBlock` fills the buffer and increments reconstructor bytes-read metrics.
- `resetBlockReader`, `closeBlockReader`, `getReadBuffer`, and `freeReadBuffer` manage lifecycle.

## Control Flow

The reader refuses to open when the offset is beyond block length. Reads set the buffer limit to the requested length, loop until the buffer is filled or no more bytes are returned, report checksum exceptions as corrupted blocks, and close/reopen readers when `StripedReader` retries slow or failed sources.

## State And Persistence

State includes the parent `StripedReader`, DataNode, configuration, source index, internal block, source datanode, `BlockReader`, read buffer, and local-peer flag. It has no persistent output; it reads existing block data.

## Dependencies And Integration Points

It integrates DataNode token generation, SASL/encryption, `DFSUtilClient.peerFromSocketAndKey`, `BlockReaderRemote`, `CorruptedBlocks`, fault injectors, and `StripedReader` retry logic.

## Risks And Edge Cases

Short-circuit local reads are intentionally not used. Connection or token failures produce a null reader and source fallback. Buffer ownership is shared with the parent, so cleanup must avoid leaks. Checksum exceptions must be reported to the NameNode through the corrupted-block accumulator.

## Test Signals

Tests should cover successful remote reads, local-peer metric classification, offset-at-end behavior, connection failure fallback, checksum exception reporting, buffer allocation/freeing, reset behavior, and interruption/fault-injection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockReader.java -->
