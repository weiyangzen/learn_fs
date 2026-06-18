# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-target.c

## Purpose
Implements the Device Mapper `cache` target, which maps an origin device through a faster cache device using persistent metadata, a cache replacement policy, dirty/discard tracking, background migration, and writeback/writethrough/passthrough I/O modes.

## Main Interfaces
- Target lifecycle: `cache_ctr()`, `cache_dtr()`, `cache_preresume()`, `cache_resume()`, `cache_postsuspend()`.
- I/O path: `cache_map()`, `cache_end_io()`, `map_bio()`, `process_deferred_bios()`.
- Metadata persistence: `commit()`, `commit_op()`, `sync_metadata()`, `write_dirty_bitset()`, `write_discard_bitset()`, `write_hints()`.
- Migration/invalidation: `mg_start()`, `mg_lock_writes()`, `mg_copy()`, `mg_update_metadata()`, `invalidate_start()`, `invalidate_cblock()`.
- User/control reporting: `cache_status()`, `cache_message()`, `cache_io_hints()`, `cache_iterate_devices()`.

## Control Flow
Incoming bios are converted to cache origin blocks and routed through `map_bio()`. Flushes and discards are deferred to the worker; partial trailing blocks bypass cache and go to origin. Normal bios acquire a bio-prison cell so concurrent access to the same block can be serialized against migration or invalidation.

Policy lookup decides whether a bio is a hit, miss, or should trigger background work. Misses go to origin; hits normally go to cache, with writeback marking cache blocks dirty. Writethrough writes to clean cached blocks are cloned to both origin and cache. Passthrough mode routes to origin and invalidates cached blocks on writes.

Background policy work drives promotions, demotions, and writebacks. Migrations lock writes first, quiesce conflicting bios, copy with kcopyd or use an overwrite optimization, upgrade to a read/write exclusion lock, update metadata, commit when required, then release detained bios.

## State And Synchronization
`struct cache` owns metadata, origin/cache devices, policy state, dirty/discard bitsets, stats, bio prison, kcopyd client, workqueue, delayed commit waker, migration mempool, deferred bio lists, and an I/O tracker. A spinlock protects deferred bios and discard state. The bio prison serializes per-block accesses. `background_work_lock` prevents new background migrations during suspend. The `batcher` groups bios and continuations behind metadata commits.

## Integration Points
Uses `dm-cache-metadata` for persistent mappings, dirty bits, discards, stats, and hints; `dm_cache_policy` for lookup and replacement decisions; `dm-bio-prison-v2` for per-block exclusion; `dm-kcopyd` for data movement; and Device Mapper target hooks for table status, messages, queue limits, and device iteration.

## Notable Behaviors
- Supports `writeback`, `writethrough`, `passthrough`, `metadata2`, and `no_discard_passdown` features.
- Refuses passthrough construction unless all cached blocks are clean.
- FUA and flush bios are issued only after needed metadata commits.
- Suspend drains workers, requeues deferred bios if needed, writes dirty/discard/hint/stat metadata, and commits clean-shutdown state.
- Cache shrinking is refused if any block that would be dropped is dirty.
- `invalidate_cblocks` messages are only allowed in passthrough mode.

## Risks And Review Focus
- Commit ordering is central to correctness, especially demotion, FUA, flush, and suspend paths.
- Dirty-bit and policy state must stay synchronized across migration success and failure.
- Bio-prison lock levels and release paths are sensitive to races with migration, invalidation, and deferred bios.
- Discard tracking uses a coarser discard-block bitmap and must preserve range/granularity correctness.
