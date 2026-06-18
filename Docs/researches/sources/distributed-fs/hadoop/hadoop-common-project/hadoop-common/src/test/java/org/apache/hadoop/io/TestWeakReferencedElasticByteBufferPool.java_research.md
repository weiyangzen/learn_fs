<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWeakReferencedElasticByteBufferPool.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWeakReferencedElasticByteBufferPool.java

Purpose: Parameterized JUnit coverage for `WeakReferencedElasticByteBufferPool`, validating direct and heap `ByteBuffer` pooling, capacity selection, insertion ordering, weak-reference pruning, and release behavior.

Important APIs/types/functions: `params()` returns `"direct"` and `"array"` modes. `initTestWeakReferencedElasticByteBufferPool` maps mode to `isDirect`. Tests call `getBuffer(boolean direct, int len)`, `putBuffer(ByteBuffer)`, `getCurrentBuffersCount(boolean)`, and `release()`. Helpers `createByteArray` and `validateBufferContent` fill and verify buffers.

Control flow: each parameterized test initializes a new pool and requests buffers of different capacities. The basic test writes random bytes into a buffer, flips it, reads bytes back, then returns the buffer and asserts `position()` resets to zero. Size-order tests return buffers to the pool and request smaller sizes to ensure the pool chooses the smallest suitable greater-or-equal capacity. Insertion-time tests request equal-size buffers and assert identity ordering with AssertJ `isSameAs`. GC tests null strong references, call `System.gc()`, then assert weakly referenced buffers are pruned or skipped.

State and persistence behavior: pool state is process-local. The test observes the pool's internal counts through public test-support API `getCurrentBuffersCount`. Weak references mean GC timing affects expected behavior; tests try to remove strong refs before collection.

Dependencies and integration points: depends on Java NIO `ByteBuffer`, AssertJ assertions, JUnit parameterization, and `HadoopTestBase`. It integrates directly with Hadoop's byte-buffer pool used by I/O paths that recycle direct or array-backed buffers.

Risks and edge cases: GC-sensitive assertions can be timing-sensitive on unusual JVMs. The local variable `buffer1`/`buffer2` nulling relies on the JIT not preserving hidden strong references. Tests do not cover mixed direct and array pools in the same method beyond parameterization.

Test signals: verifies initial type/capacity/position, count changes after `putBuffer` and `getBuffer`, FIFO ordering among equal capacities, clearing through `release`, and behavior after weak-reference collection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWeakReferencedElasticByteBufferPool.java -->
