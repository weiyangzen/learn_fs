# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dedupe.c

## Purpose
Implements VDO write deduplication coordination around content hashes and the kernel UDS index. The file is centered on per-hash-zone `hash_lock` state machines that let concurrent `data_vio` writes with the same record name share one index lookup, one verified duplicate PBN lock, and one newly written copy when no duplicate exists. Deduplication is an optimization rather than a correctness requirement, so slow or unavailable index operations are deliberately timed out and the writes continue without dedupe.

## Important APIs, Types, And Functions
The public entry points are `vdo_make_hash_zones()`, `vdo_free_hash_zones()`, `vdo_start_dedupe_index()`, `vdo_resume_hash_zones()`, `vdo_drain_hash_zones()`, `vdo_finish_dedupe_index()`, `vdo_acquire_hash_lock()`, `vdo_continue_hash_lock()`, `vdo_release_hash_lock()`, `vdo_clean_failed_hash_lock()`, `vdo_share_compressed_write_lock()`, `vdo_get_duplicate_lock()`, `vdo_select_hash_zone()`, `vdo_get_dedupe_statistics()`, `vdo_dump_hash_zones()`, `vdo_message_dedupe_index()`, and the timer-tuning setters.

`struct hash_lock` is the internal state-machine object. It tracks the record name, registered map state, duplicate PBN and `pbn_lock`, lock agent, waiter queue, holder list, advice-update flags, verification status, and reference counts. Its states are `INITIALIZING`, `QUERYING`, `WRITING`, `UPDATING`, `LOCKING`, `VERIFYING`, `DEDUPING`, `UNLOCKING`, and `BYPASSING`.

`struct hash_zone` owns the lock map, lock pool, UDS request context pool, pending and available context lists, timeout funnel queue, timer, statistics, and completion for one hash-zone thread. `struct hash_zones` owns the shared UDS index session, global dedupe/index state, action manager, ratelimiter, timeout counters, and the array of zones.

`struct dedupe_context` wraps a UDS request so the file can time out a request without reusing the caller-visible request object before the UDS callback has actually returned.

## Control Flow
New writes enter through `vdo_acquire_hash_lock()` on the selected hash-zone thread. `acquire_lock()` either creates/registers a lock from the zone pool or returns the existing lock for the record name. Hash collisions are checked by comparing block data against an existing holder; on collision the write bypasses dedupe to prevent corruption.

The common no-duplicate path is `INITIALIZING -> QUERYING -> WRITING -> BYPASSING`. `start_querying()` launches `UDS_POST` when the agent already has an allocation, or `UDS_QUERY` otherwise. `finish_querying()` decodes UDS advice with `decode_uds_advice()` and either proceeds to `start_locking()` or writes a new block with `start_writing()`. `finish_writing()` records the just-written location as the verified duplicate for any waiters, starts a UDS update if advice changed, or exits.

The duplicate path is `QUERYING -> LOCKING -> VERIFYING -> DEDUPING -> UNLOCKING`. `lock_duplicate_pbn()` runs in the physical zone, rejects write locks and exhausted increment limits, acquires or attaches to a read PBN lock, and acquires a provisional reference for previously unheld candidate blocks. `start_verifying()` reads the candidate block, optionally decompresses it, compares the full VDO block with `blocks_equal()`, and `finish_verifying()` decides whether to dedupe or treat advice as stale. In `DEDUPING`, there is no exclusive agent; the agent and waiters are launched in parallel through `launch_dedupe()`.

When the duplicate PBN has no remaining reference increments, `fork_hash_lock()` replaces the registered lock with a new one and moves the current waiter set to it. The old lock continues cleanup and loses UDS update authority; the new lock writes a fresh copy and may update advice.

UDS query timeout flow is separate. `query_index()` gets a `dedupe_context`, puts it on the pending list, starts the zone timer, and calls `uds_launch_request()`. `finish_index_operation()` either requeues the requester to the hash zone or marks a timed-out context complete for later reuse. `timeout_index_operations_callback()` moves overdue pending contexts out of the pending list, clears the `data_vio` context pointer, continues those writes without dedupe, and reports rate-limited timeout statistics.

## State And Persistence
The dedupe index is persisted by UDS in the index region configured from `volume_geometry`; this file opens, creates, closes, suspends, resumes, and queries that index through `uds_*` APIs. Hash locks, contexts, wait queues, and timers are volatile runtime state. Duplicate PBN locks and provisional references protect on-disk block lifetimes while dedupe decisions are in flight, but the lock objects themselves are not persistent.

Index state is represented as `IS_CLOSED`, `IS_CHANGING`, or `IS_OPENED`, plus target state, `create_flag`, `dedupe_flag`, and `error_flag`. `vdo_start_dedupe_index()`, `vdo_message_dedupe_index()`, resume, and drain/suspend operations manipulate these fields under `zones->lock` and launch `change_dedupe_state()` on the dedupe thread.

## Dependencies And Integration Points
This file depends on VDO's thread/completion system, `data_vio` write path, physical-zone PBN locks, slab depot reference accounting, packer/compression callbacks, int-map hash tables, wait queues, action manager, admin states, statistics, and logger/memory helpers. External integration is with the UDS indexer API: `uds_create_index_session()`, `uds_open_index()`, `uds_launch_request()`, `uds_suspend_index_session()`, `uds_resume_index_session()`, `uds_close_index()`, `uds_get_index_session_stats()`, and `uds_destroy_index_session()`.

The DM target calls this through load/resume/suspend phases and dmsetup index messages. Data path integration comes from `data-vio.c`, which selects hash zones, acquires hash locks, continues locks after write/dedupe completion, and cleans failed locks.

## Risks
The main risk is state-machine correctness across asynchronous thread transitions. Most fields are only safe on the hash-zone thread, while UDS callbacks, physical-zone callbacks, CPU callbacks, bio completions, and timer completions race through explicit state transitions. A missed context state transition could reuse a UDS request too early or leave a data_vio waiting forever.

Physical reference accounting is high risk: stale advice, compressed-block slots, PBN write locks, provisional references, and increment-limit rollover must be handled exactly or dedupe can create leaks, premature frees, or data corruption. The hash collision fallback is essential because identical record names are not sufficient proof of identical data.

Timeout tuning affects performance more than correctness. Too short an interval suppresses useful dedupe; too long an interval can stall writes behind slow UDS operations. The header declares `vdo_get_dedupe_index_timeout_count()` but this source does not define it, so builds that reference it would fail unless the prototype is stale and unused.

## Test Signals
Useful tests include concurrent identical writes, hash collision injection, stale-advice cases, compressed-write dedupe, out-of-reference rollover, UDS timeout behavior, and suspend/resume while queries are pending. Runtime signals are stable `hash_lock` pool return assertions, no stuck waiters, increasing valid/stale advice counters, bounded `dedupe_advice_timeouts`, successful `index-enable`, `index-disable`, `index-close`, and `index-create` messages, and no PBN lock/refcount assertions during stress.
