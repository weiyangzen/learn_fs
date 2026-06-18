<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/BufferAllocator.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/BufferAllocator.java

Purpose: Test utility abstraction for allocating direct or heap `ByteBuffer`s for erasure-code tests, with simple and sliced allocation strategies.

Important APIs/types/functions: abstract `BufferAllocator` stores `usingDirect` and exposes protected `isUsingDirect()` plus abstract `allocate(int bufferLen)`. `SimpleBufferAllocator` allocates a fresh heap or direct buffer each time. `SlicedBufferAllocator` owns one large `overallBuffer` and returns slices until capacity is exhausted, then falls back to fresh allocation.

Control flow: simple allocator delegates directly to `ByteBuffer.allocateDirect` or `ByteBuffer.allocate`. Sliced allocator checks remaining capacity as `overallBuffer.capacity() - overallBuffer.position()`, sets limit to `position + bufferLen`, creates a slice, advances position, and returns the slice. If insufficient capacity remains, it allocates a new independent buffer of requested type.

State and persistence behavior: `SlicedBufferAllocator` persists cursor state in `overallBuffer.position()` and mutates its limit during allocation. No external persistence.

Dependencies and integration points: used by erasure-code tests that need controlled direct/heap buffers and sometimes contiguous sliced views to exercise raw coder behavior.

Risks and edge cases: after setting `overallBuffer.limit(position + bufferLen)`, the allocator does not restore the limit to capacity. The next available-space check uses capacity, but setting position beyond current limit can be sensitive unless previous operations permit it; current pattern advances to the limit each time. The class is not thread-safe.

Test signals: provides deterministic direct/heap allocation and fallback behavior for higher-level erasure coder tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/BufferAllocator.java -->
