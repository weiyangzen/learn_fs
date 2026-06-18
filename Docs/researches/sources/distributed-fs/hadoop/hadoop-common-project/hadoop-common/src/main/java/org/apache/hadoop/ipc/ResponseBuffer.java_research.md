# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ResponseBuffer.java

## Purpose
`ResponseBuffer` is a byte-length-framed `DataOutputStream` used to encode RPC responses with a four-byte length prefix.

## Important APIs, Types, and Functions
Constructors allocate a `FramedBuffer`. `writeTo`, `toByteArray`, `capacity`, `setCapacity`, `ensureCapacity`, and `reset` manage the buffer. `FramedBuffer` reserves four framing bytes, overrides `size`, writes big-endian length in `setSize`, and resets count to the frame offset.

## Control Flow
Writers append response payload through `DataOutputStream`. Before extraction, `getFramedBuffer` updates the first four bytes from `written`. `ensureCapacity` grows the backing array for protobuf serialization.

## State and Persistence Behavior
State is a reusable in-memory byte array plus `written` count. It does not persist data.

## Dependencies and Integration Points
It is used by `RpcWritable.writeTo`, protobuf wrappers, server responder code, and tests such as `TestResponseBuffer` and `TestIPCServerResponder`.

## Risks and Test Signals
Risks include incorrect frame length after reset/reuse, capacity shrink/expand bugs, and mismatch between `written` and buffer count. Tests should verify framing bytes, reset behavior, capacity changes, and response writes of varied sizes.
