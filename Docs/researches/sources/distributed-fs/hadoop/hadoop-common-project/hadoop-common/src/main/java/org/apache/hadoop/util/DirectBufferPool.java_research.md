# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DirectBufferPool.java

Purpose: `DirectBufferPool` reuses direct `ByteBuffer`s by exact capacity to reduce native-memory churn.

Important APIs and types: `getBuffer(int)` obtains a direct buffer, `returnBuffer(ByteBuffer)` clears and stores it, and testing `countBuffersOfSize(int)` reports queue length.

Control flow: buffers are grouped by capacity in a concurrent map. `getBuffer` polls weak references until it finds a live buffer or allocates a new direct buffer. `returnBuffer` clears the buffer, creates or reuses the capacity queue, and enqueues a weak reference.

State and persistence behavior: in-memory concurrent map from size to queues of weak references. Weak values allow GC to reclaim returned direct buffers.

Dependencies and integration points: used by HDFS/MapReduce IO code that repeatedly allocates same-sized direct buffers.

Risks: pooling is exact-size only; larger buffers are never reused for smaller requests. Queues may accumulate cleared weak references until polled. Returning a heap buffer is not rejected and could later return a non-direct buffer despite class purpose.

Test signals: cover allocate/reuse same size, distinct sizes, returned buffer clear state, weak-reference cleanup, concurrent put/get, count accessor, and behavior with heap buffers if callers misuse it.
