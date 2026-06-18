# sources/distributed-fs/ceph-client/arch/arm/mm/cache-xsc3l2.c

Purpose: implements XScale3 L2 cache maintenance and registration for systems where the XSC3 L2 cache is present and enabled.

Important APIs/types/functions: important helpers include `xsc3_l2_present`, `xsc3_l2_clean_mva`, `xsc3_l2_inv_mva`, `xsc3_l2_inv_all`, `l2_map_va`, `l2_unmap_va`, `xsc3_l2_inv_range`, `xsc3_l2_clean_range`, `xsc3_l2_flush_all`, `xsc3_l2_flush_range`, and initcall `xsc3_l2_init`. Constants define L2 enable bit `CR_L2`, 32-byte lines, and set/way sizing from L2 type.

Control flow: `core_initcall` checks CPU type and L2 presence. If CR_L2 is set, it invalidates all L2 and installs `outer_cache` range callbacks. Runtime range operations map physical addresses to virtual addresses when highmem is enabled because XScale3 cache ops use MVA, then perform clean/invalidate by line or set/way for all-cache sentinel ranges.

State and persistence: no global C state beyond `outer_cache` assignment. Highmem mappings are transient per operation. Hardware L2 state persists until cache operations or reset.

Dependencies and integration points: selected by `CACHE_XSC3L2`, depends on XScale3 CP15 private cache registers, `cpu_is_xsc3`, highmem `kmap_atomic_pfn`, and global `outer_cache`.

Risks: cache maintenance uses MVA rather than PA, requiring correct highmem temporary mappings and unmapping. The all-cache sentinel is `start == 0 && end == -1ul`; callers must use it intentionally. If L2 is present but CR_L2 is disabled, callbacks are not installed.

Test signals: boot XScale3 with L2 enabled and disabled, run highmem and lowmem DMA coherency tests, verify all-cache flush/invalidate sentinel behavior, and compare set/way loops against detected L2 type size.
