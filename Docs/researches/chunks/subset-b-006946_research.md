# sources/distributed-fs/ceph/src/osd/PrimaryLogPG.cc lines 8767-16309

## Scope

This chunk covers the back half of `PrimaryLogPG.cc`, starting in object rollback/snapshot materialization helpers and ending at intrusive reference helpers. It includes the primary OSD write finalization path, copy-from/promote/flush/dedup flows for cache tiering and manifests, object and snapset context lookup, watcher maintenance, replicated operation commit tracking, log-entry-only updates, recovery and backfill scheduling, hit-set persistence, cache-tier agent decisions, scrub/snap-trim integration, and erasure-code attribute-cache helpers.

The code is stateful and primary-role centric. Most functions assume the PG lock is held, mutate `OpContext`, `ObjectContext`, `SnapSetContext`, `recovery_state`, or PG queues, and bridge between client operations, local `PGTransaction`s, peer recovery messages, and asynchronous objecter callbacks.

## Purpose

This section turns prepared OSD operations into durable PG log entries and replicated object-store transactions, while also handling the lifecycle machinery that makes those operations safe: snapshot clone creation, dirty/clean cache-tier state, object copy and promotion, dedup manifest reference accounting, watcher disconnects, recovery/backfill pulls and pushes, object context caching, and cleanup on peering changes.

It also owns several autonomous primary-side background workflows. Recovery and backfill use it to repair primary or replica missing objects. Cache tiering uses it to flush dirty objects to a base tier and evict cold clean objects. Hit-set code records object access history used by the tiering agent. The snap trimmer state machine coordinates asynchronous snap removal with scrub, clean-state, local reservation, object locks, and repop completion.

## Important APIs, Types, and Functions

`make_writeable()`, `_make_clone()`, `write_update_size_and_usage()`, `truncate_update_size_and_usage()`, `prepare_transaction()`, and `finish_ctx()` are the write-finalization core. They validate snap contexts, run OSD ops, create clone objects when a head is modified under snapshots, update `object_info_t`, `SnapSet`, object statistics, clean-region metadata, and append `pg_log_entry_t` records before the transaction is submitted.

`do_osd_op_effects()`, `complete_disconnect_watches()`, `get_watchers()`, `populate_obc_watchers()`, `check_blocklisted_watchers()`, and `handle_watch_timeout()` maintain watch/notify state. They create and connect `Watch` objects from persisted `object_info_t::watchers`, start notifies, process notify acks, disconnect timed-out or blocklisted watchers, and persist watcher removal as a normal object modification.

`do_copy_get()`, `start_copy()`, `_copy_some()`, `_copy_some_manifest()`, `process_copy_chunk()`, `process_copy_chunk_manifest()`, `_write_copy_chunk()`, `finish_copyfrom()`, `finish_promote()`, `finish_promote_manifest()`, `cancel_copy()`, and `cancel_copy_ops()` implement object copy-from and cache-tier promote. They exchange `object_copy_data_t` chunks over objecter reads, copy attrs/data/omap/reqids, verify optional digests, use temp objects for multi-chunk copies, handle redirect and chunked manifests, and unblock the destination object when the copy completes or is canceled.

`start_dedup()`, `do_cdc()`, `get_fpoid_from_chunk()`, `finish_set_dedup()`, and `finish_set_manifest_refcount()` implement distributed dedup for chunked manifests. They content-define chunks with `CDC`, derive fingerprint object IDs using configured SHA algorithms, issue refcount operations into the dedup tier, and finally replace object manifests and register old-reference drops after commit.

`start_flush()`, `finish_flush()`, `try_flush_mark_clean()`, `cancel_flush()`, and `cancel_flush_ops()` implement cache-tier flush. They copy dirty objects to the base pool, enforce snap ordering and older-clone cleanliness, optionally enter the dedup path, join or cancel concurrent flushes, clear `FLAG_DIRTY`, mark chunked-manifest chunks missing/clean as needed, and requeue waiting flush requests.

