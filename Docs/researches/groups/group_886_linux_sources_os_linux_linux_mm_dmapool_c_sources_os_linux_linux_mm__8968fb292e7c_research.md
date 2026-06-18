# Group Research: group_886_linux_sources_os_linux_linux_mm_dmapool_c_sources_os_linux_linux_mm__8968fb292e7c

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/dmapool.c -->
# File Research: sources/os/linux/linux/mm/dmapool.c

## Purpose

Implements the Linux generic DMA pool allocator for small coherent DMA objects. A `struct dma_pool` owns pages allocated via `dma_alloc_coherent()`, subdivides them into fixed-size blocks, and serves those blocks to drivers that need small, aligned, coherent DMA buffers.

## Core Data Structures

- `struct dma_pool`: pool metadata, including `page_list`, `next_block` free list, size/alignment-derived geometry, counters, device pointer, NUMA node, sysfs list node, and pool name.
- `struct dma_page`: per-coherent-allocation page header with virtual address and DMA address.
- `struct dma_block`: free-list node stored inside free blocks; records next block and DMA address.

## Main Behavior

- `dma_pool_create_node()` validates device, size, alignment, and boundary constraints, normalizes block size, chooses allocation size, allocates the pool, and registers it under `dev->dma_pools`.
- A per-device read-only sysfs attribute `pools` is created when the first pool is registered and removed when the last pool is destroyed.
- `pool_initialise_page()` splits a coherent allocation into valid blocks, honoring the configured boundary by skipping offsets that would cross it.
- `dma_pool_alloc()` pops a free block under `pool->lock`; if no block exists, it allocates a new coherent page outside the spinlock, initializes it, and retries.
- `dma_pool_free()` validates/debug-poisons the block, pushes it onto the free list, and decrements active allocation count.
- `dma_pool_destroy()` unregisters the pool, warns if still busy, frees all backing coherent pages only when no active blocks remain, and frees metadata.
- `dmam_pool_create()` / `dmam_pool_destroy()` wrap pool lifetime in devres-managed resources.

## Debug / Hardening Paths

When `DMAPOOL_DEBUG` is enabled through `CONFIG_SLUB_DEBUG_ON`:

- Freed blocks are filled with `POOL_POISON_FREED`.
- Allocation checks verify the freed poison pattern after the embedded `struct dma_block`.
- Free validates the DMA address belongs to a pool page and detects double free by scanning the free list.
- Allocated blocks can be filled with `POOL_POISON_ALLOCATED` unless init-on-alloc is requested.

Without debug, free still honors `init_on_free` by zeroing the block.

## Locking and Concurrency

- `pool->lock` protects the free list and allocation counters.
- `pools_lock` protects the per-device `dma_pools` list.
- `pools_reg_lock` serializes sysfs file creation/removal races across pool create/destroy.
- Page allocation is done outside `pool->lock` because coherent DMA allocation can sleep.

## Dependencies and Interfaces

Exports:

- `dma_pool_create_node`
- `dma_pool_destroy`
- `dma_pool_alloc`
- `dma_pool_free`
- `dmam_pool_create`
- `dmam_pool_destroy`

Consumes core DMA APIs, devres, sysfs device attributes, poisoning helpers, GFP init policy helpers, spinlocks, and device pool list infrastructure.

## Important Invariants

- Alignment must be a power of two; zero alignment becomes one.
- Block size is at least `sizeof(struct dma_block)` and aligned up to requested alignment.
- Boundary is either zero, a power of two, and at least block size; internally capped to allocation size.
- Free-list nodes are embedded in unused DMA blocks.
- Used blocks are not individually tracked; correctness depends on active count and debug validation.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/dmapool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/dmapool_test.c -->
# File Research: sources/os/linux/linux/mm/dmapool_test.c

## Purpose

A simple module-init timing and stress test for the DMA pool allocator in `dmapool.c`. It creates a synthetic device, creates pools with several size/alignment/boundary combinations, repeatedly allocates and frees many blocks, and prints elapsed time.

