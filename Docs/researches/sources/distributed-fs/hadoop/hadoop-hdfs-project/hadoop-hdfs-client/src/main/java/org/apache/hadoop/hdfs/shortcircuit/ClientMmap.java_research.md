# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/shortcircuit/ClientMmap.java

Purpose: `ClientMmap` is a closeable client reference to a memory-mapped short-circuit replica region.

Important APIs/types/functions: constructor stores the owning `ShortCircuitReplica`, `MappedByteBuffer`, and whether the mmap added a no-checksum anchor. `getMappedByteBuffer()` returns the mapped buffer. `close()` removes the no-checksum anchor if anchored, unreferences the replica, and nulls the replica field to make close idempotent.

Control flow: callers obtain it from `ShortCircuitReplica.getOrCreateClientMmap()`. Closing releases cache/reference-count resources and may allow eviction.

State and persistence behavior: holds an in-memory mapped buffer and a mutable replica reference used to prevent double release. It does not unmap directly; unmapping is controlled by `ShortCircuitCache`/`ShortCircuitReplica`.

Dependencies and integration points: depends on `ShortCircuitReplica` and Java NIO `MappedByteBuffer`. It integrates with block reader mmap access and no-checksum anchoring.

Risks and test signals: failure to close leaks replica references and anchors, preventing slot release/munmap. Tests should cover anchored and unanchored close, double close, and reference-count effects in the cache.
