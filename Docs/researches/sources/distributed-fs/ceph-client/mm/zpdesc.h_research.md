# sources/distributed-fs/ceph-client/mm/zpdesc.h

## Purpose
`mm/zpdesc.h` defines `struct zpdesc`, the zsmalloc-specific descriptor overlay for pages that back zspages. It isolates zsmalloc metadata from direct `struct page` field access while preserving the current layout contract with the MM core.

## Important APIs, types, and functions
`struct zpdesc` overlays page fields used by zsmalloc: flags, `lru`, movable operations, `next` or huge-page `handle`, `zspage`, `first_obj_offset`, and refcount. Static offset assertions (`ZPDESC_MATCH`) enforce layout compatibility with `struct page`. Conversion helpers are `zpdesc_page()`, `zpdesc_folio()`, and `page_zpdesc()`. Inline wrappers provide lock, trylock, unlock, wait, get/put, local kmap, PFN conversion, movable/zsmalloc page-type marking, zone lookup, and lock-state testing.

## Control flow
The header itself has no runtime control flow beyond inline wrappers. zsmalloc allocates normal pages, casts the head page to `zpdesc`, fills zsmalloc metadata, and calls these helpers when it must interact with folio/page APIs, migration, kmap, zone accounting, or page flags.

## State and persistence
`zpdesc` state is the live page descriptor state for zsmalloc pages. It persists only while the backing page is allocated. `PG_private` marks the first component page, `PG_locked` is used by migration/page lock code, and `PageZsmalloc` is sticky until the page returns to the buddy allocator.

## Dependencies and integration points
The header depends on folio/page APIs, migration support, and pagemap helpers. It is consumed by `zsmalloc.c` to bridge zsmalloc internals with generic MM operations such as page migration and zone statistics.

## Risks and invariants
The layout must not grow into `struct page` fields that zsmalloc does not own, especially memcg-related overlap. `first_obj_offset` has only 24 usable bits because upper bits encode page type. Callers must avoid arbitrary casts and use helpers so future representation changes remain possible.

## Test signals
Build-time static assertions are the first signal. Runtime coverage comes from zsmalloc allocation/free, migration/compaction, highmem kmap paths, and debug VM checks around `PageZsmalloc`, first-page marking, and page locks.