## Test Shape

- `NR_TESTS` is 100 iterations per parameter set.
- `pool_parms[]` covers block sizes 16, 64, 256, 1024, 4096, and a boundary-sensitive case `{ size = 68, align = 32, boundary = 4096 }`.
- `nr_blocks()` scales block count by page size and clamps it between 1024 and 8192.

## Main Functions

- `dmapool_test_alloc()` allocates `blocks` entries from the global `pool`, records virtual/DMA pairs, then frees all. On allocation failure it unwinds already allocated blocks.
- `dmapool_test_block()` allocates the pair array, creates one DMA pool, runs `NR_TESTS` allocate/free cycles, times with `ktime_get()`, logs microseconds, and destroys the pool.
- `dmapool_checks()` initializes and registers `test_dev`, sets a 64-bit coherent DMA mask, then runs all parameter tests.
- `dmapool_exit()` is empty; the test work runs during module init.

## Device Setup

The test uses a static `struct device test_dev` with:

- Name `dmapool-test`
- Empty release callback
- `set_dma_ops(&test_dev, NULL)`
- Static `dma_mask`
- `dma_set_mask_and_coherent(..., DMA_BIT_MASK(64))`

## Interfaces

Registered with:

- `module_init(dmapool_checks)`
- `module_exit(dmapool_exit)`

Metadata:

- `MODULE_DESCRIPTION("dma_pool timing test")`
- `MODULE_LICENSE("GPL")`

## Notes

This is not a KUnit-style assertion suite. It primarily checks allocator functionality under repeated create/alloc/free/destroy cycles and reports timing. Failures propagate as module init errors.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/dmapool_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/early_ioremap.c -->
# File Research: sources/os/linux/linux/mm/early_ioremap.c

## Purpose

Provides generic early boot temporary mapping helpers for architectures that need `early_ioremap()` / `early_memremap()` before normal `ioremap()` is available. The implementation is active for `CONFIG_MMU`; the non-MMU fallback returns direct physical-address casts.

## MMU Implementation

The file manages a fixed number of boot-time mapping slots using the fixmap area:

- `prev_map[FIX_BTMAPS_SLOTS]`: currently active mappings.
- `prev_size[FIX_BTMAPS_SLOTS]`: original requested sizes for unmap validation.
- `slot_virt[FIX_BTMAPS_SLOTS]`: virtual base for each fixmap slot.

`early_ioremap_setup()` initializes slot virtual addresses and warns if stale mappings exist.

## Main Mapping Flow

`__early_ioremap()`:

1. Finds a free slot.
2. Rejects zero size or address wraparound.
3. Saves original size.
4. Aligns physical address down and expands size to page boundaries.
5. Rejects requests requiring more than `NR_FIX_BTMAPS` pages.
6. Installs fixmap PTEs using `__early_set_fixmap()` before paging init reset, or `__late_set_fixmap()` after.
7. Stores and returns the virtual address plus original page offset.

`early_iounmap()`:

1. Finds the slot by returned address.
2. Verifies the supplied size matches the original request.
3. Computes aligned page count.
4. Clears fixmap entries with `__early_set_fixmap(..., FIXMAP_PAGE_CLEAR)` or `__late_clear_fixmap()`.
5. Marks the slot free.

## Public Helpers

- `early_ioremap()` maps I/O memory with `FIXMAP_PAGE_IO`.
- `early_memremap()` maps memory with `FIXMAP_PAGE_NORMAL`, after optional architecture adjustment.
- `early_memremap_ro()` maps read-only memory when `FIXMAP_PAGE_RO` exists.
- `early_memremap_prot()` maps with an explicit architecture pgprot value under `CONFIG_ARCH_USE_MEMREMAP_PROT`.
- `early_memunmap()` delegates to `early_iounmap()`.
- `copy_from_early_mem()` copies from physical memory in chunks that fit the early mapping slot capacity.

## Debug and Leak Detection

