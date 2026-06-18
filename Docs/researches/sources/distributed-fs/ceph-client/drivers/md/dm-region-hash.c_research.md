# sources/distributed-fs/ceph-client/drivers/md/dm-region-hash.c

## Purpose
Provides the shared region-state engine used by the mirror target. It maps sectors/bios to dirty-log regions, caches nontrivial region states in a hash table, tracks pending writes, coordinates recovery quiescing, delays bios that conflict with recovery, and updates the persistent dirty log.

## Important APIs, Types, And Functions
`struct dm_region_hash` holds region size/shift, dirty log, hash buckets, locks, flush-failure flag, recovery semaphore/count, clean/quiesced/recovered/failed lists, mempool, callbacks, and target begin sector. `struct dm_region` stores key, state, hash/list nodes, pending count, and delayed bios.

Exported APIs include `dm_region_hash_create()`, `dm_region_hash_destroy()`, `dm_rh_dirty_log()`, `dm_rh_bio_to_region()`, `dm_rh_region_to_sector()`, `dm_rh_get_state()`, `dm_rh_inc_pending()`, `dm_rh_dec()`, `dm_rh_mark_nosync()`, `dm_rh_update_states()`, `dm_rh_recovery_prepare()`, `dm_rh_recovery_start()`, `dm_rh_recovery_end()`, `dm_rh_recovery_in_flight()`, `dm_rh_flush()`, `dm_rh_delay()`, `dm_rh_stop_recovery()`, and `dm_rh_start_recovery()`.

## Control Flow
Writes call `dm_rh_inc_pending()` to allocate/find each region, transition clean regions to dirty, and mark them in the dirty log. Completion calls `dm_rh_dec()`, which moves zero-pending dirty regions to the clean list, recovering regions to the quiesced list, or leaves no-sync regions resident. The mirror worker periodically calls `dm_rh_update_states()` to remove clean/recovered regions from the hash, clear or update log state, dispatch delayed bios, release recovery slots, and flush the dirty log.

Recovery starts with `dm_rh_start_recovery()` seeding the recovery semaphore. `dm_rh_recovery_prepare()` asks the dirty log for resync work, marks selected regions recovering, and either waits for pending writes to drain or places already-quiesced regions on the quiesced list. The caller starts I/O for regions returned by `dm_rh_recovery_start()` and later calls `dm_rh_recovery_end()` with success/failure, which queues the region for state update and wakes workers.

## State And Persistence
The hash is an in-memory cache of regions that are dirty, no-sync, recovering, recently clean, or awaiting recovered processing. Persistent state is delegated to `struct dm_dirty_log` operations: `mark_region`, `clear_region`, `set_region_sync`, `get_resync_work`, `flush`, and `in_sync`. A flush failure sets `flush_failure`, preventing later write completions from being marked clean because durability is uncertain.

Locking is split between `hash_lock` for bucket membership and `region_lock` for state/list/delayed-bio fields. A recovery semaphore limits parallel recovery to `max_recovery`, and `recovery_in_flight` lets suspend wait until recovery callbacks have fully dispatched delayed bios.

## Dependencies And Integration Points
This module exports GPL symbols used by `dm-raid1.c` and any other DM target using dirty-log region recovery. It depends on `dm-dirty-log.h`, `dm-region-hash.h`, bio lists, vmalloc buckets, mempools, spin/rw locks, semaphores, and caller-provided callbacks to dispatch delayed bios and wake workers/waiters.

## Risks
The state machine is concurrency-sensitive: regions move among hash buckets and clean/quiesced/recovered lists under different locks, and callers must pair pending increments/decrements exactly. `dm_rh_delay()` appends to a region's delayed list under only the hash read lock, relying on region lifetime and caller sequencing. Flush failure handling is intentionally pessimistic; clearing it incorrectly could lose mirrored consistency. Destroy asserts no quiesced regions and no pending writes, so teardown ordering must be correct.

## Test Signals
Test region-size mapping, dirty-to-clean transitions, no-sync marking on write/flush failure, delayed bios during recovery, recovery success and failure paths, max-recovery throttling, stop/start recovery during suspend/resume, dirty-log operation failures, and hash races under concurrent writes to the same region. Mirror-target recovery tests are the main integration signal.
