# File Research: sources/block-storage/linux-dm/drivers/md/dm-region-hash.c

## Purpose

`dm-region-hash.c` provides the dirty-region state machine used by the mirror target. It tracks which regions are clean, dirty, nosync, recovering, quiesced for recovery, recovered, or failed recovery, and coordinates delayed bios with dirty-log updates.

## Data Structures

`struct dm_region_hash` stores the region size/shift, dirty log, hash table, list locks, recovery concurrency limit, recovery semaphore, in-flight recovery count, clean/quiesced/recovered/failed lists, mempool, target offset, and callbacks for dispatching bios and waking workers/waiters.

`struct dm_region` stores the region key, state, hash/list nodes, pending I/O count, and delayed bios. Clean regions may be omitted from the hash, while dirty/nosync/recovering regions remain present until state transitions allow removal.

## State Transitions

`dm_rh_inc_pending()` allocates/fetches regions for normal writes, increments pending counts, turns clean regions dirty, removes them from the clean list, and marks the dirty log. Flush and discard bios are ignored for region pending counts.

`dm_rh_dec()` decrements pending counts. When a region reaches zero pending I/O, dirty regions become clean and move to `clean_regions`, recovering regions move to `quiesced_regions`, and regions affected by flush failure become nosync.

`dm_rh_update_states()` removes clean/recovered lists from the hash, clears dirty-log regions, completes successful or failed resync work, frees region objects, and flushes the dirty log.

## Recovery Coordination

`dm_rh_start_recovery()` releases `max_recovery` semaphore slots and wakes workers. `dm_rh_stop_recovery()` consumes those slots to stop new recovery. `dm_rh_recovery_prepare()` asks the dirty log for resync work, marks chosen regions recovering, and either moves already-quiesced regions to the quiesced list or waits for pending I/O to drain.

`dm_rh_recovery_start()` hands quiesced regions to the caller. `dm_rh_recovery_end()` places completed regions on the recovered or failed-recovered list and wakes workers. Completion dispatches delayed bios before waking recovery waiters so suspend cannot finish before queued work is visible.

## Invariants And Risks

- `hash_lock` protects the hash table; `region_lock` protects region state, lists, and delayed bios.
- Dirty-log errors from `in_sync()` are treated as nosync.
- `dm_rh_mark_nosync()` is not interrupt-safe and assumes the region hash entry exists for in-flight writes.
- Flush failure prevents later regions from being marked clean because durability ordering is uncertain.
- `recovery_in_flight` includes an extra reference during prepare to avoid racing stop-recovery.
- Destroy requires no quiesced regions and no pending I/O in remaining hash entries.

## Test Focus

Test clean-to-dirty-to-clean transitions, nosync marking after failed writes, flush failure effects, delayed bios for recovering regions, recovery semaphore start/stop behavior, failed recovery with handled/unhandled errors, dirty-log callback errors, hash allocation races, suspend wait ordering, and destroy assertions with pending/quiesced regions.
