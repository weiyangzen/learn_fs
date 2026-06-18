# sources/distributed-fs/ceph-client/include/linux/highmem-internal.h

## Purpose
`highmem-internal.h` provides the internal architecture/configuration split for highmem and local kmap APIs. It implements or declares the low-level behavior behind public highmem helpers, handling `CONFIG_HIGHMEM`, `CONFIG_KMAP_LOCAL`, `CONFIG_PREEMPT_RT`, and architecture flush hooks.

## Important APIs, Types, And Functions
For local mappings it declares `__kmap_local_pfn_prot()`, `__kmap_local_page_prot()`, `kunmap_local_indexed()`, `kmap_local_fork()`, schedule-in/out hooks, and `kmap_assert_nomap()`. Under `CONFIG_HIGHMEM` it declares `kmap_high()`, `kunmap_high()`, `__kmap_flush_unused()`, and `__kmap_to_page()`, and implements `kmap()`, `kunmap()`, `kmap_local_page()`, `kmap_local_folio()`, atomic kmap variants, highpage counters, and `is_kmap_addr()`. Without highmem, it maps directly through `page_address()`/`folio_address()` and returns zero highmem counts. `kunmap_atomic()` and `kunmap_local()` macros enforce that callers pass addresses, not `struct page *`.

## Control Flow And State
The file selects between global highmem mappings, local per-task/per-CPU mappings, and direct lowmem addresses. Atomic mappings disable page faults and either migration or preemption depending on RT. Local mappings must be unmapped in reverse nesting order. Persistent state belongs to architecture kmap slots, current task kmap control, and per-CPU fixmap state.

## Dependencies And Integration Points
It depends on architecture `asm/highmem.h` when highmem is enabled, page/folio APIs, preemption/migration controls, pagefault controls, fixmap constants, and optional flush hooks. Public `highmem.h` includes this header.

## Risks
Risks include wrong unmap order, assuming atomic kmap side effects, calling sleeping `kmap()` in atomic context, stale mappings across fork/schedule paths, missing architecture flushes, and passing page pointers to unmap macros. Panic-safe mapping returns NULL for highmem pages and callers must handle that.

## Test Signals
Build matrix with and without HIGHMEM/KMAP_LOCAL/PREEMPT_RT, DEBUG_KMAP_LOCAL checks, nested local mapping tests, atomic mapping pagefault/preemption state assertions, fork/schedule hooks, and highmem page copy/zero callers.
