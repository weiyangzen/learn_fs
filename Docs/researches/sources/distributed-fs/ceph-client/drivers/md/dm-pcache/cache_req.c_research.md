
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_req.c

## Purpose
Handles pcache read/write requests against the in-memory key tree and persistent-memory cache data. Reads are satisfied from cached keys when possible and otherwise issue backing-device reads that can populate cache placeholders. Writes allocate cache space, copy bio data into persistent memory, insert replacement keys, and append key metadata.

## Important APIs, Types, And Functions
`cache_data_head_init()` and `cache_data_alloc()` allocate data space from per-CPU cache segment heads without crossing segment boundaries. `cache_copy_from_req_bio()` and `cache_copy_to_req_bio()` transfer data between bios and cache segments while checking segment generation. Miss handling uses `cache_miss_req_alloc()`, `cache_miss_req_init()`, `submit_cache_miss_req()`, `cache_miss_req_free()`, and `miss_read_end_req()`. Read overlap callbacks (`read_before`, `read_overlap_tail`, `read_overlap_contain`, `read_overlap_contained`, `read_overlap_head`) drive `cache_subtree_walk()`. `cache_read()` splits requests by subtree and submits backing reads for misses. `cache_write()` allocates keys/data and inserts/appends them. `pcache_cache_flush()` closes all ksets. `pcache_cache_handle_req()` dispatches flush/read/write.

## Control Flow
Reads build a temporary requested key and walk the relevant subtree. Cached non-empty keys copy data into the upper bio; empty placeholder keys cause backing reads without inserting new placeholders; missing gaps allocate backing reads with empty keys that are inserted before submission. On read completion, a still-empty placeholder is allocated cache data, filled from the upper bio, marked clean, appended to keysets, and retained unless a write deleted it meanwhile. Writes split at 4 MiB subtree boundaries, allocate data space, copy bio contents to DAX cache, insert with overlap fixup, and append key metadata, forcing keyset close on FUA.

## State And Persistence
Runtime state includes per-CPU data heads, pending backing requests, placeholders, tree locks, and request refs. Persistent state is data copied into cache segments plus keysets appended by `cache_key_append()`. Flush closes keysets but lower backing flush/writeback is handled by other subsystems.

## Dependencies And Integration Points
Depends on backing-device request APIs, segment copy helpers, cache key/tree APIs, pcache request refcounting, bio flags, and writeback/GC generation management.

## Risks
Read-miss placeholder races with concurrent writes are handled by checking `cache_key_empty()` under the tree lock, but this is a critical correctness path. Segment generation checks prevent copying from reclaimed data; failure deletes stale keys and restarts. Data allocation may shorten keys at segment boundaries, requiring outer loops. Error paths must release segment refs and key refs exactly. Prefetch reads populate cache from the same upper bio data after backing completion, so request lifetime is important.

## Test Signals
Test full hits, full misses, mixed overlap reads, concurrent read miss and write overwrite, stale generation deletion/research, subtree boundary splits, segment boundary splits, FUA forced keyset close, flush-only requests, allocation failures for preallocated miss requests, backing read errors deleting placeholders, and data CRC replay after writes.
