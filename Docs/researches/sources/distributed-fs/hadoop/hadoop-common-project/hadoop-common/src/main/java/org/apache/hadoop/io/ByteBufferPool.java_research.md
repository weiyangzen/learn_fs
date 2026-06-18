<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ByteBufferPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ByteBufferPool.java

Purpose: public interface for pooling heap or direct `ByteBuffer` instances.

Important APIs, types, and functions: `getBuffer(boolean direct, int length)` returns a buffer with at least one byte and generally at least the requested length. `putBuffer(ByteBuffer)` returns a buffer to the pool. Default `release()` is a no-op hook for implementations that can clear resources.

Control flow: users borrow, use, and return buffers. Implementations choose whether to allocate or reuse.

State and persistence: no state in the interface.

Dependencies and integration points: used by Hadoop IO paths that want reusable direct buffers, with `ElasticByteBufferPool` as a simple implementation.

Risks and test signals: the Javadoc says direct in one sentence but the method supports both direct and heap buffers; callers must respect the `direct` flag. Tests for implementations should cover requested length, directness, clearing, reuse, and release semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ByteBufferPool.java -->