`start_cls_gather()`, `cancel_cls_gather()`, and `cancel_cls_gather_ops()` run class-method gather operations against objects in another pool and resume the original `OpContext` when all objecter reads return.

`new_repop()`, `issue_repop()`, `repop_all_committed()`, `eval_repop()`, `op_applied()`, `remove_repop()`, `simple_opc_create()`, `simple_opc_submit()`, `submit_log_entries()`, `cancel_log_updates()`, `already_complete()`, and `apply_and_flush_repops()` own replicated operation lifecycle. They allocate `RepGather`s, submit `PGTransaction`s to `pgbackend`, track projected logs, run success/commit/finish callbacks in order, satisfy duplicate waiters, and cleanly abort or requeue in-flight operations on interval changes.

`create_object_context()`, `get_object_context()`, `find_object_context()`, `object_context_destructor_callback()`, `add_object_context_to_pg_stat()`, `get_snapset_context()`, `put_snapset_context()`, `kick_object_context_blocked()`, and `requeue_op_blocked_by_object()` manage in-memory object and snapset contexts. They decode `OI_ATTR` and `SS_ATTR`, cache erasure-code attrs, map snap IDs to clone objects, maintain snapset refcounts, and unblock operations waiting for object promotion, copy, scrub, or recovery.

`recover_missing()`, `remove_missing_object()`, `finish_degraded_object()`, `finish_unreadable_object()`, `_committed_pushed_object()`, `_applied_recovered_object()`, `_applied_recovered_object_replica()`, `on_failed_pull()`, `pick_newest_available()`, `do_update_log_missing()`, `do_update_log_missing_reply()`, `mark_all_unfound_lost()`, `_clear_recovery_state()`, `cancel_pull()`, `start_recovery_ops()`, `recover_primary()`, `primary_error()`, `prep_object_replica_deletes()`, `prep_object_replica_pushes()`, and `recover_replicas()` coordinate normal recovery. They pull missing objects to the primary, push valid primary objects to replicas, delete objects known removed, handle unfound/lost policy, and keep peer missing logs and last-complete-on-disk state consistent.

`recover_backfill()`, `prep_backfill_object_push()`, `update_range()`, `scan_range_primary()`, `scan_range_replica()`, `earliest_peer_backfill()`, `all_peer_done()`, and `check_local()` implement backfill scanning and object movement. They compare local and peer backfill intervals, request replica scans, push missing or wrong-version objects, send deletion lists, advance peer `last_backfill`, and validate local stray deletion under debug settings.

`hit_set_setup()`, `hit_set_create()`, `hit_set_apply_log()`, `hit_set_persist()`, `hit_set_trim()`, `hit_set_remove_all()`, `hit_set_in_memory_trim()`, `get_hit_set_current_object()`, and `get_hit_set_archive_object()` implement hit-set object lifecycle. They build and persist Bloom or other hit-set types, archive and trim history objects in the hit-set namespace, update `pg_hit_set_history_t`, and load recent archives for cache-agent eviction decisions.

`agent_setup()`, `agent_clear()`, `agent_work()`, `agent_load_hit_sets()`, `agent_maybe_flush()`, `agent_maybe_evict()`, `agent_stop()`, `agent_delay()`, `agent_choose_mode_restart()`, `agent_choose_mode()`, and `agent_estimate_temp()` implement the cache-tier agent. They list objects, skip unsafe candidates, choose flush/evict modes from dirty/full ratios, schedule flushes, evict cold clean objects, and adjust OSD-level agent queue participation by effort.

`do_replica_scrub_map()`, `_range_available_for_scrub()`, `rep_repair_primary_object()`, `maybe_preempt_replica_scrub()`, and `get_eclistener()` provide scrub and repair integration. The snap trimmer nested states `NotTrimming`, `WaitReservation`, and `AwaitAsyncWork` gate trim work on primary/active/clean state, scrub inactivity, reservations, and object write locks.

