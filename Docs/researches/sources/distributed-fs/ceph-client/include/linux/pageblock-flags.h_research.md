<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pageblock-flags.h -->
# sources/distributed-fs/ceph-client/include/linux/pageblock-flags.h

## Purpose
This header defines pageblock-level flags and helpers used by the buddy allocator, compaction, migratetype selection, hugepage grouping, and memory isolation.

## Important APIs, types, and functions
`enum pageblock_bits` defines migratetype bits, compact-skip, and optional isolate bit. It defines `NR_PAGEBLOCK_BITS`, `MIGRATETYPE_MASK`, `MIGRATETYPE_AND_ISO_MASK`, `pageblock_order`, `pageblock_nr_pages`, alignment helpers, and external helpers `get_pfnblock_migratetype()`, `get_pfnblock_bit()`, `set_pfnblock_bit()`, and `clear_pfnblock_bit()`. Under `CONFIG_COMPACTION`, `get_pageblock_skip()`, `set_pageblock_skip()`, and `clear_pageblock_skip()` manipulate `PB_compact_skip`; otherwise they are no-op/false.

## Control flow
Allocator and compaction code classify PFN blocks by migratetype bits, align PFN ranges to pageblock boundaries, mark blocks skipped by compaction, and optionally isolate blocks for memory isolation. `pageblock_order` is chosen from hugetlb variable/fixed size, THP PMD order, or maximum allocation order.

## State and persistence
Pageblock flags persist in the memory-section/pageblock metadata managed by mm/page_alloc. Migratetype and skip/isolate state affect allocation and compaction decisions until changed.

## Dependencies and integration points
It depends on page types, hugepage/THP configs, memory isolation, compaction, page allocator migratetypes, PFN/page conversion, and alignment macros.

## Risks and test signals
Risks include wrong pageblock size for hugepage/THP configurations, migratetype bit overlap, isolate bit not preserved with migratetype, compaction skip staleness, and alignment mistakes during memory hotplug/CMA. Test migratetype set/get, compaction skip behavior, hugepage/THP pageblock sizing, CMA/memory isolation, memory hotplug ranges, and `!CONFIG_COMPACTION` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pageblock-flags.h -->
