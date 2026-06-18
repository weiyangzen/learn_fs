<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush_mm.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush_mm.h

## Purpose
This header implements cache maintenance for MMU-enabled m68k systems. It covers ColdFire, 68040/060, and older CACR-driven CPUs, and exposes Linux cacheflush hooks used by memory management, DMA, and executable mapping paths.

## Important APIs, Types, And Functions
- ColdFire helpers `clear_cf_icache()`, `clear_cf_dcache()`, `clear_cf_bcache()`, `flush_cf_icache()`, `flush_cf_dcache()`, and `flush_cf_bcache()` manipulate CACR or `cpushl`.
- `flush_icache()` handles whole-instruction-cache flush by CPU family.
- External range helpers: `cache_clear()`, `cache_push()`, and `cache_push_v()`.
- `__flush_cache_all()`, `__flush_cache_030()`, `flush_cache_mm()`, `flush_cache_range()`, and `flush_cache_page()` integrate with VM changes.
- `__flush_pages_to_ram()` pushes/invalidates page data before instruction use or DMA visibility.
- Public hooks include `flush_dcache_page()`, `flush_dcache_folio()`, `flush_icache_pages()`, `flush_icache_user_page()`, `flush_icache_range()`, `copy_to_user_page()`, and `copy_from_user_page()`.

## Control Flow
Flush functions branch on `CPU_IS_COLDFIRE`, `CPU_IS_040_OR_060`, and `CPU_IS_020_OR_030`. VM flushes only act on the current mm for 030-style caches. Page flushing converts kernel virtual addresses to physical addresses for 040/060 `cpushp` loops or set indexes for ColdFire.

## State And Persistence Behavior
The state affected is CPU cache content and, indirectly, memory visibility for DMA and instruction fetch. The header owns no software state but depends on current task/mm and CPU feature state.

## Dependencies And Integration Points
It depends on Linux MM types, page helpers, CPU feature macros, physical address translation, and ColdFire cache constants. It integrates with mmap/munmap, fork, user-page copying, module/text patching, signal trampolines, and DMA/cache coherency paths.

## Risks And Edge Cases
CPU-family-specific assembly must match available instructions. Flushing too little can execute stale instructions or expose stale DMA data; flushing too much costs performance. Current-mm checks are subtle for aliasing caches.

## Test Signals
Run executable mapping/self-modifying-code tests, ptrace/signal trampoline tests, DMA coherency tests, fork/mmap stress, module load/unload, and cross-builds for ColdFire, 030, 040, and 060 targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush_mm.h -->