`setattr_maybe_cache()`, `setattrs_maybe_cache()`, `rmattr_maybe_cache()`, `getattr_maybe_cache()`, `getattrs_maybe_cache()`, and `get_internal_versions()` abstract attribute access. On erasure-coded pools, attrs can come from `ObjectContext::attr_cache`; public attrs are stored with a leading underscore during copy and stripped on reads.

## Control Flow

The write path starts with `prepare_transaction()`. It rejects invalid `SnapContext`, calls `do_osd_ops()`, records log-only errors for write requests on modern releases, handles read-only or no-op writes, enforces pool-full policy, calls `make_writeable()` for head objects, selects `MODIFY`, `DELETE`, or `REPLACE`, and delegates to `finish_ctx()`.

`make_writeable()` snapshots the old head when a write modifies an object covered by newer snapshots. It creates a clone object at `snapc.seq`, copies user bits, version, dirty/omap/pinned/manifest flags, builds clone overlap, increments stats, adds a `CLONE` log entry, and advances `ctx->at_version`. It then subtracts modified ranges from the newest clone overlap so clone byte accounting remains correct.

`finish_ctx()` is the final mutation checkpoint. It drops dedup references for dirty chunked manifests when appropriate, assigns user and object versions, writes `OI_ATTR` and `SS_ATTR`, appends the primary log entry including per-op return codes and clean regions, moves extra reqids into the log, and applies `ctx->new_obs` and `ctx->new_snapset` back to the cached object context.

Copy-from control flow is callback driven. `start_copy()` blocks the destination `ObjectContext`, cancels any earlier copy for that destination, then starts either `_copy_some()` for normal/redirect objects or `_copy_some_manifest()` for chunked manifests. `_copy_some()` issues objecter `copy_get` reads, optionally with snap listing. `process_copy_chunk()` validates the tid, accumulates data and omap digests, writes partial chunks to a temp object when the cursor is incomplete, reissues reads until complete, verifies source digests, and returns a `fill_in_final_tx` closure to the copy callback. Manifest copy instead fans out reads for chunk objects and, once all complete, writes the chunks into the manifest object and logs `PROMOTE`.

Flush control flow starts by checking that older clones are clean or recoverable, then either deduplicates chunked/forced-dedup objects or sends a base-tier `copy_from`/remove operation with enforced snap context. `finish_flush()` handles objecter completion and calls `try_flush_mark_clean()`. That function verifies the object was not modified after the copied `user_version`, handles scrub lock conflicts and opportunistic eviction, takes a write lock, clears dirty state, updates chunked manifests, logs `CLEAN`, requeues joined requests, and submits the repop.

Recovery scheduling in `start_recovery_ops()` is staged. It first marks local recovery complete if there is no local missing set, recovers replicas if the primary is complete or all primary missing objects are unfound, then recovers primary missing objects, then may run backfill if recovery is drained and reservations/cluster flags allow it. When nothing remains, it clears recovery/backfill states and posts the next peering event.

`recover_primary()` walks missing objects in version order from `last_requested`, handles `LOST_REVERT` by either locally relabeling a known prior version or setting target locations for the old version, and calls `recover_missing()` unless the object or its head is already recovering. `recover_replicas()` orders peers by shortest missing list, skips objects beyond peer backfill cursors or still missing on the primary, and prepares deletes or pushes through `PGBackend::RecoveryHandle`.

Backfill control flow repeatedly reconciles a local `PrimaryBackfillInterval` with per-peer `ReplicaBackfillInterval`s. It scans local or peer ranges when intervals are empty, removes objects that exist only on peers, pushes objects missing or wrong-version on targets, tracks in-flight pushes and pending stat updates, advances `last_backfill`, and sends `OP_BACKFILL_PROGRESS` or `OP_BACKFILL_FINISH`.

Cache-agent control flow is a bounded object-list pass. `agent_work()` lists a small range from `agent_state->position`, skips hit-set namespace, degraded, missing, blocked, scrubbed, pending, and unsupported omap-to-EC objects, then tries eviction before flush depending on active modes and quota. It advances position, detects full hash-space wraps, decays temperature history, trims loaded hit sets, and either delays or recalculates mode.

