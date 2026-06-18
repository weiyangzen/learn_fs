# sources/distributed-fs/ceph-client/arch/xtensa/mm/cache.c

Purpose: Maintains Xtensa D-cache aliasing and I-cache/D-cache coherency for user pages, page cache pages, MMU updates, and user-page copying.

Important APIs, types, and functions: `clear_user_highpage()`, `copy_user_highpage()`, `flush_dcache_folio()`, `local_flush_cache_range()`, `local_flush_cache_page()`, `update_mmu_cache_range()`, `copy_to_user_page()`, `copy_from_user_page()`, `PG_arch_1`, and alias helper functions.

Control flow: For aliasing caches, highpage clear/copy maps pages at color-matched temporary aliases, invalidates conflicting kernel mappings, marks folio cache state, and uses assembly alias helpers. `flush_dcache_folio()` either defers flushing with `PG_arch_1` for unmapped page-cache pages or flushes/invalidate aliases immediately. `update_mmu_cache_range()` flushes stale TLB entries and resolves pending cache coherency before mapping a folio.

State and persistence: Uses `PG_arch_1` differently depending on aliasing mode: dirty/deferred flush for aliasing, clean I/D coherence marker for non-aliasing executable pages. Temporarily disables preemption around TLB temporary alias use.

Dependencies and integration: Depends on `mm/misc.S` cache/TLB alias routines, folio/page cache state, TLB flush API, VM flags, highmem mapping, and SMP wrappers in `smp.c`.

Risks: Misinterpreting `PG_arch_1` causes stale instruction fetches or D-cache alias corruption; preemption must be disabled while temporary TLB aliases are active; whole-cache range flushes are blunt and expensive.

Test signals: Executable mmap after writes, page-cache mmap sharing, highmem user pages, alias-color stress with `SHMLBA`, SMP cache flushes, and self-modifying/user text tests.
