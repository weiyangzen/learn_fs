<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cacheflush.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cacheflush.h

**Purpose:** Declares and wraps MIPS cache flush operations for memory management, user pages, vmaps, and instruction/data coherency.

**Important APIs/types/functions:** Function pointers cover full/mm/range/page flushes, icache flushes, vmap/vunmap, and kernel vmap range flushes. Inline helpers include `flush_dcache_folio`, `flush_dcache_page`, `flush_anon_page`, `flush_cache_vmap`, `flush_cache_vunmap`, `flush_kernel_vmap_range`, and `invalidate_kernel_vmap_range`.

**Control flow:** Runtime CPU feature flags determine whether to flush aliasing D-cache lines immediately or mark folios `PG_dcache_dirty`.

**State, dependencies, integration:** Depends on CPU cache flags and MM folio/page state. Used by mmap, exec, copy-to-user-page, and vmalloc paths.

**Risks and test signals:** Cache alias bugs show as stale I-cache/D-cache data. Test executable page writes, aliasing-cache CPUs, non-ic-fills-from-dcache CPUs, vmalloc/vmap, and anon page flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cacheflush.h -->