`agent_choose_mode()` computes dirty and full ratios from PG stats, target bytes/objects, PG divisor, object overhead, hit-set objects, and EC-base omap limitations. It applies slop/hysteresis, selects low/high flush and some/full evict modes, quantizes evict effort, updates stats counters, and enables, disables, or adjusts OSD agent scheduling. Exiting full-evict mode requeues waiters blocked by cache pressure.

Snap trimming is a statechart. `NotTrimming` ignores work unless the PG is primary, active, clean, and has `snap_trimq`; it waits for scrub if needed. `WaitReservation` starts a trim after reservation if trimming is still allowed. `AwaitAsyncWork` queues work by average object size, fetches objects from `snap_mapper`, calls `trim_object()` up to the configured concurrency, submits each returned `OpContext`, and transitions to wait states until repops finish or locks clear. Completion erases the snap from trim queues, records purged snaps, writes PG info, shares it, and reposts `KickTrim`.

## State and Persistence Behavior

Object state persists through object data operations plus `OI_ATTR` and `SS_ATTR`. `finish_ctx()` encodes `object_info_t` and `SnapSet`, writes them into the `PGTransaction`, updates the cached `ObjectContext`, and records a `pg_log_entry_t` so replicas, recovery, duplicate detection, and rollback can reason about the mutation.

PG statistics are maintained incrementally in `object_stat_sum_t` deltas. This chunk adjusts counts for objects, bytes, writes, dirty objects, omap, whiteouts, cache-pinned objects, manifests, clones, hit-set archives, flushes, evictions, recovered/repaired objects, and flush/evict mode flags. `apply_stats()` also stores pending stat updates for objects in the active backfill window.

Snapshots persist in `SnapSet` clone vectors, clone sizes, clone snaps, and clone overlaps. `make_writeable()` adds clones and overlap ranges; `finish_promote()` may repair or remove clone entries when a promoted snap was trimmed; snap trimming writes purged-snap state through `recovery_state.adjust_purged_snaps()` and `write_if_dirty()`.

Copy and flush operations keep transient state in `copy_ops`, `flush_ops`, temp objects, objecter tids, blocked object contexts, and callback result structures. Successful copy/promote/flush state becomes durable only when the generated `PGTransaction` is submitted and committed through `RepGather`; failed multi-chunk copies delete partial temp objects.

Dedup manifests persist in `object_info_t::manifest` and external refcount objects in the configured dedup tier. `finish_set_dedup()` clears dirty state, sets `FLAG_MANIFEST` and `TYPE_CHUNKED` if needed, replaces the chunk map, and registers old reference decrements on commit so refcounts are not dropped before the manifest change is durable.

Recovery state is stored in `recovery_state`, PG log missing sets, peer missing maps, peer last-complete-on-disk, `recovering`, `backfills_in_flight`, `peer_backfill_info`, `backfill_info`, and `pending_backfill_updates`. `submit_log_entries()` persists log-only entries locally and sends `MOSDPGUpdateLogMissing` to peers, with `log_entry_update_waiting_on` holding the repop until all acknowledgments arrive.

Hit-set state persists as special objects in `osd_hit_set_namespace` plus `pg_hit_set_history_t` in PG info. `hit_set_persist()` writes an archive object with fabricated object metadata, logs a normal `MODIFY`, trims old archives with `DELETE` log entries, and updates in-memory agent hit-set maps.

Object and snapset context caches are local and discarded on interval changes. `get_object_context()` decodes attrs from disk when needed and caches attrs for EC pools; `context_registry_on_change()`, `clear_cache()`, `on_change()`, and `on_shutdown()` discard watchers, cancel callbacks, and clear object contexts so stale interval state is not reused.

## Dependencies and Integration Points

