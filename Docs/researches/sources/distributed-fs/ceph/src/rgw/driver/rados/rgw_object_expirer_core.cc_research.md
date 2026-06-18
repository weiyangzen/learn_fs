# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_object_expirer_core.cc

## Purpose
Implements the RGW object expirer worker and its time-indexed hint store. It processes deletion hints created for objects that should expire at a future time, calls object-specific expiry handling, and trims processed hints from RADOS timeindex shards.

## Important APIs And Functions
Static helpers derive shard object names (`obj_delete_at_hint.%010u`), shard ids from object index keys, and key extensions containing tenant, bucket name/id, object name, and instance. `RGWObjExpStore::objexp_hint_add()` writes encoded `objexp_hint_entry` values with `cls_timeindex_add()`. `objexp_hint_list()` reads hints for a time range. `objexp_hint_trim()` trims processed timeindex entries, using `cls_timeindex_trim_repeat()` until `-ENODATA`.

`RGWObjectExpirer::garbage_single_object()` loads the bucket and calls `RadosObject::handle_obj_expiry()`. `garbage_chunk()` decodes listed hints and attempts deletion. `process_single_shard()` locks a shard, repeatedly lists chunks up to the configured chunk size, processes and trims them, and stops early when the configured interval budget is reached. `OEWorker::entry()` runs periodic rounds.

## Control Flow
Hints are added to a shard selected by bucket index hashing over object name plus instance, and stored in the zone log pool. The worker keeps `last_run`; each round records `start` and processes all shards for hints in `[last_run, start]`. If all shards complete, `last_run` advances to `start`; otherwise the next round retries the same interval. Each shard uses a cls lock named `gc_process` with duration equal to `rgw_objexp_gc_interval`, so concurrent RGWs skip shards already locked by another processor.

Within a shard, listing uses marker pagination and chunk size `rgw_objexp_chunk_size`. Any decoded entry attempts object expiry. `-ERR_PRECONDITION_FAILED` means the hint is stale or no longer applicable and is not treated as a hard failure. If any entries were inspected, the code trims from the previous marker to the returned marker across the time range.

## State And Persistence
Persistent state is the set of cls timeindex objects in the zone log pool, each keyed by expiry time and key extension with encoded hint data. Locks are stored on the shard objects through cls lock. Runtime state includes `last_run`, per-round `start`, markers, and the worker thread/down flag.

## Dependencies And Integration Points
Depends on `RGWObjExpStore`, SAL RadosStore/Driver, bucket loading, bucket index hashing, `cls/timeindex`, `cls/lock`, zone log pool, and `RadosObject::handle_obj_expiry()`. Configuration knobs include number of hint shards, chunk size, and GC interval.

## Risks And Edge Cases
`objexp_hint_parse()` logs decode errors but returns 0, so a corrupt hint can flow with default fields and should be watched. `process_single_shard()` uses `continue` on list errors inside the loop; without marker progress, repeated errors can spin until the time budget expires. Unlock is not guarded by RAII, so unexpected early returns after lock acquisition would risk waiting for lock expiry. Hints are trimmed even if object deletion failed with errors other than precondition failure, which can drop retry opportunities. Tests should validate stale hints, bucket missing, decode failures, lock contention, time-budget early exit, trim repeat behavior, and retry interval advancement.
