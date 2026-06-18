<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ElasticByteBufferPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ElasticByteBufferPool.java

Purpose: simple unbounded heap/direct `ByteBufferPool` that allocates on demand and caches returned buffers by capacity.

Important APIs, types, and functions: nested `Key` orders buffers by capacity and insertion time. `getBuffer(direct,length)` finds the smallest cached buffer with capacity at least length or allocates a new heap/direct buffer. `putBuffer()` clears and inserts by `(capacity, System.nanoTime())`, retrying on duplicate keys. `size(boolean direct)` reports cached buffer count.

Control flow: all pool operations are synchronized. Returned buffers are cleared before use; inserted buffers are cleared before caching.

State and persistence: two `TreeMap<Key, ByteBuffer>` instances store heap and direct buffers. No persistence and no default maximum cache size.

Dependencies and integration points: implements `ByteBufferPool`; used by Hadoop IO paths that want simple buffer reuse.

Risks and test signals: because the cache is unbounded, workloads returning many large buffers can retain memory/direct memory. Tests should cover smallest-sufficient reuse, direct/heap separation, clear semantics, size reporting, duplicate timestamp retry, and memory retention behavior under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ElasticByteBufferPool.java -->
