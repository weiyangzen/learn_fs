<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockWriter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockWriter.java

## Purpose

`StripedBlockWriter` owns the connection and packet stream for writing one reconstructed internal block to one target DataNode.

## Important APIs, Types, And Functions

- Constructor captures block, target, storage type/id, allocates target buffer, and initializes the transfer stream.
- `init()` opens a socket, performs SASL/encryption setup, sends `writeBlock` with `PIPELINE_SETUP_CREATE`, and stores input/output streams.
- `transferData2Target(byte[])` calculates chunk checksums, builds `DFSPacket`s, writes checksum and data, and advances block offset and sequence number.
- `endTargetBlock(byte[])` sends the final empty packet and flushes.
- `close()` releases streams and socket; `freeTargetBuffer()` returns buffer to the reconstructor pool.

## Control Flow

Initialization must fully succeed or clean up all partially opened resources. During transfer, empty buffers are skipped. Direct buffers use a temporary direct checksum buffer; heap buffers use array checksumming. Data is split into packets bounded by `maxChunksPerPacket`.

## State And Persistence

Runtime state includes target socket/streams, target buffer, current target block offset, sequence number, and block/storage identity. Persistent effect is the target DataNode receiving packets for a new block replica.

## Dependencies And Integration Points

It integrates `StripedWriter`, DataNode socket/token/SASL APIs, `Sender.writeBlock`, `DFSPacket`, checksum calculation, `PacketHeader`, and fault injection.

## Risks And Edge Cases

The code does not read or validate packet acknowledgements. Direct-buffer checksum calculation must copy checksum bytes before returning temporary buffer. Initialization failure must free the target buffer to avoid leaks. Packet offsets and sequence numbers must remain monotonic.

## Test Signals

Tests should cover create-block handshake parameters, heap/direct checksum paths, packet sizing, empty-buffer skip, final packet emission, failure cleanup, byte metrics, and socket/SASL error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockWriter.java -->
