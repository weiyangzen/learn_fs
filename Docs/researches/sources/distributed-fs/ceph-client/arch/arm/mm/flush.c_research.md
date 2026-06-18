## sources/distributed-fs/ceph-client/arch/arm/mm/flush.c

### Purpose
Implements ARM cache flush/coherency helpers above the CPU-specific cache vector, including VIPT/VIVT alias handling, ptrace/uprobe write visibility, folio D-cache maintenance, and anonymous-page flushing.

### Important APIs, Types, And Functions
Important entry points are `flush_cache_mm`, `flush_cache_range`, `flush_cache_pages`, `copy_to_user_page`, `flush_uprobe_xol_access`, `__flush_dcache_folio`, `__sync_icache_dcache`, `flush_dcache_folio`, `flush_dcache_page`, and `__flush_anon_page`. `arm_heavy_mb` is exported when configured.

### Control Flow
VIVT paths delegate to VIVT helpers. VIPT aliasing paths map a fixed alias at `FLUSH_ALIAS_START` with cache color and perform line or page flushes. Ptrace/uprobe writes copy data then flush D/I aliases based on executable mapping and current CPU membership. Folio flushes either lazily clear `PG_dcache_clean` or perform kernel mapping flushes, user alias walks, and I-cache flushes as required.

### State, Dependencies, And Integration
State includes optional `soc_mb` callback and folio `PG_dcache_clean` bits. Depends on cache type helpers, highmem mappings, mapping interval trees, `mm.h` fixed aliases, SMP broadcast behavior, outer cache sync, and CPU cache-vector functions. Integrates with VM, ptrace, uprobes, page cache, DMA coherency, and executable mapping setup.

### Risks And Test Signals
Risks are stale instruction fetch after code modification, lost D-cache dirty data, over/under-flushing highmem folios, and SMP broadcast assumptions. Test ptrace text pokes, uprobes, JIT/module exec mappings, shared file mmap writes, highmem folios, and cache aliasing platforms.
