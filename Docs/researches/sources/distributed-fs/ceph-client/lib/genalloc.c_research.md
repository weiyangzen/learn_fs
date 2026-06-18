# sources/distributed-fs/ceph-client/lib/genalloc.c

## Purpose
`genalloc.c` implements the generic special-purpose memory pool allocator used for memory outside normal `kmalloc` management, such as device SRAM, uncached memory, or DMA-visible regions. Allocation/free are bitmap-based and designed to be lockless after chunks have been added.

## Important APIs, Types, and Functions
Core APIs include `gen_pool_create()`, `gen_pool_add_owner()`, `gen_pool_destroy()`, `gen_pool_alloc_algo_owner()`, `gen_pool_free_owner()`, `gen_pool_virt_to_phys()`, `gen_pool_avail()`, `gen_pool_size()`, `gen_pool_has_addr()`, and `gen_pool_for_each_chunk()`. DMA wrappers include `gen_pool_dma_alloc*()` and `gen_pool_dma_zalloc*()`. Allocation strategies include `gen_pool_first_fit()`, `gen_pool_first_fit_align()`, `gen_pool_fixed_alloc()`, `gen_pool_first_fit_order_align()`, and `gen_pool_best_fit()`. Device-managed integration is provided by `devm_gen_pool_create()`, `gen_pool_get()`, and `of_gen_pool_get()` under `CONFIG_OF`.

## Control Flow, State, and Persistence
A `struct gen_pool` owns an RCU-protected list of `struct gen_pool_chunk` objects. Each chunk stores virtual and physical base addresses, inclusive end address, owner pointer, an atomic available-byte count, and a bitmap where one bit represents `1 << min_alloc_order` bytes. Adding chunks takes `pool->lock`; allocation walks chunks under RCU, skips chunks with insufficient `avail`, asks the selected algorithm for a start bit, atomically sets bitmap bits with cmpxchg, retries on conflict, subtracts rounded size from `avail`, and returns a virtual address plus optional owner. Freeing finds the containing chunk, atomically clears the bits, restores `avail`, and BUGs on invalid ranges or double-free-like bitmap conflicts. Destroy asserts all bits are clear before freeing chunks and the optional name.

## Dependencies and Integration Points
The implementation depends on bitmap helpers, RCU lists, atomic operations, spinlocks, device resources, OF/platform-device lookup, and vmalloc-backed chunk metadata. It is exported for drivers and subsystems that publish special memory pools or consume pools through devres or device-tree phandles.

## Risks and Test Signals
Risks include livelock under heavy atomic contention, BUG-triggering invalid frees, address overflow in `virt + size - 1` or `start + size - 1`, alignment data requiring power-of-two semantics, NMI use on architectures without NMI-safe cmpxchg, and destroy-time BUGs if allocations remain. Tests should exercise concurrent allocation/free, all algorithms, alignment and fixed offsets, owner round trips, DMA physical translation, empty/full pools, devm lookup uniqueness, OF phandle lookup, and misuse cases under debug kernels.
