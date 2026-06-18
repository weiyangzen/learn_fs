# sources/distributed-fs/ceph/src/osd/OSDMapMapping.cc

## Purpose
`OSDMapMapping.cc` implements the precomputed PG mapping cache and the parallel work queue used to populate it. It materializes, for every pool and PG slot in an `OSDMap`, the up set, up primary, acting set, and acting primary, then builds a reverse acting map from OSD to PGs. This avoids repeated CRUSH/upmap/temp calculation in callers that need to scan large portions of the map.

## Important APIs and Functions
`OSDMapMapping::_init_mappings()` synchronizes the internal per-pool tables with the current `OSDMap` pools, preserving reusable mappings when pool `pg_num` and size are unchanged and dropping removed or resized pools. `update(const OSDMap&)` performs a complete synchronous rebuild by initializing mappings, updating every pool range, and finishing. `update(const OSDMap&, pg_t)` refreshes one PG row in an existing table. `_update_range()` calls `OSDMap::pg_to_up_acting_osds()` for each PG slot and writes the row. `_build_rmap()` constructs `acting_rmap`, skipping `CRUSH_ITEM_NONE`, and `_finish()` rebuilds the reverse map and records the epoch.

The file also implements `ParallelPGMapper::Job::finish_one()`, `ParallelPGMapper::WQ::_process()`, and `ParallelPGMapper::queue()`. `queue()` splits either an explicit PG vector or every pool's `[ps, ps_end)` ranges into work items of `pgs_per_item`, increments the job shard count before enqueue, and asserts that at least one item was queued.

## Control Flow
Full synchronous rebuild is linear: `_start()` calls `_init_mappings()`, every pool range is recalculated by `_update_range()`, and `_finish()` builds reverse OSD-to-PG indexes and copies `osdmap.get_epoch()`. The parallel path is similar, but `OSDMapMapping::start_update()` creates a `MappingJob`, initializes table shape in the constructor, and asks `ParallelPGMapper` to queue all ranges. Worker threads process each `Item`, call either `Job::process(pgs)` or `Job::process(pool, begin, end)`, then call `finish_one()`. When the final shard finishes, the job stamps `finish`, calls `complete()` (which invokes `_finish()`), wakes waiters, and completes any registered finish context.

Abort handling is cooperative. `Job::abort()` marks the job aborted, steals the finish context, waits for all already-started shards to finish, then completes the finish context with `-ECANCELED`. The work queue drops aborted items in `_dequeue()` by calling `finish_one()` and deleting the item instead of processing it.

## State and Persistence
The mapping is process-local cache state, not durable storage. `PoolMapping` rows contain six regions: acting primary, up primary, acting count, up count, acting OSD vector capacity equal to pool size, and up OSD vector capacity equal to pool size. `OSDMapMapping` owns the `pools` table, `acting_rmap`, `epoch`, and `num_pgs`. `ParallelPGMapper::Job` owns timing, shard count, abort state, an optional completion context, a mutex, and a condition variable.

## Dependencies and Integration Points
The implementation depends directly on `OSDMap` placement APIs, `pg_pool_t` pool shape, Ceph work queues/thread pools, `Context` completion callbacks, and CRUSH's `CRUSH_ITEM_NONE` sentinel. OSD services that need PG-to-OSD or OSD-to-PG mappings can use this cache instead of recomputing against `OSDMap` repeatedly.

## Risks
Parallel updates mutate shared `OSDMapMapping` tables from multiple work items. Correctness relies on work item ranges being non-overlapping and table shape being fixed before workers start. `queue()` asserts that at least one item exists, so an empty map or zero `pgs_per_item` would be hazardous. `PoolMapping::set()` truncates oversized vectors to pool size to avoid table overflow, which prevents crashes but can make the cache less accurate if upstream mapping ever returns more entries than expected. `acting_rmap` indexes by OSD id and assumes acting OSD ids are below `osdmap.get_max_osd()`.

## Test Signals
Tests should compare cached `get()` results with direct `OSDMap::pg_to_up_acting_osds()` for replicated and EC pools, verify pool resize/removal behavior, check single-PG update, validate reverse acting maps, and exercise parallel completion, wait, finish-context, and abort paths. Edge cases include `CRUSH_ITEM_NONE`, temp/upmap changes, pool size changes, and explicit PG-vector queueing.
