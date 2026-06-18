# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRpcWritable.java

## Purpose

`TestRpcWritable` validates `RpcWritable` wrappers for classic Hadoop `Writable` values, shaded protobuf messages, and nested `RpcWritable.Buffer` slices. It protects the byte-buffer decoding contract used by mixed IPC payload formats.

## Important APIs, Types, And Functions

The tests use `RpcWritable.wrap(Writable)`, `RpcWritable.wrap(Message)`, `RpcWritable.Buffer.wrap(ByteBuffer)`, `Buffer.getValue(defaultProto)`, and `Buffer.newInstance(Class, Configuration)`. Test fixtures are a `LongWritable` initialized from `Time.now()` and two `EchoRequestProto` messages.

## Control Flow

The tests serialize a value or sequence of values to a `ByteArrayOutputStream`, wrap the resulting bytes in a `ByteBuffer`, then decode through the appropriate `RpcWritable` path. The nested-buffer test first consumes a `LongWritable`, then extracts the remaining bytes into a nested buffer and decodes two protobuf messages from the slice.

## State And Persistence Behavior

All state is in-memory `ByteBuffer` position and remaining-byte counters. The tests assert that wrapper reads advance the original buffer consistently and that nested buffer extraction drains the parent while preserving the child slice.

## Dependencies And Integration Points

This file integrates with Hadoop `Writable`, shaded protobuf `Message`, generated IPC test protos, `RpcWritable`, and byte-buffer based RPC decoding. It is a low-level serialization compatibility check for both protobuf and legacy writable RPC payloads.

## Risks And Test Signals

Risks include off-by-one buffer consumption, incorrectly handling delimited protobuf messages, parent/child buffer aliasing, and leaving unread bytes. Test signals are object equality, positive remaining-byte assertions between sequential reads, and final `remaining()==0` checks on both parent and nested buffers.
