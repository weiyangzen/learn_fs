<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page-flags.h -->
# sources/distributed-fs/ceph-client/include/linux/page-flags.h

## Purpose
This is the central page/folio flag API. It defines page flag bits, compound-page head/tail handling, folio conversion, flag policy macros, generated-style Page/Folio accessors, mapping flag encodings, page type encodings, and allocator sanity masks.

## Important APIs, types, and functions
`enum pageflags` defines core bits such as locked, writeback, referenced, uptodate, dirty, lru, head, waiters, active, workingset, owner/private bits, reserved, reclaim, swapbacked, unevictable, dropbehind, mlocked, hwpoison, young/idle, and arch bits, plus aliases for readahead, swapcache, checked, anon-exclusive, mappedtodisk, fscache/Xen/migration/reported/hotplug/compound-second-page uses. Core helpers include `_compound_head()`, `compound_head()`, `set_compound_head()`, `clear_compound_head()`, `page_folio()`, `folio_page()`, `PageTail()`, `PageCompound()`, `PagePoisoned()`, `const_folio_flags()`, `folio_flags()`, many `Page*`/`folio_*` accessors, `folio_test_uptodate()`/mark helpers with barriers, writeback start declarations, folio large/head helpers, page type ops (`PageBuddy`, `PageOffline`, `PageTable`, `PageGuard`, `PageSlab`, `PageZsmalloc`, `PageUnaccepted`, `PageLargeKmalloc`, `PageNetpp`), `PageHuge()`, hwpoison checks, movable-ops flags, anon-exclusive helpers, `folio_has_private()`, and check masks.

## Control flow
Flag accessors route operations to the correct physical `struct page`: any page, head page, no-tail, no-compound, or first tail page for compound-only flags. Compound-head lookup reads `compound_info`, either as a direct head pointer with bit 0 as tail marker or as a mask when HugeTLB vmemmap optimization allows. Uptodate setting uses a write barrier before setting the bit; testing uses a read barrier after observing the bit. Page type helpers encode special non-mapcount page states in the high byte of `page_type`, with debug checks when setting/clearing.

## State and persistence
Persistent runtime state is in `struct page`: `flags`, `compound_info`, `mapping`, `page_type`, and related folio fields. Flags track page cache, writeback, LRU, reclaim, swap, memory failure, migration, allocator, compound, and owner-specific state across page lifetime. Allocator masks define what must be clear at free/prep while preserving exceptional hwpoison state.

## Dependencies and integration points
It depends on mm types, generated bounds, bitops/bug/mmdebug, memory barriers, page allocator, file cache, reclaim, swap, highmem, KSM, THP/HugeTLB, memory failure, migration, Xen, page idle, memory hotplug, slab, zsmalloc, page pool, and architecture-specific page bits.

## Risks and test signals
Risks include operating on tail pages with the wrong policy, missing memory barriers around uptodate data visibility, alias-bit confusion across subsystems, corrupting `page_type` mapcount/type encoding, stale compound head during split races, allocator free/prep flag leaks, and improper use of owner-private flags. Test page allocator debug checks, folio split/merge, THP/HugeTLB, writeback and page-cache uptodate ordering, KSM/anon mapping flags, swapcache, memory failure/hwpoison, migration movable-ops, highmem, page idle, and 32-bit/64-bit config variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page-flags.h -->
