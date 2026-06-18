
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache.h

## Purpose
Defines the pcache cache data model, on-media metadata formats, cache modes, segment/key/keyset structures, tree-walk contracts, and public APIs shared by cache initialization, key replay, request handling, GC, writeback, and segment management.

## Important APIs, Types, And Functions
Key constants define GC thresholds, subtree size, keyset limits, segment limits, writeback/GC intervals, cache modes, and metadata flags. On-media structures include `pcache_cache_pos_onmedia`, `pcache_cache_seg_ctrl`, `pcache_cache_info`, `pcache_cache_key_onmedia`, and `pcache_cache_kset_onmedia`. Runtime structures include `pcache_cache_pos`, `pcache_cache_segment`, `pcache_cache_subtree`, `pcache_cache_tree`, `pcache_cache_key`, `pcache_cache_kset`, `pcache_cache`, `pcache_cache_ctrl`, and per-CPU `pcache_cache_data_head`. Inline helpers cover subtree selection, media addresses, keyset selection, key state, position copying, segment-control detection, key trimming/deletion, CRC checks, cache mode/GC percent fields, key ranges, and tail encode/decode wrappers.

## Control Flow
The header establishes contracts rather than running logic. Request handling uses `cache_subtree_walk()` callback slots to classify before/after/overlap cases. Writers append keysets, readers submit miss requests, GC advances tails and segment references, and writeback advances dirty tails using the declared APIs.

## State And Persistence
This header describes both volatile and persistent state. Persistent state is stored in DAX cache media with CRC/sequence protection for selected records and keyset CRCs. Runtime state includes rbtrees, locks, refs, delayed work, segment maps, and per-CPU heads.

## Dependencies And Integration Points
Depends on `segment.h`, pcache metadata helpers, kernel rbtrees, mempools, workqueues, CRC32C, DAX flush assumptions, backing/cache-dev structures, and `dm_pcache` ownership macros.

## Risks
On-media layouts are ABI-like; changing sizes or fields can break existing cache devices. Inline key deletion erases rb nodes and drops refs, so callers must hold tree locks. `cache_key_invalid()` relies on segment generations advanced by GC. Subtree selection assumes requests are split at 4 MiB boundaries. Several helpers use `BUG_ON`, reflecting strict internal invariants.

## Test Signals
Build all pcache objects, validate on-media struct sizes/CRCs, exercise each cache mode flag, subtree boundary splitting, key trimming/deletion under locks, generation invalidation, tail encode/decode redundancy, GC percent field bounds, and data CRC enabled/disabled replay.
