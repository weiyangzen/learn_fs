# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_segment.c

## Purpose
Implements persistent-cache segment metadata management for `dm-pcache`. A cache segment wraps one physical cache-device segment, stores replicated segment-info records at the beginning of the segment, stores a replicated generation counter in the segment-control area, and exposes allocation/reference helpers used by cache writes, garbage collection, and key cleanup.

## Important APIs, Types, And Functions
The file operates on `struct pcache_cache_segment`, `struct pcache_segment_info`, `struct pcache_cache_seg_ctrl`, and `struct pcache_cache_seg_gen` from the pcache headers. `cache_seg_init()` initializes a segment either as new media or by loading existing metadata. `get_cache_segment()` finds and reserves a free cache segment in `cache->seg_map`. `cache_seg_get()` and `cache_seg_put()` maintain the segment reference count, and `cache_seg_set_next_seg()` persists segment chaining through `next_seg`.

Private helpers `cache_seg_info_write()` and `cache_seg_info_load()` maintain the metadata slot selected by `info_index`, increment the metadata sequence, calculate CRC with `pcache_meta_crc()`, and use `pcache_meta_find_latest()` on reload. `cache_seg_ctrl_write()`, `cache_seg_ctrl_load()`, and `cache_seg_gen_increase()` do the same for the segment generation record.

## Control Flow
Initialization calls `pcache_segment_init()` with data starting after the segment-info and control areas. For a newly formatted cache, `cache_seg_init()` zeroes the metadata/control ranges, writes an initial generation, writes segment info, and writes `pcache_empty_kset` at the data start to invalidate old key-set contents. For an existing cache, it loads the latest valid segment-info and generation entries before the segment can be used.

Allocation scans `cache->seg_map` from `cache->last_cache_seg`, wraps once, marks the found bit, and reports the cache as full if no zero bit exists. When the last reference is dropped, `cache_seg_put()` invalidates the segment by incrementing and persisting its generation, clears its bitmap bit, clears `cache_full`, wakes deferred requests, and queues `clean_work` so stale keys pointing at the old generation can be removed.

## State And Persistence
Persistent state is stored directly in pmem/DAX-mapped cache segments. The segment-info area uses `PCACHE_META_INDEX_MAX` alternating slots with CRC and sequence numbers; the control area persists the generation counter the same way. Writes use `memcpy_flushcache()` followed by `pmem_wmb()`, so crash recovery can select the latest complete record and ignore torn or corrupt metadata.

Volatile state includes the segment allocation bitmap, `last_cache_seg` search hint, `cache_full`, reference counters, `info_lock`, and `gen_lock`. The generation value is the core stale-reference guard: keys that name an old generation become invalid after the segment is recycled.

## Dependencies And Integration Points
This file depends on `cache_dev.h` for cache-device address layout and zeroing, `cache.h` for key-set metadata and work items, `segment.h` for generic segment initialization, and `dm_pcache.h` for logging and deferred-request wakeups. It integrates with the cache write path through segment allocation and references, with garbage collection through invalidation and `clean_work`, and with replay/recovery through persisted segment metadata.

## Risks
Metadata slot ordering and CRC logic are high-risk because a wrong `info_index` or generation slot can resurrect stale keys after crash recovery. `get_cache_segment()` assumes the segment bitmap is authoritative and protected by `seg_map_lock`; a missed bit clear can permanently reduce capacity, while a premature clear can allow overwrite of referenced data. `cache_seg_ctrl_write()` intentionally avoids locking based on single-threaded access assumptions, so future callers must not introduce concurrent generation writes without revisiting that contract.

## Test Signals
Useful signals include format and reload tests that verify segment info/generation survives remount, forced corruption of one metadata slot to confirm the alternate slot is chosen, write/read tests across segment reuse, cache-full/deferred-request recovery tests, and GC tests that confirm old-generation keys are removed after `cache_seg_put()`. Persistent-memory fault tests should exercise `copy_mc_to_kernel()` and CRC rejection paths.
