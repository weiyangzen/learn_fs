# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/network/protocol/databuffer/ByteArrayDataBuffer.java

## Purpose
`ByteArrayDataBuffer` is a test-only `DataBuffer` implementation backed by a byte array. It gives tests a simple buffer source that can expose Netty and read-only `ByteBuffer` views.

## Important APIs, Types, and Functions
The constructor stores array, offset, and length. `getNettyOutput()` returns an unpooled wrapped `ByteBuf`; `getLength()` returns length; `getReadOnlyByteBuffer()` returns a read-only view. Byte-copy and stream-read methods are intentionally unsupported. `release()` is a no-op.

## Control Flow, State, and Persistence
The buffer is immutable with respect to offset/length but references the original byte array. It has no persistence and relies on GC for cleanup.

## Dependencies and Integration Points
It implements `DataBuffer` for test code and depends on Guava preconditions and Netty `Unpooled`.

## Risks and Test Signals
Because many `DataBuffer` methods throw `UnsupportedOperationException`, it is only suitable for code paths using Netty output or read-only buffer. Tests using write handlers that call `readBytes()` must use a fuller buffer implementation.
