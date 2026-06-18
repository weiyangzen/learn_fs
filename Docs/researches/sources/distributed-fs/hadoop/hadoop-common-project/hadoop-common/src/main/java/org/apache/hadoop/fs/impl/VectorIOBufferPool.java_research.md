# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/VectorIOBufferPool.java

## Purpose
Function-backed ByteBufferPool adapter for vectored IO allocation and release callbacks.

## Important APIs, Types, and Functions
Constructor takes IntFunction<ByteBuffer> allocate and Consumer<ByteBuffer> release; getBuffer(); putBuffer().

## Control Flow
getBuffer ignores the direct flag and calls allocate(length). putBuffer ignores null and otherwise calls release.

## State and Persistence Behavior
Stores two function references. No persistence.

## Dependencies and Integration Points
Used to adapt FileRange allocation/release callbacks into APIs expecting ByteBufferPool.

## Risks and Test Signals
Risks are direct flag being ignored and release callback behavior for reused buffers. Tests should verify null release, callback invocation, and length forwarding.
