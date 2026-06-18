# sources/distributed-fs/ceph-client/include/linux/highmem.h

## Purpose
`highmem.h` is the public helper layer for accessing pages and folios that may not have a permanent kernel virtual address. It documents and wraps long-term `kmap()`, temporary `kmap_local_page()`/`kmap_local_folio()`, deprecated `kmap_atomic()`, user-page zero/copy helpers, machine-check tolerant copy helpers, and page/folio memcpy/memset utilities.

## Important APIs, Types, And Functions
Important APIs include `kmap()`, `kunmap()`, `kmap_to_page()`, `kmap_flush_unused()`, `kmap_local_page()`, `kmap_local_folio()`, `kmap_atomic()`, highpage counters, `clear_user_page()`, `clear_user_pages()`, `clear_user_highpage()`, `clear_user_highpages()`, `vma_alloc_zeroed_movable_folio()`, `clear_highpage()`, `zero_user_segments()`, `copy_user_highpage()`, `copy_highpage()`, `copy_mc_user_highpage()`, `copy_mc_highpage()`, `memcpy_page()`, `memcpy_folio()`, `memset_page()`, `memcpy_from_page()`, `memcpy_to_page()`, `memzero_page()`, `memcpy_from_folio()`, `memcpy_to_folio()`, `folio_zero_tail()`, `folio_fill_tail()`, `memcpy_from_file_folio()`, `folio_zero_segments()`, `folio_zero_segment()`, `folio_zero_range()`, and `folio_release_kmap()`.

## Control Flow And State
Callers map a page/folio, operate on the returned address, flush dcache when needed for user-visible or DMA-visible writes, and unmap in reverse nesting order. Large folio helpers split copies at page boundaries when only partial highmem mapping is possible. Machine-check variants queue memory failure on source page errors. Allocation helpers may clear pages only when the architecture requires explicit zeroing.

## Dependencies And Integration Points
It depends on memory management, uaccess, cacheflush, KMSAN, KASAN tags, hardirq context rules, `highmem-internal.h`, file/VMA folio allocation, and architecture copy/clear hooks. It is used by filesystems, page cache, block, networking, and memory-management code.

## Risks
Risks include using local mapping addresses outside the caller context, unmapping in the wrong order, missing dcache flushes after writes, copying beyond page/folio boundaries, mishandling large highmem folios, ignoring machine-check copy failures, and relying on `kmap_atomic()` preemption behavior in new code.

## Test Signals
Run highmem-enabled 32-bit tests, large folio page-cache tests, KMSAN/KASAN metadata checks, userfault and page-fault paths, copy_mc error injection, boundary offsets at page edges, and filesystem inline-data paths using `folio_fill_tail()`.
