# sources/distributed-fs/ceph-client/mm/dmapool.c

## Purpose
`dmapool.c` implements the kernel DMA pool allocator for small coherent DMA objects. It allocates coherent DMA pages with `dma_alloc_coherent()`, splits each page into fixed-size aligned blocks, and hands those blocks to device drivers that need many small DMA-safe descriptors or control structures. It also exposes per-device pool diagnostics through a `pools` sysfs attribute and provides devres-managed wrappers.

## Important APIs, types, and functions
The core internal types are `struct dma_pool`, `struct dma_page`, and `struct dma_block`. `struct dma_pool` owns the per-pool block size, allocation size, boundary limit, NUMA node, free-block head, page list, active/block/page counters, device pointer, spinlock, and registration list node under `dev->dma_pools`. `struct dma_page` records each coherent allocation's CPU virtual address and DMA address. Free blocks are stored in-band as `struct dma_block` nodes.

The exported API is `dma_pool_create_node()`, `dma_pool_destroy()`, `dma_pool_alloc()`, `dma_pool_free()`, `dmam_pool_create()`, and `dmam_pool_destroy()`. `dma_pool_create_node()` validates power-of-two alignment and boundary constraints, rounds object size, allocates the pool, links it into `dev->dma_pools`, and creates `dev_attr_pools` when the first pool appears. `dma_pool_alloc()` pops an available block or temporarily drops the pool spinlock to allocate and initialize a new DMA page. `dma_pool_free()` validates and pushes a block back. The managed wrappers allocate a devres slot and destroy the pool on device teardown.

## Control flow
Pool creation normalizes input first: zero alignment becomes one, non-power-of-two alignment or boundary is rejected, tiny objects are raised to `sizeof(struct dma_block)`, and each object is aligned. The page allocation size is at least `PAGE_SIZE`, and the usable boundary is clamped to the allocation size. Registration is serialized by `pools_reg_lock` and list mutation by `pools_lock` so sysfs file creation/removal cannot race with the first or last pool on a device.

Allocation enters `pool->lock`, pops `pool->next_block`, and increments `nr_active`. If the free list is empty it drops the spinlock, allocates a `struct dma_page` and coherent DMA memory, reacquires the spinlock, calls `pool_initialise_page()`, and then pops a block. `pool_initialise_page()` walks offsets through the coherent page, skips offsets whose object would cross the configured boundary, chains valid blocks, appends the chain to the global free list, links the page to `page_list`, and updates counters. Freeing runs `pool_block_err()` first, then stores the DMA address in the block, links it at the free-list head, and decrements `nr_active`.

## State and persistence
State is entirely in kernel memory and device lifetime structures. Pool pages persist until `dma_pool_destroy()` or devres release. `nr_blocks`, `nr_active`, and `nr_pages` are maintained for diagnostics and leak detection. `dma_pool_destroy()` removes the pool from the device list and removes the `pools` sysfs file when the device has no pools left. If `nr_active` is nonzero, it logs the pool as busy and deliberately avoids freeing coherent pages to avoid releasing DMA memory still in use.

With `CONFIG_SLUB_DEBUG_ON`, `DMAPOOL_DEBUG` poisons freed and allocated blocks, checks for corruption, verifies the DMA address belongs to a pool page, and detects double-free by scanning the free list. Without debug, free optionally zeroes blocks when `init_on_free` is enabled; allocation optionally zeroes blocks when requested by allocation policy.

## Dependencies and integration points
This file integrates with the DMA mapping API (`dma_alloc_coherent()`, `dma_free_coherent()`), the device model (`struct device`, sysfs attributes, `devres`), NUMA slab allocation, list/spinlock/mutex primitives, memory initialization hardening hooks (`want_init_on_alloc/free()`), poison constants, and exported symbols consumed by device drivers. It relies on `dev->dma_pools` being initialized by device core code.

## Risks and test signals
Important risks are boundary arithmetic, stale DMA/virtual address pairs on free, double-free, and incorrect lifetime handling when a driver destroys a busy pool. The allocator stores free-list metadata inside freed DMA objects, so use-after-free by a device or driver can corrupt allocator state. The page initialization path assumes at least one valid block fits after validation. Registration must keep sysfs creation and removal balanced across concurrent create/destroy calls.

Useful test signals include `dmapool_test.c`, driver probe/remove cycles using `dmam_pool_create()`, sysfs `poolinfo` counter sanity, SLUB debug poison reports, DMA API debug warnings, boundary-sensitive devices, and tests that destroy pools only after all active blocks are returned.