- Boot parameter `early_ioremap_debug` enables warnings with stack dumps for map/unmap activity.
- `check_early_ioremap_leak()` runs at `late_initcall` and warns if any slots remain mapped.

## Architecture Hooks

- Weak `early_memremap_pgprot_adjust()` lets architectures modify protections.
- Architectures may provide `__late_set_fixmap` / `__late_clear_fixmap`; otherwise default stubs `BUG()` after `early_ioremap_reset()` marks `after_paging_init`.

## Non-MMU Behavior

When `CONFIG_MMU` is disabled:

- `early_ioremap()` returns the physical address cast to `void __iomem *`.
- `early_memremap()` and `early_memremap_ro()` return direct `void *`.
- `early_iounmap()` is a no-op.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/early_ioremap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/execmem.c -->
# File Research: sources/os/linux/linux/mm/execmem.c

## Purpose

Implements the executable memory allocator used for kernel executable regions such as module text and related execmem types. It abstracts architecture-provided executable-memory ranges, fallback ranges, permissions, alignment, and optional read-only-execute cache behavior.

## Global Configuration

- `execmem_info`: selected allocator configuration, set during init.
- `default_execmem_info`: fallback setup using `VMALLOC_START..VMALLOC_END`, `PAGE_KERNEL_EXEC`, alignment 1.
- `execmem_arch_setup()` is weak and may be overridden by architectures.

`execmem_validate()` ensures the default range has alignment, start/end, and pgprot. It also strips unsupported `EXECMEM_ROX_CACHE` flags if the architecture lacks `CONFIG_ARCH_HAS_EXECMEM_ROX`.

`execmem_init_missing()` fills unspecified execmem ranges from `EXECMEM_DEFAULT`, except `EXECMEM_MODULE_DATA`, which receives `PAGE_KERNEL`.

## Allocation Without ROX Cache

Under `CONFIG_MMU`, `execmem_vmalloc()` allocates from the selected primary range using `__vmalloc_node_range()`, then retries the fallback range if configured. It adds KASAN shadow handling when `EXECMEM_KASAN_SHADOW` is set.

Without MMU, it falls back to `vmalloc()`.

`execmem_vmap()` reserves virtual memory for `EXECMEM_MODULE_DATA` using the configured range and fallback.

## ROX Cache Path

When `CONFIG_ARCH_HAS_EXECMEM_ROX` is enabled, the file provides an executable-memory cache that keeps memory mapped ROX and temporarily flips regions writable for updates.

Key structures:

- `struct execmem_cache`
  - `mutex`
  - `busy_areas` maple tree
  - `free_areas` maple tree
  - `pending_free_cnt`

Important constants:

- `FREE_DELAY`: delayed retry for slow frees.
- `PENDING_FREE_MASK`: marks busy-tree entries pending async free.

Main ROX cache behavior:

- `execmem_cache_populate_alloc()` allocates PMD-rounded memory when possible, fills it with trapping instructions, marks it ROX, adds it to the free tree, then allocates the requested range.
- `execmem_cache_alloc_locked()` finds a suitable free range in primary or fallback execmem range, moves the allocated part to `busy_areas`, and leaves any remainder in `free_areas`.
- `__execmem_cache_free()` forces memory RW/NX, fills trapping instructions, restores ROX, moves range back to free tree, and removes it from busy tree.
- `execmem_cache_free()` tries a non-retry GFP path under lock; on failure marks the entry pending and schedules delayed work.
- `execmem_cache_free_slow()` retries pending frees with `GFP_KERNEL`.
- `execmem_cache_clean()` eventually releases PMD-aligned free cached areas back to vmalloc and restores direct-map validity.

## Permissions

- `execmem_force_rw()` converts allocated executable memory to writable and NX.
- `execmem_restore_rox()` restores read-only executable permissions.
- `execmem_set_direct_map_valid()` toggles direct-map validity for vmalloc backing pages and rolls back on failure.

When ROX cache is not enabled, permission forcing is a no-op and the cache allocator/free path returns unused.

## Public Interfaces

