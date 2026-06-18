# sources/distributed-fs/orangefs/src/io/buffer/ncac-lru.h

## Purpose
Declares LRU policy functions for the NCAC cache.

## Important APIs, Types, And Functions
Declares `LRU_add_cache_item`, `LRU_remove_cache_item`, and `LRU_shrink_cache`.

## Control Flow
These functions are called by generic cache-policy wrappers during admission, removal, hit refresh, and eviction.

## State And Persistence
The header has no state. Implementations mutate `struct cache_stack` and `struct extent` objects.

## Dependencies And Integration Points
Relies on internal type visibility from including translation units. Included by `cache.c` and `ncac-lru.c`.

## Risks And Test Signals
Risks are declaration drift and lack of documented locking requirements in the header. Build and eviction-policy tests are signals.
