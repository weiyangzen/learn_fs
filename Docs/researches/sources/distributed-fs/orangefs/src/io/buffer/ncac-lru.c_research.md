# sources/distributed-fs/orangefs/src/io/buffer/ncac-lru.c

## Purpose
Implements the LRU cache policy operations used by NCAC cache admission, removal, and shrinking.

## Important APIs, Types, And Functions
Exports `LRU_add_cache_item`, `LRU_remove_cache_item`, and `LRU_shrink_cache`.

## Control Flow
Admission inserts the extent at the active-list head and sets `PG_lru`. Removal unlinks from the LRU list and decrements counters. Shrink scans from the active-list tail, checks pending I/O completion if needed, converts completed pending extents to clean, and discards clean unreferenced extents by removing them from LRU and adding them to the free extent list until the expected count is reached or no more victims exist.

## State And Persistence
Mutates cache active-list links/counters, extent LRU flags, inode page counters, and free extent list. No persistent state exists. Callers are expected to hold the cache lock.

## Dependencies And Integration Points
Depends on internal NCAC structures, state and flag helpers, cache discardability, and Trove completion checks. Called from `cache.c` and extent allocation.

## Risks And Test Signals
Risks include only active-list scanning, no inactive-list use despite fields, no clearing of LRU flags on removal, no radix removal during shrink, debug output, and counter consistency questions. Tests should validate shrink under clean, dirty, referenced, and pending I/O victims and ensure evicted extents are no longer discoverable.
