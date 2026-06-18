# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/sparse-cache.h

## Purpose
Declares the sparse-cache API and documents its concurrency contract for lock-free reads with barrier-coordinated membership updates.

## Important APIs, Types, And Functions
Forward-declares `struct index_zone` and `struct sparse_cache`. Exposes creation/free, membership query, coordinated update, invalidate, and search functions. Search returns a virtual chapter and record page for a record name.

## Control Flow
Index triage decides when a sparse chapter might need caching, then zone workers call `uds_update_sparse_cache()`. Normal request processing calls `uds_sparse_cache_contains()` for a known chapter or `uds_search_sparse_cache()` after volume-index miss.

## State And Persistence
The header emphasizes that cache membership must not change between coordinated update calls and that all zones must observe identical membership. It contains no persistent format; sparse chapter pages remain stored in the volume and are cached in memory.

## Dependencies And Integration Points
Includes geometry and public indexer types. It integrates directly with `index.c` zone workers and volume/page-map code through the implementation.

## Risks
Callers must obey the "all zones, same chapter" update rule. Membership checks are not a substitute for searchability: expired and skip-search chapters may still be members but be skipped by full-cache search.

## Test Signals
Concurrency tests should validate no read locks are needed between barriers, cache membership consistency across zones, and correct search results when chapters are skipped or expired.
