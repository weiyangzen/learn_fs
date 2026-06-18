# File Research: sources/block-storage/kvdo/vdo/dedupe.c

## Purpose
Implements VDO’s deduplication coordination layer: hash zones, hash locks, UDS index query/update plumbing, duplicate verification, lock rollover, dedupe timeout handling, sysfs status, and administrative drain/resume.

## Module Model
The file’s design comment describes two coupled systems:
- Hash locks coordinate concurrent writes with identical hashes and allow them to dedupe together.
- UDS index queries are asynchronous and may time out, allowing writes to continue without dedupe.

## Key State Machines
### Hash Lock States
- `INITIALIZING`
- `QUERYING`
- `WRITING`
- `UPDATING`
- `LOCKING`
- `VERIFYING`
- `DEDUPING`
- `UNLOCKING`
- `BYPASSING`
- `DESTROYING`

A hash lock usually has one agent VIO except in `DEDUPING`, where all holders dedupe in parallel against a verified duplicate PBN lock.

### Dedupe Context States
- `IDLE`
- `PENDING`
- `TIMED_OUT`
- `COMPLETE`
- `TIMED_OUT_COMPLETE`

These manage UDS requests that may complete after VDO has already timed them out.

### Index States
- `IS_CLOSED`
- `IS_CHANGING`
- `IS_OPENED`

User-visible names include `closed`, `opening`, `online`, `offline`, `closing`, `error`, and `suspended`.

## Key Structures
- `struct hash_lock`: hash key, duplicate ring, reference counts, state, UDS update flag, verification flags, duplicate location/lock, agent, waiter queue.
- `struct dedupe_context`: UDS request wrapper, zone, requestor VIO, submission time, atomic state.
- `struct hash_zone`: per-zone hash lock map, lock pool, statistics, context lists, timer, completion, active query count.
- `struct hash_zones`: global manager, kobject, UDS parameters/session, ratelimit state, timeout counters, index/admin state, zone array.

## Hash Lock Flow
- `vdo_acquire_hash_lock()` obtains or shares a lock for a chunk name, after detecting possible hash collisions by comparing actual data.
- `vdo_enter_hash_lock()` dispatches based on lock state: starts query, waits, bypasses, dedupes, or reports invalid state.
- `start_querying()` posts or queries UDS using the agent.
- `finish_querying()` either starts locking/verifying returned advice or writes new data.
- `start_locking()` and `lock_duplicate_pbn()` acquire a read lock on candidate duplicate PBN advice.
- `start_verifying()` reads candidate data, decompresses if needed, and compares blocks.
- `finish_verifying()` marks advice valid/stale, claims reference increments, and transitions to dedupe or write.
- `start_writing()` sends an agent through compression/write path when no usable duplicate exists.
- `finish_writing()` makes the written location the verified duplicate and either dedupes waiters, updates UDS, unlocks, or exits.
- `start_deduping()` launches agent/waiters to dedupe in parallel against a verified duplicate lock.
- `finish_deduping()` releases individual holders or advances cleanup/update when the last holder remains.
- `start_updating()` updates UDS advice; `finish_updating()` cleans up after update.
- `start_unlocking()` and `finish_unlocking()` release duplicate PBN read locks and decide whether to re-lock, write, or destroy.
- `start_bypassing()` aborts dedupe for a lock and resumes ordinary compression/write path.

## Rollover Behavior
If a duplicate PBN lock has no remaining reference increments, `fork_hash_lock()` replaces the old lock in the hash map with a new lock. Remaining waiters move to the new lock, and the new agent writes a fresh copy. Only one lock updates UDS advice.

## UDS Index Handling
- Advice encoding uses version `2`, mapping state, and little-endian 64-bit PBN.
- `decode_uds_advice()` validates UDS result, rejects unmapped/zero/invalid PBN advice, and resolves the physical zone.
- `prepare_uds_request()` fills UDS request metadata for `UDS_POST` and `UDS_UPDATE`.
- `query_index()` acquires a dedupe context, starts timeout tracking, and launches `uds_start_chunk_operation()`.
- `finish_index_operation()` handles completion before or after timeout.
- `acquire_context()` reuses available contexts or recycles timed-out contexts that later completed.

## Timeout Handling
- Default timeout interval: 5000 ms.
- Default minimum timer interval: 100 ms.
- `start_expiration_timer()` arms per-zone timer.
- `timeout_index_operations_callback()` scans pending contexts, moves expired ones to timed-out list, clears requestor context, and resumes VIO processing without dedupe.
- Timeout reports are ratelimited and included in statistics.

## Admin and Lifecycle
- `vdo_make_hash_zones()` allocates zones, initializes UDS index session, creates hash-zone threads, lock pools, context pools, and action manager.
- `vdo_free_hash_zones()` frees maps, lock arrays, action manager, UDS session, ratelimit state, and kobject or raw allocation depending on admin state.
- `vdo_drain_hash_zones()` suspends UDS index then drains all zones.
- `vdo_resume_hash_zones()` resumes index and zones unless read-only.
- `vdo_start_dedupe_index()` opens/enables index, optionally creating it.
- `vdo_message_dedupe_index()` handles `index-close`, `index-create`, `index-disable`, and `index-enable`.
- `vdo_add_dedupe_index_sysfs()` creates the `dedupe/status` sysfs node.

## Statistics and Diagnostics
- Tracks valid/stale advice, concurrent data matches, hash collisions, current queries, UDS index stats, and dedupe advice timeouts.
- `vdo_dump_hash_zones()` logs UDS index state and active hash locks.
- `vdo_select_hash_zone()` maps the first byte of chunk name to a zone using multiply/shift scaling.

## Concurrency Notes
Hash lock transitions are confined to the owning hash-zone thread. Dedupe context and timer state use atomic compare-and-swap because UDS callbacks, timers, and zone completions can race.