`PGBackend` is the main persistence and recovery backend. This chunk uses it for synchronous object reads, attr reads, omap iteration, transaction submission, ordered log updates, recovery handles, object pulls/pushes/deletes, range listing, recovery-source validation, and cleanup on peering changes.

`OSD` services provide objecter calls, client/cluster messaging, performance counters, cluster log messages, agent scheduling, reservations, queued recovery/scrub work, store transactions, and global maps. Objecter operations use `ObjectOperation`, `C_GatherBuilder`, `C_OnFinisher`, `MOSDPGUpdateLogMissing`, `MOSDPGScan`, `MOSDPGBackfill`, and `MOSDPGBackfillRemove`.

`PeeringState` and `recovery_state` provide PG log access, missing locations, peer info, stats updates, trim/commit markers, hset history updates, purged-snap updates, and peering event scheduling. Many transitions post `DoRecovery`, `RequestBackfill`, `AllReplicasRecovered`, or `Backfilled`.

`ObjectContext`, `SnapSetContext`, `object_info_t`, `SnapSet`, `OpContext`, `PGTransaction`, `RepGather`, `CopyOp`, `FlushOp`, `ManifestOp`, `Watch`, `Notify`, `HitSet`, `TierAgentState`, `CDC`, `ObjectCleanRegions`, and `ObcLockManager` are the dominant local types.

Scrub integration flows through `m_scrubber`: stats notification, write blocking checks, range availability checks, scrub callback queues, replica scrub maps, repair-required flags, and cleanup on interval changes. Snap trimming explicitly waits for scrub to be inactive.

Pool and OSD map settings influence many paths: erasure-coded versus replicated behavior, omap support, required alignment, cache mode and base tier, dedup tier and fingerprint algorithm, cache target ratios/ages, hit-set configuration, full flags, release gates, removed snaps, and cluster flags such as `NOBACKFILL` and `NOREBALANCE`.

## Risks and Edge Cases

The chunk mixes persistent mutations with asynchronous callback state. Most callbacks check `last_peering_reset` or epoch before touching the PG, but missed checks or stale objecter tids could complete work from a prior interval against new state.

`finish_ctx()` is a high-risk hub. It updates object metadata, snapset metadata, stats, log entries, dirty/chunked-manifest refcounts, reqid return codes, clean regions, and cached state. A missing stat delta, wrong log type, or omitted attr write can break recovery, duplicate detection, scrub, or cache-tier accounting.

Snapshot clone accounting is subtle. `make_writeable()` must preserve manifest references, dirty/omap/pinned flags, clone overlaps, clone sizes, and snap lists while also respecting incomplete clones. Incorrect overlap updates can corrupt reported bytes or cause flush/evict decisions to be wrong.

Copy-from and promote handle multiple object formats and partial progress. Risks include omap copied into pools without omap support, digest mismatches, temp-object leaks, copied attrs with underscore translation, redirect-manifest rename conflicts, source snap deletion during copy, and chunked-manifest reads completing out of order.

Dedup is constrained and brittle. `do_cdc()` reads the whole object synchronously and explicitly excludes EC pools as base tiers. Fingerprint object placement depends on the dedup tier's PG mapping. Reference increments are issued before the manifest switch and decrements are registered after commit; errors in this order can leak or prematurely delete chunks.

Flush semantics rely on user_version stability. If the object changes after the base-tier copy, `try_flush_mark_clean()` must fail and requeue. Concurrent nonblocking flushes, scrub write blocks, older dirty clones, base-tier omap incompatibility, and chunked-manifest cleanup all create special cases.

Recovery and backfill ordering has many invariants. The code asserts on unexpected missing/backfill combinations, uses `last_requested` only when no object was skipped, and distinguishes recovering primary objects, replica pushes, deletes, and peer scans. Errors here can strand PGs in recovery, lose deletes, or mark peer `last_backfill` too far forward.

Object context lookup returns `-EAGAIN`, `-ENOENT`, or success based on snap mapping, missing sets, degraded/backfilling state, removed snaps, and whether snap IDs should map to exact clones. Callers must interpret these carefully; treating `-EAGAIN` as absence can hide recoverable objects.

