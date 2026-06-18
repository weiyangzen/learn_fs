# File Research: sources/block-storage/kvdo/vdo/memory-alloc.c

## Purpose
Implements UDS/VDO memory allocation wrappers, allocation-thread tracking, kmalloc/vmalloc selection, memory usage accounting, and leak reporting.

## Behavior
- Tracks threads allowed to allocate freely through `allocating_threads`.
- Uses `memalloc_noio_save()` for allocation contexts not registered as allocation-allowed.
- Chooses `kmalloc` for allocations up to `PAGE_SIZE` when alignment is below a page; uses `__vmalloc` otherwise.
- Zeroes allocated memory via GFP flags.
- Retries briefly on allocation failure to let reclaim make progress.
- Tracks actual allocated size using `ksize()` for kmalloc and `PAGE_ALIGN(size)` for vmalloc.

## Key Functions
- `uds_allocate_memory`: main checked allocator with error logging and accounting.
- `uds_allocate_memory_nowait`: GFP_NOWAIT zeroed kmalloc path.
- `uds_free_memory`: dispatches to `vfree` or `kfree` and decrements stats.
- `uds_reallocate_memory`: allocate-copy-free realloc wrapper.
- `uds_duplicate_string`: checked string duplication.
- `uds_memory_init` / `uds_memory_exit`: initialize registry/stats and report leaks.
- `get_uds_memory_stats` / `report_uds_memory_usage`: expose current and peak tracked memory.

## Integration Notes
Used broadly through macros in `memory-alloc.h`. Vmalloc accounting uses a linked list of `vmalloc_block_info`, allocated through the same wrapper, so recursive accounting is intentional.

## Risks / Edge Cases
- Vmalloc tracking removal is O(number of vmalloc blocks), acceptable per file comments but relevant for heavy vmalloc churn.
- `uds_reallocate_memory` relies on caller-provided `old_size`; an incorrect old size can truncate or over-copy relative to the original allocation’s logical size.
