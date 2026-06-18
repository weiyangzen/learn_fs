# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/TrackingByteBufferPool.java

## Purpose
Testing ByteBufferPool wrapper that tracks allocations/releases and throws on leaked or foreign buffers.

## Important APIs, Types, and Functions
wrap(); getBuffer(); putBuffer(); containsBuffer(); size(); close(); allocation/release/leak exception types; counters getters.

## Control Flow
getBuffer delegates allocation, records buffer identity in an IdentityHashMap with optional stack trace, and increments allocation count. putBuffer removes by identity, throws if absent, returns to delegate, clears buffer, and increments release count. close logs any unreleased buffers, clears references, and throws LeakedByteBufferException.

## State and Persistence Behavior
Stores live buffer identities, wrapped allocator, and counters. No persistence; close releases references for GC.

## Dependencies and Integration Points
Used in vector IO and buffer-pool tests. Depends on ByteBufferPool and SLF4J.

## Risks and Test Signals
Risks include unsynchronized containsBuffer/size/close against synchronized get/put, clearing after delegate release, and DEBUG stacktrace overhead. Tests should cover leak detection, double release, foreign buffer release, counters, and direct/heap buffers.
