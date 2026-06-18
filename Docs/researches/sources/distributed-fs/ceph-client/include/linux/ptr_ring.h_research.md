# sources/distributed-fs/ceph-client/include/linux/ptr_ring.h

Purpose: implements an inline fixed-size FIFO ring of pointers optimized for one producer CPU and one consumer CPU, with lock variants for normal, IRQ, IRQ-save, and BH contexts plus resize/unconsume helpers.

Important APIs and types: `struct ptr_ring` stores producer index/lock, consumer head/tail/lock, size, batch threshold, and pointer queue. APIs include full/empty tests, `__ptr_ring_produce()` and locked produce variants, peek/consume/discard/batched consume variants, peek-call macros, queue allocation/init, `ptr_ring_unconsume()`, resize helpers, multi-ring BH resize, and cleanup with optional destroy callback.

Control flow: producer acquires producer lock, checks current producer slot for fullness, executes `smp_wmb()`, writes the pointer, and advances/wraps. Consumer acquires consumer lock, reads the head with `READ_ONCE()`, processes dependency-ordered pointer data, batches slot zeroing through consumer tail to reduce cache contention, and advances head. Resize nests producer lock inside consumer lock, drains old queue into a new queue, destroys overflow entries, swaps queues, and frees old memory.

State and persistence: all queue state is in memory. Entries remain owned by callers until consumed or destroyed. `consumer_tail` defers invalidation, so occupied slots can lag logical consumption for batching.

Dependencies and integration points: depends on spinlocks, cacheline alignment, memory barriers, kvmalloc/kvfree, allocation hooks, and caller-provided pointer lifetime rules. It is used by high-throughput producer/consumer paths such as networking and virtio-like queues.

Risks and test signals: risks include wrong lock nesting during resize, using lockless empty/full checks while resizing, missing compiler barriers in polling loops, producer writing invalid pointers before `smp_wmb()`, destroy callback omissions, and interrupt/BH context mismatches. Test SPSC produce/consume order, full/empty transitions, batched consume wraparound, unconsume overflow destruction, resize under load, KCSAN/lockdep, and IRQ/BH variants.
