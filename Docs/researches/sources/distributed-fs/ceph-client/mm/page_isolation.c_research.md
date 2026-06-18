# sources/distributed-fs/ceph-client/mm/page_isolation.c

## Purpose
`page_isolation.c` isolates ranges of physical memory at pageblock granularity for memory offlining and contiguous allocation. It marks pageblocks `MIGRATE_ISOLATE`, moves free pages to isolation freelists, handles boundary cases where large pages cross isolation boundaries, and tests whether isolated ranges have become free.

## Important APIs, Types, And Functions
- `page_is_unmovable()` classifies a page as unmovable for a given `enum pb_isolate_mode`.
- `has_unmovable_pages()` scans one pageblock intersection for pages that prevent isolation.
- `set_migratetype_isolate()` and `unset_migratetype_isolate()` mutate pageblock migration type and zone isolation accounting.
- `isolate_single_pageblock()` isolates a boundary pageblock and validates or handles larger pages crossing the boundary.
- `start_isolate_page_range()`, `undo_isolate_page_range()`, and `test_pages_isolated()` are the external range operations.
- `__test_page_isolated_in_pageblock()` verifies that pages are free, HWPoisoned/offline-acceptable, or otherwise not blocking offlining.

## Control Flow
Range isolation aligns the requested PFNs to pageblock boundaries, isolates the first boundary block, isolates the last boundary block, and then walks interior pageblocks. Each pageblock isolation takes `zone->lock`, rejects already isolated blocks, accepts unaccepted pages when necessary, checks only the relevant intersection for unmovable pages, calls `pageblock_isolate_and_move_free_pages()`, and increments `zone->nr_isolate_pageblock`. Boundary isolation additionally scans the surrounding MAX_ORDER-aligned area to detect a compound or free allocation that straddles the target boundary. Undo walks aligned blocks and unsets isolate state. Testing waits for deferred hugetlb frees, confirms all pageblocks are isolated, then under the zone lock scans for buddy pages or special offlining exemptions.

## State And Persistence Behavior
The file mutates allocator runtime state: pageblock migratetype bits, free lists, `zone->nr_isolate_pageblock`, buddy orders, and trace events. There is no disk persistence. Isolation is intentionally reversible and must be undone on partial failure.

## Dependencies And Integration Points
It depends on buddy allocator internals, pageblock flags, memory hotplug, CMA allocation modes, hugetlb migration support, movable page operations, unaccepted memory acceptance, page owner dump diagnostics, and `trace/events/page_isolation.h`. It is used by memory offlining and contiguous range allocation paths.

## Risks
- Page mobility classification is a conservative sample and can race with allocation, freeing, LRU isolation, or movable-ops setup.
- Overlapping isolation attempts are serialized only by pageblock state and can fail with `-EBUSY`.
- Free pages can remain on per-CPU page lists after isolation unless callers drain or disable PCP lists when stronger guarantees are needed.
- Large compound pages crossing pageblock boundaries are difficult; unsupported cases intentionally fail isolation.
- Forgetting to undo partially isolated ranges leaves allocator capacity stranded on isolate lists.

## Test Signals
- Memory offline and `alloc_contig_range()` over ranges with movable LRU pages, CMA pages, hugetlb pages, HWPoison pages, PageOffline pages, holes, and unaccepted pages.
- Boundary tests where MAX_ORDER pages cross the start or end PFN.
- Concurrent overlapping isolation attempts should return `-EBUSY` and restore prior state.
- Trace `test_pages_isolated` and inspect zone isolate counters/free lists after success and rollback.
