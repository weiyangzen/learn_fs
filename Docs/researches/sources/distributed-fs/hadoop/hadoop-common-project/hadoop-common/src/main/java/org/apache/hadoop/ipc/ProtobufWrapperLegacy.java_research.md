# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtobufWrapperLegacy.java

## Purpose
`ProtobufWrapperLegacy` adapts unshaded `com.google.protobuf.Message` instances to `RpcWritable`, isolating legacy protobuf references from most of the RPC codebase and allowing runtime absence when legacy messages are not used.

## Important APIs, Types, and Functions
The constructor validates payloads through `isUnshadedProtobufMessage`. `writeTo` writes a delimited protobuf into `ResponseBuffer`. `readFrom` parses a delimited message from a byte-array-backed `ByteBuffer`. `PROTOBUF_KNOWN_NOT_FOUND` avoids repeated class loading failures.

## Control Flow
Wrapping first checks class availability and assignability. Serialization precomputes delimited size and ensures response buffer capacity. Deserialization reads the varint length, pushes a coded-input limit, parses through the message parser, checks the final tag, and advances the source buffer by consumed bytes.

## State and Persistence Behavior
State is the current legacy protobuf message and the static classpath-absence flag. No persistence is performed.

## Dependencies and Integration Points
It is used by `RpcWritable.wrap` and legacy protobuf server/client compatibility paths in `ProtobufRpcEngine` and `ProtobufRpcEngine2`.

## Risks and Test Signals
Risks include byte-buffer array assumptions, parser limit mistakes, stale classpath absence caching in exotic classloader scenarios, and legacy dependency drift. Tests should verify wrap detection with and without unshaded protobuf, round-trip serialization, and buffer position advancement.
