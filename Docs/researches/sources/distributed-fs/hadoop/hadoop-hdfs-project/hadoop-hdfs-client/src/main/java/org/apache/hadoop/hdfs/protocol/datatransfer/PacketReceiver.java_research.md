# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/PacketReceiver.java

## Purpose
`PacketReceiver` reads one HDFS data transfer packet at a time from an `InputStream` or `ReadableByteChannel`, parses the header, and exposes slices for checksums and data. It is used on both read and write pipeline paths.

## Important APIs, Types, and Functions
`MAX_PACKET_SIZE` is loaded from `DFS_DATA_TRANSFER_MAX_PACKET_SIZE` using a fresh `HdfsConfiguration`. The constructor chooses heap or direct buffers and allocates enough space for length prefixes.

`receiveNextPacket` delegates to `doRead`. `getHeader`, `getDataSlice`, and `getChecksumSlice` expose the most recently parsed packet. `mirrorPacketTo` writes the full last packet to an output stream, only for heap buffers. `close` returns direct buffers to a static `DirectBufferPool`.

`doRead` reads packet length and header length, validates payload and total sizes, reallocates the buffer if needed, reads the rest, parses `PacketHeader`, computes checksum length as `dataPlusChecksumLen - dataLen`, and calls `reslicePacket`.

## Control Flow
The receiver first reads the fixed 6-byte length prefix, then reads the variable header/checksum/data region. `Preconditions.checkState` prevents reading past a last-packet marker. `doReadFully` dispatches to channel reads or array-backed stream reads. `readChannelFully` loops until the buffer is full or throws premature EOF.

## State and Persistence Behavior
The object keeps the current full packet buffer plus slices and header. Direct buffers are pooled and should be returned by `close`; `finalize` attempts cleanup as a fallback. Slices are views into `curPacketBuf` and become invalid after reading the next packet.

## Dependencies and Integration Points
It depends on `PacketHeader`, `DirectBufferPool`, `HdfsClientConfigKeys`, `IOUtils`, and Java NIO buffers/channels. It is used by DataNode `BlockReceiver`, client-side block readers, and tests under `protocol/datatransfer/TestPacketReceiver.java`.

## Risks and Edge Cases
Malformed lengths can cause OOME if not capped, so `MAX_PACKET_SIZE` validation is critical. The InputStream path requires heap buffers; direct buffers are only safe with channels. `mirrorPacketTo` only works for non-direct buffers. Buffer reuse means callers must consume slices before the next receive. `finalize` is a weak safety net and close discipline matters.

## Test Signals
`TestPacketReceiver` covers packet receiving, mirroring, and configured max packet size. Additional tests should cover negative header lengths, payload length below four, oversized packets, premature EOF, direct-buffer close/pool behavior, and reading after last packet.
