# sources/distributed-fs/orangefs/src/io/buffer/cache.h

## Purpose
Declares cache-policy constants and common NCAC cache-management functions.

## Important APIs, Types, And Functions
Defines discard/refill cluster constants, `LRU_POLICY`, `ARC_POLICY`, and `TWOQ_POLICY`. Declares lookup, free extent retrieval, add/remove, shrink, discardability, and hit handlers.

## Control Flow
Callers use these functions from job/state code when locating extents, admitting extents into cache, evicting clean extents, and refreshing policy position on hits.

## State And Persistence
No state is defined directly; the prototypes operate on `struct inode`, `struct extent`, and `struct cache_stack` from `internal.h`.

## Dependencies And Integration Points
This header is included by NCAC job, state, internal, and LRU code. It relies on prior visibility of NCAC internal types.

## Risks And Test Signals
Risks are declaration drift and policy constants that imply ARC/TWOQ support not actually implemented in `cache.c`. Build and policy-dispatch tests are useful.
