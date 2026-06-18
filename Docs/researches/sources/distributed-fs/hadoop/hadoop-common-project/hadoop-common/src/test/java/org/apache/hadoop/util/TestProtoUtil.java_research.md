# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestProtoUtil.java

Purpose: tests protobuf utility compatibility for raw varint decoding and RPC request header client IDs.

Important APIs and types: `ProtoUtil.readRawVarint32`, `ProtoUtil.makeRpcRequestHeader`, protobuf `CodedOutputStream`, `RpcRequestHeaderProto`, `RpcKind`, `OperationProto`, `RpcConstants.INVALID_RETRY_COUNT`, and `ClientId`.

Control flow: `testVarInt` encodes fixed positive/negative boundary values and bit-pattern sweeps using protobuf's own writer, then decodes with Hadoop's reader and expects the original int. `testRpcClientId` obtains a client UUID and asserts `makeRpcRequestHeader` preserves it byte-for-byte in the protobuf header.

State and persistence: in-memory byte arrays and protobuf objects only.

Dependencies and integration points: validates Hadoop IPC's protobuf framing and client identity propagation against the third-party protobuf implementation.

Risks: varint sign/overflow handling, stream termination mistakes, and client-ID truncation would break RPC compatibility. Test signals compare decoded ints and client-id bytes.
