<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush_32.h

## Purpose
This header provides SPARC32 cache flush APIs for MM, DMA, signal, and user-page coherency.

## Important APIs, Types, and Functions
It maps generic flush calls to `BTFIXUP_CALL` hooks, declares `sparc_flush_page_to_ram()`, `sparc_flush_folio_to_ram()`, `flush_user_windows()`, `kill_user_windows()`, and `flushw_all()`, and defines user-page copy helpers that flush copied executable data.

## Control Flow
MM code invokes flush macros during mapping changes, page copying, vmap/vunmap, and DMA preparation. Runtime-fixed function pointers select CPU-specific flush implementations.

## State and Persistence Behavior
No persistent C state is owned here, but operations alter CPU caches and register-window state.

## Dependencies and Integration Points
It depends on SPARC32 cache/TLB fixups, `struct page`/`folio`, and generic MM cacheflush APIs.

## Risks
Missing flushes can expose stale instructions/data, especially with executable user mappings and virtually indexed caches. Overbroad `flush_cache_all()` hurts performance.

## Test Signals
Run fork/exec, signal trampoline, self-modifying code, DMA, vmap/vunmap, and CPU-specific SPARC32 boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush_32.h -->