- `execmem_alloc(type, size)`: page-aligns size and allocates from cache or vmalloc range.
- `execmem_alloc_rw(type, size)`: allocates, then forces writable permissions, returning NULL if permission change fails.
- `execmem_free(ptr)`: warns on interrupt context, frees through ROX cache if recognized, otherwise `vfree()`.
- `execmem_is_rox(type)`: reports whether the type uses ROX cache.
- `execmem_vmap(size)`: returns a `vm_struct` for module data range under MMU.

## Initialization

- If `CONFIG_ARCH_WANTS_EXECMEM_LATE`, initialization is registered with `core_initcall(execmem_late_init)`.
- Otherwise, `execmem_init()` directly initializes execmem configuration.

## Notable Invariants

- Requested allocation sizes are page-aligned.
- ROX cache free/alloc state is tracked with maple-tree address ranges.
- New executable cache memory is filled with trapping instructions before being exposed.
- `execmem_free()` must not be called from interrupt context because freeing RO memory via vmalloc is unsupported there.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/execmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/fadvise.c -->
# File Research: sources/os/linux/linux/mm/fadvise.c

## Purpose

Implements generic POSIX file access advice handling and the fadvise syscalls. It adjusts readahead behavior, marks no-reuse mode, triggers readahead for `WILLNEED`, and flushes/invalidates page cache for `DONTNEED`.

## Main Entry Points

- `generic_fadvise(file, offset, len, advice)`: default advice implementation.
- `vfs_fadvise(file, offset, len, advice)`: dispatches to `file->f_op->fadvise` if present, otherwise generic.
- `ksys_fadvise64_64(fd, offset, len, advice)`: fd-based kernel syscall helper.
- Syscall wrappers:
  - `fadvise64_64`
  - optional `fadvise64`
  - optional compat `fadvise64_64`

## Advice Handling

- `POSIX_FADV_NORMAL`: restores default readahead pages and clears `FMODE_RANDOM | FMODE_NOREUSE`.
- `POSIX_FADV_RANDOM`: sets `FMODE_RANDOM`.
- `POSIX_FADV_SEQUENTIAL`: doubles default readahead and clears random mode.
- `POSIX_FADV_WILLNEED`: computes page range and calls `force_page_cache_readahead()`.
- `POSIX_FADV_NOREUSE`: sets `FMODE_NOREUSE`.
- `POSIX_FADV_DONTNEED`: flushes dirty cache in range, then invalidates full pages only.

## Range Semantics

- Negative `offset` or `len` returns `-EINVAL`.
- `len == 0` means through end of file/address space.
- Overflow in `offset + len` is handled with unsigned math and maps to `LLONG_MAX`.
- `DONTNEED` preserves partial first and last pages to avoid discarding potentially useful data.

## DAX / Noop BDI Behavior

For DAX inodes or `noop_backing_dev_info`, recognized advice values are accepted but ignored. Unknown advice still returns `-EINVAL`.

## Cache Invalidation Details

For `POSIX_FADV_DONTNEED`:

1. `filemap_flush_range()` starts writeback for the requested range.
2. Full-page start/end page indexes are computed.
3. `lru_add_drain()` flushes local LRU additions before invalidation.
4. `mapping_try_invalidate()` attempts invalidation and reports failures.
5. If failures occur, `lru_add_drain_all()` drains remote CPUs and `invalidate_mapping_pages()` retries.

## Locking

