<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmzone.h -->
# sources/distributed-fs/ceph-client/include/linux/mmzone.h

## Purpose
`mmzone.h` is the core memory-management topology header for zones, nodes, zonelists, LRU vectors, per-CPU page caches, VM statistics, and sparse memory sections. It gives page allocator, reclaim, compaction, memory hotplug, NUMA, and sparsemem code a shared ABI for describing physical memory layout and allocator state.

## Important APIs, Types, and Functions
Key allocator constants include `MAX_PAGE_ORDER`, `MAX_ORDER_NR_PAGES`, `NR_PAGE_ORDERS`, `PAGE_ALLOC_COSTLY_ORDER`, `PAGE_BLOCK_MAX_ORDER`, `MAX_FOLIO_ORDER`, `MAX_FOLIO_NR_PAGES`, and vmemmap-tail sizing macros. `enum migratetype` defines allocator mobility classes (`MIGRATE_UNMOVABLE`, `MIGRATE_MOVABLE`, `MIGRATE_RECLAIMABLE`, `MIGRATE_HIGHATOMIC`, optional `MIGRATE_CMA`, `MIGRATE_ISOLATE`), with helpers such as `is_migrate_cma()`, `is_migrate_movable()`, and `migratetype_is_mergeable()`.

Statistics are declared through `enum zone_stat_item`, `enum node_stat_item`, `enum numa_stat_item`, and helpers `vmstat_item_print_in_thp()` and `vmstat_item_in_bytes()`. LRU state is represented by `enum lru_list`, `struct lruvec`, and, under `CONFIG_LRU_GEN`, `struct lru_gen_folio`, `struct lru_gen_mm_state`, `struct lru_gen_mm_walk`, and `struct lru_gen_memcg`.

The main persistent in-memory structures are `struct zone`, `struct zoneref`, `struct zonelist`, and `pg_data_t` (`struct pglist_data`). Accessors include `wmark_pages()`, `min_wmark_pages()`, `low_wmark_pages()`, `high_wmark_pages()`, `promo_wmark_pages()`, `zone_managed_pages()`, `zone_cma_pages()`, `zone_end_pfn()`, `zone_spans_pfn()`, `zone_is_initialized()`, `zone_is_empty()`, `zone_intersects()`, `managed_zone()`, `populated_zone()`, `zone_to_nid()`, `zone_idx()`, `is_highmem()`, and `has_managed_dma()`.

Allocation traversal and topology APIs include `build_all_zonelists()`, `__zone_watermark_ok()`, `zone_watermark_ok()`, `wakeup_kswapd()`, `kswapd_try_clear_hopeless()`, `kswapd_clear_hopeless()`, `kswapd_test_hopeless()`, `init_currently_empty_zone()`, `lruvec_init()`, `first_online_pgdat()`, `next_online_pgdat()`, `next_zone()`, `first_zones_zonelist()`, `next_zones_zonelist()`, `for_each_online_pgdat`, `for_each_zone`, `for_each_populated_zone`, and zonelist iteration macros.

Sparse memory support defines section/subsection geometry and state with `struct mem_section_usage`, `struct mem_section`, `SECTION_*` flag bits, `pfn_to_section_nr()`, `section_nr_to_pfn()`, `__nr_to_section()`, `__pfn_to_section()`, `present_section*()`, `valid_section*()`, `online_section*()`, `pfn_section_valid()`, `pfn_valid()`, `first_valid_pfn()`, `next_valid_pfn()`, and present/valid PFN iteration helpers.

## Control Flow and State
The header does not implement allocator algorithms directly, but defines the state those algorithms mutate. Allocation paths consult zonelists, zone watermarks, `managed_pages`, free areas, per-CPU pagesets, and migratetypes. Reclaim and compaction paths use `lruvec`, zone flags, compact cached PFNs, `kswapd` fields, and watermark state. Memory hotplug updates `present_pages`, section flags, and node/zone span fields under locks or hotplug synchronization.

Multi-gen LRU state flows through generation counters (`max_seq`, `min_seq`), per-generation folio lists, refault/eviction accounting, and memcg aging lists. Sparsemem validity checks flow from PFN to section number, then through `mem_section` flags and optional subsection bitmaps under scheduler RCU.

## State and Persistence Behavior
All state is in-kernel runtime state. It is not persisted across boots, but some fields are externally observable through `/proc/vmstat`, `/proc/meminfo`, debug paths, and memory hotplug/NUMA interfaces. `pg_data_t`, `zone`, `lruvec`, and `mem_section` instances are long-lived global topology records. Counters are a mix of atomic, per-CPU, seqlock-protected, RCU-protected, and lock-protected fields.

## Dependencies and Integration Points
This header depends on page flags/layout, `mm_types`, node masks, spinlocks, seqlocks, atomic operations, local locks, zswap, architecture page/sparsemem definitions, and optional hotplug/highmem/NUMA/CMA/compaction/LRU_GEN/ZONE_DEVICE features. It is consumed by `mm/page_alloc.c`, reclaim, compaction, memory hotplug, sparsemem, vmstat, NUMA balancing, zswap, and filesystem/page-cache code that needs zone or LRU information.

## Risks
Risks are mostly ABI and concurrency risks: incorrect zone flag packing breaks `struct page` flag decoding; mismatched stat enum ordering breaks vmstat output; stale section state can make `pfn_valid()` lie; missing locks around node/zone span updates can race allocator hot paths; and changing migratetype semantics can fragment memory or break CMA/isolation. Sparsemem code relies on flag-bit alignment assumptions and RCU lifetime rules.

## Test Signals
Useful signals include boot on FLATMEM and SPARSEMEM/VMEMMAP configs, memory hotplug online/offline, NUMA allocation fallback, CMA allocation, compaction and THP tests, `/proc/vmstat` sanity, page allocator stress, kswapd wakeup/reclaim tests, `pfn_valid()` boundary tests, and configs with/without `CONFIG_LRU_GEN`, `CONFIG_HIGHMEM`, `CONFIG_ZONE_DEVICE`, and `CONFIG_MEMORY_HOTPLUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmzone.h -->
