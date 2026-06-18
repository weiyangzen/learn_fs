# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/PacketHeader.java

## Purpose
`PacketHeader` represents the per-packet wire header for HDFS block data transfer. It describes block offset, packet sequence number, last-packet marker, data length, and optional sync-block flag, excluding checksums and data payload.

## Important APIs, Types, and Functions
The serialized header consists of a 4-byte packet length, a 2-byte protobuf-header length, and a `PacketHeaderProto`. `PKT_LENGTHS_LEN` is 6 bytes and `PKT_MAX_HEADER_LEN` is the length prefix plus the maximum default protobuf size.

Constructors either create an empty object for reading or build a proto from packet fields. The packet length must be at least four bytes. `syncBlock` is only set in the proto when true to avoid changing the header length unnecessarily. Getters expose proto fields and packet length.

`readFields` parses from a `ByteBuffer` or `DataInputStream`. `setFieldsFromData` parses a supplied header byte array. `putInBuffer`, `write`, and `getBytes` serialize the header. `sanityCheck` enforces positive data length except for the last packet, zero data length for the last packet, and sequence number increment by one.

## Control Flow
Writers construct and serialize headers before checksums/data. Receivers parse length prefixes and protobuf bytes, then validate sequencing through `sanityCheck` in higher-level code.

## State and Persistence Behavior
The object stores mutable `packetLen` and `proto` fields after construction/parsing. Wire format is compatibility-sensitive; comments note Hadoop 2.0.0-alpha incompatibility around variable-length headers and `syncBlock`.

## Dependencies and Integration Points
It depends on `PacketHeaderProto`, `ByteBufferOutputStream`, shaded protobuf, and Guava primitive byte sizes. It integrates with `PacketReceiver`, `BlockReceiver`, DFS output stream packet creation, and DataNode/client data pipelines.

## Risks and Edge Cases
The maximum proto size is computed from default fields and enforced with asserts, not runtime exceptions. Negative proto lengths or malformed protobufs surface during reads. `equals` compares only proto, not packet length; `hashCode` is seqno only. Compatibility depends on preserving prefix layout and optional `syncBlock` behavior.

## Test Signals
Packet receiver and data transfer tests should cover serialization round trips, sanity checks, last-packet rules, malformed lengths, sync-block headers, and equality behavior.
