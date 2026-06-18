# sources/distributed-fs/orangefs/src/io/buffer/cache.c

## Purpose
Implements common NCAC cache item operations independent of a specific cache policy: lookup, insert, remove, free-list extraction, shrinking, discardability checks, and hit promotion.

## Important APIs, Types, And Functions
Public functions are `lookup_cache_item`, `add_cache_item`, `remove_cache_item`, `get_free_extent_list_item`, `shrink_cache`, `is_extent_discardable`, and `hit_cache_item`. Private helpers split radix/inode bookkeeping from policy-list bookkeeping.

## Control Flow
Lookup queries an inode radix tree. Add first inserts into the radix tree and inode clean list, then adds to the selected policy list, currently LRU. Remove performs the inverse order: LRU removal followed by radix deletion and mapping clear. `shrink_cache` dispatches to LRU shrink logic for LRU and ARC constants. Cache hits remove and re-add the item in the policy list to refresh its position.

## State And Persistence
State changes are in-memory inode radix trees, clean-page lists, extent mapping/index fields, and global cache-stack active/inactive/free counters. No persistent state exists. Locking is expected to be handled by callers; helper comments identify inode/cache-stack protection expectations but this file does not acquire locks itself.

## Dependencies And Integration Points
Depends on NCAC internal structs, state/flag macros, `radix`, and `ncac-lru`. It is used by NCAC read/write job processing and eviction.

## Risks And Test Signals
Risks include missing list deletion from `mapping->clean_pages` in `remove_cache_item_no_policy`, double `nrpages` accounting because both radix add and LRU add increment inode counters, ARC falling back to LRU, and no lock enforcement. Tests should cover add/lookup/remove, duplicate insert failure, discard rules for dirty or referenced extents, shrink under pending I/O, and counter/list consistency.
