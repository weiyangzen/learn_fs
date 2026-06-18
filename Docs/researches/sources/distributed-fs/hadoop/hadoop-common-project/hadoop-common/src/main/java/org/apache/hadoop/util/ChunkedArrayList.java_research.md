# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ChunkedArrayList.java

Purpose: `ChunkedArrayList<T>` is a memory-fragmentation-friendly list for large append-heavy collections, storing elements across multiple growing chunks rather than one contiguous array.

Important APIs and types: constructors configure initial and maximum chunk size. Implemented operations include `add`, `get`, `iterator`, `clear`, `isEmpty`, `size`, and testing accessors `getNumChunks`/`getMaxChunkSize`.

Control flow: first add allocates the initial chunk. When the current chunk reaches capacity, a new chunk is allocated at 1.5x previous capacity capped by `maxChunkSize`. Iteration concatenates chunk iterators and decrements total size on iterator removal. `get` scans chunks linearly until the index falls inside one.

State and persistence behavior: in-memory chunks, cached last chunk/capacity, and total size. `clear` drops all chunk references.

Dependencies and integration points: uses Hadoop shaded/third-party Guava-style `Lists`/`Iterables` helpers and `Preconditions`. Intended for internal Hadoop large-list workloads.

Risks: random access is O(number of chunks). Only a subset of `List` operations is efficient/supported. Iterator removal updates size but may leave `lastChunk` capacity assumptions if removing from the last chunk through concatenated iterator.

Test signals: cover chunk growth, max chunk cap, `Integer.MAX_VALUE` guard, iteration order, iterator remove size accounting, clear reset, negative/out-of-range get, and constructor validation.
