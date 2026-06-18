# File Research: sources/cow-pools/bcachefs-tools/include/linux/mempool.h

This header declares Linux mempool support. `mempool_t` stores a spinlock, minimum/current counts, element array, pool data, alloc/free callbacks, and wait queue.

It declares lifecycle, resize, allocate, free, and destroy operations, plus callback pairs for slab, kmalloc, and page-backed pools. Inline helpers build pool instances for common backends. `mempool_alloc()` wraps `mempool_alloc_noprof()` through a placeholder allocation-hook macro.
