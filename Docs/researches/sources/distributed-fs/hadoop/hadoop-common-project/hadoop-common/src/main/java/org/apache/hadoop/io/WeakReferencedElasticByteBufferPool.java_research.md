# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WeakReferencedElasticByteBufferPool.java

## Purpose

`WeakReferencedElasticByteBufferPool.java` is a thread-safe `ElasticByteBufferPool` variant that stores pooled heap and direct `ByteBuffer` instances through `WeakReference`s. It lets the JVM reclaim buffers that are no longer strongly referenced while still reusing live buffers by nearest sufficient capacity.

## Important APIs, types, and functions

- The class extends `ElasticByteBufferPool`.
- `directBuffers` and `heapBuffers` are `TreeMap<Key, WeakReference<ByteBuffer>>` pools keyed by capacity and insertion time.
- `getBuffer(boolean direct, int length)` removes cleared weak references, finds the smallest buffer with capacity at least `length`, removes it from the pool, and returns it or allocates a new buffer.
- `putBuffer(ByteBuffer buffer)` clears the buffer and inserts it with a unique `(capacity, System.nanoTime())` key.
- `release()` clears both pools.
- `getCurrentBuffersCount(boolean isDirect)` is visible for tests.

## Control flow

All public methods are synchronized. `getBuffer()` chooses the direct or heap tree, prunes entries whose weak reference has been cleared, looks up `ceilingEntry(new Key(length, 0))`, removes that entry if present, and returns the referent when still live. If no entry or no referent remains, it allocates a new direct or heap buffer. `putBuffer()` clears the returned buffer and loops until it finds a unique nanosecond key before inserting a weak reference.

## State and persistence behavior

State is in-memory only and may shrink asynchronously when the garbage collector clears weak references. Direct and heap buffers are tracked separately. Returned buffers are cleared before pooling, so position and limit reset to capacity. The pool does not persist data and does not guarantee that a returned buffer remains available for later reuse.

## Dependencies and integration points

The class depends on `ElasticByteBufferPool` and its `Key` ordering, Java `ByteBuffer`, `WeakReference`, `TreeMap`, and Hadoop annotations. It integrates where Hadoop code wants elastic buffer reuse without retaining direct-buffer memory strongly.

## Risks and edge cases

- Each `getBuffer()` prunes the whole tree with `removeIf`, which can be O(n) under large pools.
- Weak references make reuse nondeterministic and GC-sensitive; performance tests should not assume stable hit rates.
- `putBuffer(null)` would fail; callers must only return real buffers.
- If system clock/nanotime granularity is poor, `putBuffer()` can loop, though the code expects this to be rare.
- `release()` only removes pool references; callers holding buffers keep them alive.

## Test signals

Tests should verify direct/heap separation, nearest-greater capacity selection, buffer clearing on return, pool count visibility, `release()`, GC-cleared weak reference pruning, and multi-threaded get/put safety.