Updates to `file->f_mode` are protected by `file->f_lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/fadvise.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/fail_page_alloc.c -->
# File Research: sources/os/linux/linux/mm/fail_page_alloc.c

## Purpose

Provides fault injection for page allocator failures. It lets tests or debug configurations simulate allocation failure based on configured fault attributes, GFP filters, and minimum allocation order.

## Configuration State

Static `fail_page_alloc` contains:

- `struct fault_attr attr`
- `ignore_gfp_highmem`, default true
- `ignore_gfp_reclaim`, default true
- `min_order`, default 1

Boot setup uses:

- `__setup("fail_page_alloc=", setup_fail_page_alloc)`

## Main Function

`should_fail_alloc_page(gfp_t gfp_mask, unsigned int order)` returns true when the current allocation should fail.

It refuses injection when:

- `order < min_order`
- `__GFP_NOFAIL` is set
- highmem allocations are ignored and `__GFP_HIGHMEM` is set
- reclaimable allocations are ignored and `__GFP_DIRECT_RECLAIM` is set

If `__GFP_NOWARN` is set, it passes `FAULT_NOWARN` to avoid noisy reporting and possible deadlock-prone logging.

The function is exposed to the error injection framework:

- `ALLOW_ERROR_INJECTION(should_fail_alloc_page, TRUE)`

## Debugfs Interface

Under `CONFIG_FAULT_INJECTION_DEBUG_FS`, `late_initcall(fail_page_alloc_debugfs)` creates:

- `fail_page_alloc/ignore-gfp-wait`
- `fail_page_alloc/ignore-gfp-highmem`
- `fail_page_alloc/min-order`

All are mode `0600`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/fail_page_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/failslab.c -->
# File Research: sources/os/linux/linux/mm/failslab.c

## Purpose

Provides fault injection for slab allocator failures. It supports global slab failure injection, optional reclaim-GFP filtering, and optional per-cache filtering through `SLAB_FAILSLAB`.

## Configuration State

Static `failslab` contains:

- `struct fault_attr attr`
- `ignore_gfp_reclaim`, default true
- `cache_filter`, default false

Boot setup uses:

- `__setup("failslab=", setup_failslab)`

## Main Function

`should_failslab(struct kmem_cache *s, gfp_t gfpflags)` returns `-ENOMEM` when injection says the allocation should fail, otherwise 0.

It refuses injection when:

- The cache is the bootstrap `kmem_cache`.
- `__GFP_NOFAIL` is set.
- reclaimable allocations are ignored and `__GFP_DIRECT_RECLAIM` is set.
- `cache_filter` is enabled and the cache lacks `SLAB_FAILSLAB`.

If `__GFP_NOWARN` is set, it passes `FAULT_NOWARN` to suppress warning output.

The function is registered with:

- `ALLOW_ERROR_INJECTION(should_failslab, ERRNO)`

## Debugfs Interface

Under `CONFIG_FAULT_INJECTION_DEBUG_FS`, `late_initcall(failslab_debugfs_init)` creates:

- `failslab/ignore-gfp-wait`
- `failslab/cache-filter`

The debugfs root is created via `fault_create_debugfs_attr("failslab", ...)`.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/failslab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/filemap.c -->
# File Research: sources/os/linux/linux/mm/filemap.c

## Purpose

This is the central generic Linux page-cache implementation for normal files. It handles page-cache insertion/removal, folio lookup, writeback coordination, read paths, splice reads, mmap faults and fault-around, direct/buffered write integration, folio lifecycle helpers, cache invalidation, and optional `cachestat(2)` support.

## Major Responsibilities

- Maintain `address_space->i_pages` xarray entries for cached folios, shadow entries, swap/shmem entries, and DAX-like value entries.
- Provide generic read and write operations used by many filesystems.
- Coordinate dirty/writeback state and error reporting.
- Implement folio wait queues and folio lock/writeback wakeups.
- Support large folios and PMD mapping where allowed.
- Protect truncate/hole-punch races using `mapping->invalidate_lock`.
- Provide mmap fault handling for file-backed VMAs.

## Page Cache Removal and Accounting

Key helpers:

- `page_cache_delete()`: removes one locked folio from the xarray, clears marks, detaches mapping, and subtracts `nrpages`.
- `filemap_unaccount_folio()`: verifies folio is unmapped, updates LRU/node/memcg stats, handles THP/shmem/kernel-file accounting, and cleans dirty accounting if necessary.
- `__filemap_remove_folio()`: trace + unaccount + delete.
- `filemap_remove_folio()`: public locked-folio removal with inode lock and xarray lock.
- `delete_from_page_cache_batch()`: batch removal optimized for sorted dense folio batches.
- `filemap_free_folio()`: calls filesystem `free_folio()` then drops page-cache references.

## Writeback and Error Handling

Important exported functions:

- `filemap_check_errors()`
- `filemap_fdatawrite_range()`
- `filemap_fdatawrite()`
- `filemap_flush_range()`
- `filemap_flush()`
- `filemap_flush_nr()`
- `filemap_fdatawait_range()`
- `filemap_fdatawait_range_keep_errors()`
- `file_fdatawait_range()`
- `filemap_write_and_wait_range()`
- `file_write_and_wait_range()`
- `file_check_and_advance_wb_err()`
- `__filemap_set_wb_err()`

The file uses `mapping->wb_err` / `file->f_wb_err` errseq tracking so writeback errors can be reported once per file descriptor, especially through fsync-like paths. Legacy `AS_EIO` and `AS_ENOSPC` bits are also checked and cleared or preserved depending on helper.

## Page Cache Insertion and Replacement

Key helpers:

- `replace_page_cache_folio()`: atomically replaces an old locked folio with a new locked folio in the page cache.
- `__filemap_add_folio()`: low-level insertion into xarray, handling conflicts, shadow entries, large-entry splitting, accounting, and reference setup.
- `filemap_add_folio()`: charges memcg, locks folio, inserts, handles workingset refault, adds to LRU, and kernel-file stats.
- NUMA-aware `filemap_alloc_folio_noprof()` supports mempolicy and cpuset memory spreading.

Important invariants:

- Inserted folios must be locked.
- Folio index must align to folio size.
- Folio order must satisfy mapping minimum order.
- Large xarray value conflicts may be split to fit smaller folios.
- Shadow entries can be returned to callers for workingset refault logic.

## Invalidation Lock Helpers

- `filemap_invalidate_lock_two()` and `filemap_invalidate_unlock_two()` lock two mappings in address order to avoid deadlock.
- Read and write paths use shared/exclusive invalidate locks to synchronize with truncate and hole punching.

## Folio Wait Queues and Locking

The file defines hashed wait queues:

- `folio_wait_table[256]`
- `folio_waitqueue(folio)`

`pagecache_init()` initializes wait queues, writeback, and sysctl `vm/page_lock_unfairness`.

Core wait/wakeup functions:

- `wake_page_function()`
- `folio_wake_bit()`
- `folio_wait_bit_common()`
- `folio_wait_bit()`
- `folio_wait_bit_killable()`
- `folio_unlock()`
- `folio_end_read()`
- `folio_end_writeback_no_dropbehind()`
- `folio_end_writeback()`
- `__folio_lock()`
- `__folio_lock_killable()`
- `__folio_lock_or_retry()`

The lock wait logic supports shared waits, exclusive waits, dropped-reference waits, and fair lock handoff after configurable unfairness. It also accounts thrashing stalls for non-uptodate workingset folios.

## Lookup and Batch Traversal

Core lookup:

- `filemap_get_entry()`: lockless RCU lookup with speculative folio refcounting.
- `__filemap_get_folio_mpol()`: lookup/create API with `FGP_*` flags, locking, accessed/stable handling, large folio allocation, and NOWAIT behavior.

Batch APIs:

- `find_get_entries()`
- `find_lock_entries()`
- `filemap_get_folios()`
- `filemap_get_folios_contig()`
- `filemap_get_folios_tag()`
- `filemap_get_folios_dirty()`

Gap APIs:

- `page_cache_next_miss()`
- `page_cache_prev_miss()`

These rely on xarray RCU traversal and carefully pin folios only after checking they remain in the xarray.

## Generic Buffered Read Path

Primary functions:

- `filemap_get_read_batch()`
- `filemap_read_folio()`
- `filemap_range_uptodate()`
- `filemap_update_page()`
- `filemap_create_folio()`
- `filemap_readahead()`
- `filemap_get_pages()`
- `filemap_read()`
- `generic_file_read_iter()`

Flow:

1. `generic_file_read_iter()` handles direct I/O first if `IOCB_DIRECT` is set.
2. Short direct reads may fall back to buffered reads unless DAX or complete/error.
3. `filemap_read()` gets batches of cached folios, drives readahead or synchronous `read_folio`, checks i_size after folios become uptodate, flushes dcache for writable mappings, and copies to the iterator.
4. `IOCB_NOWAIT`, `IOCB_NOIO`, `IOCB_WAITQ`, and `IOCB_DONTCACHE` alter blocking, I/O submission, async wait, and dropbehind behavior.

## Dropbehind / Uncached Reads and Writes

The file supports `FGP_DONTCACHE` and `IOCB_DONTCACHE` through folio `dropbehind` marking. Clean non-writeback dropbehind folios can be invalidated after reads or writeback completion. Dirty dropbehind accounting is adjusted when a non-uncached lookup clears the flag.

## Direct I/O and Buffered Write Integration

Key functions:

- `kiocb_write_and_wait()`
- `filemap_invalidate_pages()`
- `kiocb_invalidate_pages()`
- `kiocb_invalidate_post_direct_write()`
- `generic_file_direct_write()`
- `generic_perform_write()`
- `__generic_file_write_iter()`
- `generic_file_write_iter()`

Behavior:

- Direct writes first write back and invalidate overlapping cache unless NOWAIT requires `-EAGAIN`.
- After direct write, clean cached pages are invalidated again to reduce stale-cache risk.
- Failure to invalidate page cache after direct I/O logs a ratelimited critical warning and sets writeback error.
- Buffered writes loop over `write_begin` / copy / `write_end`, throttle dirty pages, handle short copies, shrink chunk size for large folios on zero progress, and fault in user pages outside filesystem locks for progress.
- `generic_file_write_iter()` wraps checks, inode locking, and sync-on-write handling.

## Splice and SEEK_HOLE / SEEK_DATA

Splice helpers:

- `splice_folio_into_pipe()`
- `filemap_splice_read()`

They move page-cache folio references into pipe buffers, using page-cache pipe buffer operations.

Seek helpers:

- `mapping_seek_hole_data()`
- `folio_seek_hole_data()`
- `seek_folio_size()`

The seek implementation can use `is_partially_uptodate()` to distinguish block-level holes/data inside non-uptodate folios.

## mmap Fault Handling

Under `CONFIG_MMU`, key functions:

- `filemap_fault()`
- `filemap_map_pages()`
- `filemap_page_mkwrite()`
- `generic_file_mmap()`
- `generic_file_mmap_prepare()`
- `generic_file_readonly_mmap()`
- `generic_file_readonly_mmap_prepare()`

Fault flow:

1. Rejects faults beyond i_size with `VM_FAULT_SIGBUS`.
2. Attempts page-cache lookup.
3. Existing folio may trigger async mmap readahead.
4. Missing folio triggers major fault accounting and sync mmap readahead.
5. Uses `invalidate_lock` before creating or reading folios to synchronize with truncate/hole punch.
6. Locks folio, potentially dropping mmap/per-VMA lock and returning `VM_FAULT_RETRY`.
7. Reads non-uptodate folios synchronously.
8. Rechecks i_size under folio lock.
9. Returns locked page via `vmf->page`.

Readahead helpers:

- `do_sync_mmap_readahead()`
- `do_async_mmap_readahead()`

They respect `VM_RAND_READ`, `VM_SEQ_READ`, `VM_EXEC`, THP/PMD folio constraints, and `ra->mmap_miss`.

Fault-around mapping:

- `filemap_map_pmd()` attempts PMD mapping of large folios.
- `next_uptodate_folio()` finds lockable uptodate folios.
- `filemap_map_folio_range()` maps ranges of large folios into PTEs.
- `filemap_map_order0_folio()` handles order-0 folios.
- `filemap_map_pages()` maps multiple cached folios around a fault and updates RSS counters.

Non-MMU builds return `-ENOSYS` for mmap helpers and `VM_FAULT_SIGBUS` for page_mkwrite.

## Read Cache Helpers

- `read_cache_folio()`
- `mapping_read_folio_gfp()`
- `read_cache_page()`
- `read_cache_page_gfp()`

These get or create a cache folio/page, invoke a filler or `read_folio`, wait for uptodate state, and return pinned folio/page. They expect `mapping->invalidate_lock` to be held.

## Folio Release and Inode Invalidation

- `filemap_release_folio()` releases filesystem-private folio metadata using `a_ops->release_folio()` or `try_to_free_buffers()`, but refuses writeback folios.
- `filemap_invalidate_inode()` optionally writes back, unmaps, invalidates page cache over a byte range, and checks writeback errors.

## cachestat Support

Under `CONFIG_CACHESTAT_SYSCALL`:

- `filemap_cachestat()` walks xarray entries and counts cached, dirty, writeback, evicted, and recently evicted pages.
- It handles shadow entries and shmem swap entries.
- `can_do_cachestat()` restricts cache-status visibility to writable/openable/owner-capable users.
- `SYSCALL_DEFINE4(cachestat, ...)` validates fd, user pointers, flags, hugetlb exclusion, permissions, and returns `struct cachestat`.

## Key External Dependencies

This file is deeply integrated with:

- xarray / maple-like page cache storage
- folios and large folios
- writeback and errseq
- readahead
- memcg and lruvec stats
- VFS inode/file operations
- direct I/O
- VM fault machinery
- swap/shmem and workingset tracking
- pipe/splice infrastructure
- sysctl and optional cachestat syscall

## High-Risk Areas

- Lock ordering is explicitly documented at the top and is essential: `i_rwsem`, `invalidate_lock`, `mmap_lock`, `i_mmap_rwsem`, page-table locks, `i_pages`, LRU locks, and writeback locks interact.
- Lockless xarray lookup relies on RCU plus speculative refcounting and reload checks.
- mmap fault retry paths must correctly manage dropped mmap locks and pinned files.
- Direct I/O invalidation failure is treated as possible data corruption.
- Large folio and PMD mapping paths must preserve SIGBUS semantics beyond i_size.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/filemap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/folio-compat.c -->
# File Research: sources/os/linux/linux/mm/folio-compat.c

## Purpose

Provides non-inline compatibility wrappers from legacy `struct page` APIs to folio-based implementations. The header comment states callers should eventually be converted to folios, but these functions avoid bloating callers with inline wrappers.

## Exported Compatibility Functions

- `unlock_page(page)` -> `folio_unlock(page_folio(page))`
- `end_page_writeback(page)` -> `folio_end_writeback(page_folio(page))`
- `wait_on_page_writeback(page)` -> `folio_wait_writeback(page_folio(page))`
- `mark_page_accessed(page)` -> `folio_mark_accessed(page_folio(page))`
- `set_page_writeback(page)` -> `folio_start_writeback(page_folio(page))`
- `set_page_dirty(page)` -> `folio_mark_dirty(page_folio(page))`
- `set_page_dirty_lock(page)` -> `folio_mark_dirty_lock(page_folio(page))`
- `clear_page_dirty_for_io(page)` -> `folio_clear_dirty_for_io(page_folio(page))`
- `redirty_page_for_writepage(wbc, page)` -> `folio_redirty_for_writepage(wbc, page_folio(page))`
- `add_to_page_cache_lru(page, mapping, index, gfp)` -> `filemap_add_folio(mapping, page_folio(page), index, gfp)`
- `pagecache_get_page(mapping, index, fgp_flags, gfp)` -> `__filemap_get_folio()` then `folio_file_page()`

## Role in Transition

This file is a shim for subsystems still using `struct page` while the page cache and memory-management internals move toward folio-native APIs. It preserves exported page-based symbols without duplicating logic.

## Error Semantics

`pagecache_get_page()` returns `NULL` when `__filemap_get_folio()` returns an error pointer, matching older page-cache helper behavior rather than propagating encoded errors.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/folio-compat.c -->