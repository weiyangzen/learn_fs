# sources/distributed-fs/ceph-client/kernel/dma/pool.c

## Purpose

`pool.c` implements atomic coherent DMA pools used when callers need DMA-coherent memory from contexts that cannot sleep or cannot perform the normal allocation/remap path. It creates separate genalloc pools for DMA, DMA32, and kernel-addressable zones, supports an early `coherent_pool=` boot parameter, exposes pool sizes via debugfs, and grows pools asynchronously when they become low.

## Important APIs, Types, And Functions

- Global pools: `atomic_pool_dma`, `atomic_pool_dma32`, and `atomic_pool_kernel`, with size counters `pool_size_dma`, `pool_size_dma32`, and `pool_size_kernel`.
- `early_coherent_pool()` parses the `coherent_pool` early boot parameter into `atomic_pool_size`.
- `dma_atomic_pool_debugfs_init()` creates `/sys/kernel/debug/dma_pools` size files.
- `cma_in_zone()` checks whether the default CMA area is usable for a requested DMA zone.
- `atomic_pool_expand()` allocates pages, prepares them coherent, optionally remaps them with `dma_common_contiguous_remap()`, decrypts memory, and adds the range to a `gen_pool`.
- `atomic_pool_resize()` and `atomic_pool_work_fn()` grow pools in background work when free space falls below the configured initial pool size.
- `dma_atomic_pool_init()` sizes and initializes pools at `postcore_initcall`.
- `dma_guess_pool()` orders fallback pool selection based on GFP zone flags.
- `dma_alloc_from_pool()` allocates zeroed memory from the best available pool and returns the backing page plus CPU address.
- `dma_free_from_pool()` finds the owning gen_pool and frees the address range.

## Control Flow

At boot, `dma_atomic_pool_init()` computes a default pool size of 128 KiB per GiB of RAM, bounded by a 128 KiB minimum and `MAX_ORDER_NR_PAGES`, unless `coherent_pool=` provided an override. It initializes workqueue state, creates a kernel pool if normal memory exists, then optional DMA and DMA32 pools when their managed zones exist. Each pool is a `gen_pool` configured for first-fit order alignment and seeded by `atomic_pool_expand()`.

Expansion chooses the largest feasible order no larger than `MAX_PAGE_ORDER`, preferring CMA if the CMA area belongs to the requested zone, then falling back to `alloc_pages()`. It prepares coherent memory, remaps for `CONFIG_DMA_DIRECT_REMAP`, decrypts pages because DMA pools must be unencrypted, and adds the virtual-to-physical range to the gen_pool. Error paths re-encrypt when possible, remove remaps, and free pages; if re-encryption fails after successful decryption, the code intentionally leaks the pages rather than returning insecure memory to the allocator.

Allocation tries pools in a zone-sensitive fallback order from `dma_guess_pool()`. `__dma_alloc_from_pool()` allocates from gen_pool, validates the physical address through the caller-supplied `phys_addr_ok` callback, schedules background growth if available space drops below the baseline size, zeroes the CPU address, and returns the page. Freeing scans possible pools and releases the range if it belongs to one.

## State And Persistence Behavior

The pools are long-lived kernel runtime state initialized after core boot and not designed to shrink. Pool pages remain decrypted for the lifetime of the pools. Debugfs size counters persist while the kernel runs. Dynamic expansion is asynchronous through `atomic_pool_work`; allocations can schedule this work when pool availability drops.

## Dependencies And Integration Points

The implementation depends on CMA, genalloc, debugfs, DMA direct remapping, set_memory encryption/decryption, coherent preparation hooks, workqueues, zone management, and the generic DMA pool APIs declared in `dma-map-ops.h`. SWIOTLB dynamic allocation also uses `dma_alloc_from_pool()` for atomic encrypted-memory cases.

## Risks And Edge Cases

- Pool sizing affects atomic DMA reliability; too-small pools trigger allocation failures and warnings.
- Decryption/re-encryption failures are security-sensitive. The intentional leak path avoids returning memory with uncertain encryption state.
- `atomic_pool_expand()` does not shrink pools, so repeated low-water growth can permanently consume memory.
- Zone fallback order must preserve device addressing constraints; using a wider pool for a narrow device is gated by `phys_addr_ok`.
- Remapped coherent memory cannot be used in contexts that sleep incorrectly, and expansion itself may sleep, which is why allocation from existing pools is separated from background growth.

## Test Signals

Check boot logs for preallocated pool messages, debugfs pool size files, atomic DMA allocation under `GFP_ATOMIC`, exhaustion warnings, background expansion behavior, CMA-zone selection, encrypted-memory systems, `CONFIG_DMA_DIRECT_REMAP` mappings, and free-path recognition through `dma_free_from_pool()`.