Cache-agent decisions depend on approximate stats and hit-set temperature. Invalid post-split stats disable the agent, EC base pools make omap objects unflushable, and full-evict mode can requeue waiters. Bad stats or stale hit sets can cause excessive flushing/eviction or insufficient cache pressure relief.

Hit-set persistence is skipped during degradation, scrub conflicts, or early backfill positions. Since hit sets share PG object ordering and are normal objects, their create/delete transaction can interfere with backfill if not delayed.

Snap trimming must only run while clean, primary, active, not scrubbing, and with reservation/work budget. It starts multiple repops and captures references to the state's `in_flight` set in callbacks; correctness depends on state lifetime and reset transitions.

Interval-change cleanup is broad. `on_change()` and `on_shutdown()` cancel copy, flush, proxy, manifest, cls gather, async reads, recovery, repops, log updates, watchers, backoffs, reservations, and object contexts. Missing a queue can leave stuck operations; overzealous clearing can drop a user op that should be requeued.

## Test Signals

Write-path tests should cover invalid snap contexts, read-only no-op writes, full-pool return behavior, log-only write errors, snapshot clone creation, dirty/undirty transitions, omap and manifest stat deltas, clean-region encoding, extra reqid logging, and duplicate return-code persistence.

Copy/promote tests should exercise normal, redirect-manifest, and chunked-manifest copy; multi-chunk temp object assembly; EC async reads; attrs and omap cursor pagination; omap unsupported destination errors; digest mismatch injection; snap deletion during copy; cancellation on interval change; and proxy op requeue after success.

Flush and dedup tests should cover dirty head and clone flush, older dirty clone rejection, whiteout removal flush, concurrent flush piggyback/cancel behavior, scrub-blocked nonblocking flush, version-change failure, chunked-manifest clean marking, forced dedup, CDC chunk generation, fingerprint algorithms, refcount failure, and old-reference decrement after commit.

Object context tests should cover cache hit/miss, missing attrs with and without `can_create`, corrupt `OI_ATTR` or `SS_ATTR`, EC attr-cache reads, snap ID to clone mapping, removed-snap filtering, missing/degraded clone `-EAGAIN`, and snapset refcount release on context destruction.

Watcher tests should cover reconnecting persisted watchers on activation, blocklisted watcher removal, notify start/ack dispatch, watch timeout delayed by degraded object or scrub, durable watcher attr removal, and disconnect callbacks after commit.

RepGather/log update tests should cover commit callback ordering, waiting-for-ondisk duplicate replies, aborted repops during `on_change()`, `submit_log_entries()` with multiple acting shards, peer update replies with unknown tids or wrong shards, and `already_complete()` behavior around uncommitted repops.

Recovery tests should cover primary missing pulls, deleted missing objects, unfound handling, lost delete/revert, local revert without pulling, failed pulls marking peer missing, replica delete and push preparation, async recovery targets ordering, missing head before snapped object, and recovery completion peering events.

Backfill tests should cover initial interval setup, local scan update from projected logs, peer scan requests, deleting peer-only objects, pushing missing and wrong-version objects, shard-specific versions, pending stat advancement with in-flight objects, `NOBACKFILL` and `NOREBALANCE` deferral, and final `OP_BACKFILL_FINISH`.

Hit-set and agent tests should cover hit-set disable cleanup, Bloom target sizing bounds, archive persist and trim, skipping degraded/scrubbed/backfill-overlapping archives, loading hit-set archives, temperature grading, flush/evict mode hysteresis, object skip reasons, full-evict requeues, and agent delay after a full pass with no work.

Scrub/snap-trim tests should cover replica scrub map ignored when scrub inactive, scrub range blocked by object context, repair marking primary object missing and entering recovery, snap trim blocked by scrub or unclean PG, reservation success, lock failure waiting, multiple in-flight trim repops, purged-snap persistence, and reset on trim errors.
