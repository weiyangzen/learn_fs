
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_gc.c

## Purpose
Implements pcache garbage collection for keyset metadata and cache segment references. It advances the key tail after the dirty tail has moved far enough and the used-segment percentage crosses the configured GC threshold, releasing segment references held by old cache keys.

## Important APIs, Types, And Functions
`cache_key_gc()` drops the segment reference for a decoded key. `need_gc()` compares dirty-tail and key-tail positions, reads the next keyset from DAX media, validates magic and CRC, and checks used segment count against `pcache_cache_get_gc_percent()`. `last_kset_gc()` handles `PCACHE_KSET_FLAGS_LAST` records by moving the key tail to the next segment and clearing the old segment bit. `pcache_cache_gc_fn()` is the delayed-work entry that loops through eligible keysets, decodes each key, releases references, advances and persists key tail, and requeues itself.

## Control Flow
GC snapshots dirty tail and key tail under their mutexes, calls `need_gc()`, then either handles a segment-transition keyset or walks each key in the current keyset. Decode failure increments `gc_errors` and permanently stops future GC to avoid retrying partially processed metadata. Successful processing advances `cache->key_tail` by the keyset on-media size and writes the new tail position. When no more work is needed, delayed work is queued after `PCACHE_CACHE_GC_INTERVAL`.

## State And Persistence
Persistent state affected by GC is the encoded key-tail position and segment allocation bitmap state indirectly represented by segment metadata. Runtime state includes `gc_errors`, `gc_kset_onmedia_buf`, segment references, and `seg_map`.

## Dependencies And Integration Points
Depends on keyset CRC helpers, cache position encode/decode, segment references from cache segment code, DAX `copy_mc_to_kernel()`, dirty-tail advancement by writeback, and pcache stopping state.

## Risks
GC correctness depends on dirty tail never lagging behind data that still needs writeback. Decode errors stop GC to avoid corrupting state but can fill the cache. `last_kset_gc()` clears segment map bits after moving to the next segment; incorrect tail comparisons could reuse live key metadata. Used-segment threshold controls aggressiveness and defaults to 70 percent.

## Test Signals
Test threshold behavior below/above GC percent, corrupted keyset magic/CRC, last-keyset segment transitions, dirty-tail equals key-tail no-op, decode failure setting `gc_errors`, stopping behavior, repeated requeue interval, segment reference release, and persistence of advanced key tail across restart.
