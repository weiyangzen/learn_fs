# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcWritable.java

## Purpose
`RpcWritable` is the serialization abstraction used by Hadoop IPC for shaded protobuf messages, legacy unshaded protobuf messages, built-in Writables, and raw request/response buffers.

## Important APIs, Types, and Functions
`wrap(Object)` chooses `RpcWritable`, shaded `Message`, legacy protobuf, or `Writable` adapters. Old `Writable.readFields/write` are disabled. `WritableWrapper`, `ProtobufWrapper`, and `Buffer` implement optimized `writeTo` and `readFrom`. `Buffer.getValue` decodes a value from its current `ByteBuffer`.

## Control Flow
Serialization writes directly to `ResponseBuffer` with capacity preallocation. Shaded protobuf parsing reads a delimited message through `CodedInputStream` and advances the byte buffer by consumed bytes. `Buffer.readFrom` slices the remaining bytes and consumes them from the caller by changing the limit.

## State and Persistence Behavior
State is in-memory wrapper payload or byte buffer. No durable persistence is performed.

## Dependencies and Integration Points
It integrates with `Client`, `Server`, protobuf engines, SASL client access, `ResponseBuffer`, and tests in `TestRPC`/response buffer suites.

## Risks and Test Signals
Risks include assuming array-backed byte buffers, incorrect buffer position advancement, disabled writable methods surprising callers, and legacy protobuf detection order. Tests should cover shaded/legacy/writable round trips, raw buffer slicing, non-array buffers, and capacity preallocation.
