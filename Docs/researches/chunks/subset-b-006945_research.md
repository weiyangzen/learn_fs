# sources/distributed-fs/ceph/src/osd/PrimaryLogPG.cc lines 1-8766

## Scope

This chunk covers the first 8,766 lines of Ceph's `PrimaryLogPG.cc`, the core implementation for primary placement-group request handling in the classic OSD. The range starts with includes, callback helpers, recovery hooks, object wait/blocking logic, admin/listing PG operations, request admission, client op dispatch, tier-cache and manifest handling, proxy/promote/refcount paths, transaction execution, backfill/snap-trim support, and the first major part of low-level OSD operation execution through rollback setup. The file continues after line 8766, so this chunk stops while `_do_rollback_to()` is still updating the in-memory `object_info_t` from the rollback source.

## Purpose

Within this range, `PrimaryLogPG` acts as the PG-facing coordinator for:

- admitting OSD messages only when map, peering, active, readable, and flush conditions allow them;
- routing client object operations to the primary, read-capable replica, objecter proxy path, recovery wait queue, or cache-tier promotion path;
- building `OpContext` transactions, executing requested `OSDOp`s, and deciding whether to reply immediately, record an error in the PG log, or submit replicated writes through `RepGather`;
- maintaining object context state, locks, dirty ranges, clean-region tracking, snapsets, manifest metadata, cache-tier state, and PG/object stats;
- integrating recovery and backfill notifications with wait queues and OSD stats;
- implementing read, write, xattr, omap, watch/notify, tmap, copy, manifest, tier flush/evict/promote, delete, and rollback operation semantics.

This code is not a standalone API layer. It is a dense integration point between client-visible RADOS semantics, peering/recovery state, the backing object store, `PGBackend`, object-class execution, cache-tier machinery, scrub/snap trimming, and the OSD messenger/objecter.

## Important APIs, Types, and Helpers

- `PrimaryLogPG::OpContext` is the central per-operation mutable state. In this chunk it tracks the original `OpRequest`, request id, `OSDOp` vector, object contexts, lock manager, current/new object state, generated `PGTransaction`, snap context, log entries, callback lists, async read finishers, return data, clean regions, modified ranges, byte/read/write counters, and user/internal versions.
- `PrimaryLogPG::CopyCallback` defines completion for copy/promote/copy-from workflows. `CopyFromCallback`, `PromoteCallback`, and `PromoteManifestCallback` adapt copy completion into either `execute_ctx()` re-entry, `finish_copyfrom()`, `finish_promote()`, or error/requeue handling.
- `BlessedGenContext`, `UnlockedBlessedGenContext`, and `BlessedContext` wrap callbacks with a captured OSD map epoch and drop completion if the PG has reset since the callback was issued. Locked wrappers reacquire the PG lock before completion.
- Recovery callbacks `C_OSD_AppliedRecoveredObject`, `C_OSD_CommittedPushedObject`, and `C_OSD_AppliedRecoveredObjectReplica` bridge ObjectStore transaction apply/commit events to PG recovery bookkeeping.
- Proxy operation records `ProxyReadOp` and `ProxyWriteOp` are driven here by `do_proxy_read()`, `finish_proxy_read()`, `do_proxy_write()`, and `finish_proxy_write()`. They issue objecter operations to the base/target pool and later synthesize normal client replies.
- Manifest/refcount helpers use `ManifestOp`, `RefCountCallback`, `C_SetManifestRefCountDone`, `C_SetDedupChunks`, `inc_refcount_by_set()`, `dec_refcount*()`, and `refcount_manifest()` to keep dedup/chunk references coherent when setting, unsetting, dirtying, rolling back, trimming, or deleting manifest objects.
- `ReadFinisher`, `C_ChecksumRead`, `C_ExtentCmpRead`, `FillInVerifyExtent`, and `ToSparseReadResult` make erasure-coded async reads re-enter `do_osd_ops()` as if the read sub-operation completed inline.
- `OpFinisher` instances stored by subop number make multi-stage operations idempotent across `-EINPROGRESS` re-entry, notably copy-from, tier promote, set-redirect reference acquisition, set-chunk reference acquisition, checksums, extent comparisons, and async reads.

## Admission and Request Control Flow

`do_request()` is the top-level message gate for this range. It first preserves per-source map ordering via `waiting_for_map`, requests newer OSD maps when needed, and discards requests that are stale or otherwise invalid. It then applies PG-level RADOS backoff support for capable sessions when the PG is down, incomplete, peering, or not active enough to serve object operations. If the PG is not peered, only `PGBackend::can_handle_while_inactive()` messages are passed through; other requests wait on `waiting_for_peered`. If peered but recovery needs a flush, requests wait on `waiting_for_flush`.

Once peered and flushed, `PGBackend::handle_message()` gets first chance to consume backend-specific messages. Remaining messages are dispatched by type:

- `CEPH_MSG_OSD_OP` and object-level `CEPH_MSG_OSD_BACKOFF` require active state; OSD ops additionally require cache-pool feature support and then enter `do_op()`.
- `MSG_OSD_PG_SCAN`, `MSG_OSD_PG_BACKFILL`, and `MSG_OSD_PG_BACKFILL_REMOVE` drive backfill scan/progress/removal handling.
- scrub reservation/replica scrub messages are delegated to scrubber paths.
- missing-log update messages are delegated to peering/recovery handlers defined elsewhere.

`do_op()` decodes the `MOSDOp`, serializes optimized EC object-class calls through a single coroutine lane when `should_use_coroutine()` says the pool allows EC optimizations and the op includes `CEPH_OSD_OP_CALL`, and otherwise calls `do_op_impl()` directly. While a coroutine op is active, subsequent ops wait in `waiting_for_coro_op` and are requeued by `on_coroutine_complete()`.

`do_op_impl()` is the main client-op admission pipeline. It checks PG containment for the target head, session object backoffs, unsupported parallel execution, derived op info, direct-read incompatibilities, primary/replica routing rules, laggy/wait readability, caps, object name/key/namespace length limits, backing-store key validity, blocklist state, full/failsafe-full/EIO pool flags, invalid writes to snapshots, max write size, unreadable or degraded target state, EC direct-read local missing state, scrub write blocks, snap rollback/degraded/unreadable blockers, duplicate in-progress writes, and injected EC read errors before it ever creates an `OpContext`.

The object-context lookup phase handles `LIST_SNAPS` snapdir rules, blocked head objects, replica-read conflict checks, `find_object_context()`, snapset context loading, unreadable/degraded clones, hit-set update/persistence, tier-agent decisions, adjacent clone recovery for manifest/chunked operations, manifest redirection/chunk proxying, cache-tier miss handling, ENOENT/copy-get special cases, locator consistency warnings, object-level blocks, lock acquisition, lost-object reads, and read-only ENOENT replies. Only then does it allocate `OpContext`, acquire/skip locks, set cache-ignore flags, and call `execute_ctx()`.

## Recovery, Missing Object, and Wait Queues

`on_local_recover()` updates snap mapping for recovered clone objects, handles the `LOST_REVERT` case where the recovered version must be advanced to the revert log entry version, marks active pushes, calls `recovery_state.recover_got()`, updates primary-side object context state, registers ObjectStore apply/commit callbacks, publishes stats, releases object backoffs, and wakes unreadable waiters when the recovered object becomes readable.

`on_global_recover()` records that an object recovered on all replicas, publishes stats, drops recovery read markers, removes `backfills_in_flight` and `recovering` entries, finishes the recovery op, releases backoffs, requeues degraded/unreadable waiters, and calls both `finish_degraded_object()` and `finish_unreadable_object()`.

`maybe_kick_recovery()` checks `missing_loc` for a specific object and, if it is not already recovering or unfound, opens a backend recovery handle and chooses between `recover_missing()`, replica delete preparation, or replica push preparation. `wait_for_unreadable_object()` and `wait_for_degraded_object()` both call this helper before parking the request and incrementing delayed-op metrics.

Degraded classification is subtle. `is_degraded_or_backfilling_object()` treats an object as degraded if it is already in the degraded wait map, locally missing, missing on non-async recovery targets, or within an in-flight backfill range. Missing objects on async recovery targets are intentionally not treated as blocking in that path. `is_degraded_on_async_recovery_target()` exists for cases that still need to notice async-target degradation, such as rollback and some write blockers.

Write-specific blockers include full cache (`objects_blocked_on_cache_full` and `waiting_for_cache_not_full`), clean/primary-repair waits, snap rollback promotion blocks, degraded snap blocks, unreadable snap blocks, and generic blocked-object waits. `maybe_await_blocked_head()` and `wait_for_blocked_object()` tie these blockers back to object-context `start_block()`/`stop_block()` use.

## PG Admin and Listing Operations

`do_command()` implements admin/asok-style PG commands for this chunk. `query` dumps snap trim queue, peering state, recovery state, scrubber state, and tier agent state. `log` dumps the PG log. `mark_unfound_lost` validates mode, primary role, unfound state, and source probing before scheduling `mark_all_unfound_lost()`. `list_unfound` optionally decodes a JSON object offset, streams bounded missing/unfound records, and asks `PeeringState::QueryUnfound` to append source-location data. Scrub commands delegate to `PrimaryLogScrub` for forced, abort, scheduled, and debug actions.

`do_pg_op()` handles PG/object listing and hit-set operations embedded in `MOSDOp`s. `PGLS` and `PGNLS` merge backend object listing results with PG-log missing entries so recently missing-but-log-visible objects appear consistently. They skip snaps, deleted missing entries, wrong namespaces, internal hit-set namespace where appropriate, and class/plain filters. Filter construction is done by `get_pgls_filter()`, which either creates `PGLSPlainFilter` or resolves `class.filter` through `ClassHandler`.

`do_scrub_ls()` decodes `scrub_ls_arg_t`, validates same-interval state, and asks the scrubber's store-error cache for results, returning `-EAGAIN` for interval mismatch or `-ENOENT` if the scrubber store is unavailable.

## Object Locks and Context Lifetime

`get_rw_locks()` maps op ordering and read/write behavior to `RWState::RWREAD`, `RWWRITE`, or `RWEXCL`. EC reads that can overtake writes are forced to exclusive locking in write-ordered contexts. If a head context is needed for a missing/new clone, the snapdir/head lock is acquired before the clone lock to preserve ordering.

`release_object_locks()` asks `ObcLockManager` for requests to requeue and flags for recovery or snap trimming. It queues recovery or sends `TrimWriteUnblocked()` as needed. Requests blocked by active scrub go to the front of `waiting_for_scrub`; others are requeued normally.

`close_op_ctx()` releases locks, drops the transaction, runs registered finish callbacks, clears coroutine active context if applicable, and deletes the context. This is the common cleanup path for errors, requeues, async cancellation, and successful contexts that are not handed to a `RepGather` finish lambda.

## Cache Tier, Proxy, Promotion, and Manifest Control Flow

`maybe_handle_manifest_detail()` processes existing manifest objects before normal execution. Redirect manifests proxy reads or writes to the target unless the op ignores redirect or is a manifest/tier metadata op. Chunked manifests proxy eligible data reads through chunk objects if all requested chunks are represented and marked missing; otherwise they may block on degraded/scrub/laggy states or promote the object if any manifest chunks are missing.

`maybe_handle_cache_detail()` handles cache-tier misses based on `pg_pool_t::cache_mode`:

- `WRITEBACK` promotes mandatory misses, proxies writes/reads when allowed, blocks when the agent marks the cache full, and may promote based on hit-set recency.
- `READONLY` promotes missing reads but redirects writes to the base tier.
- `PROXY`/deprecated `FORWARD` proxy reads/writes unless promotion is mandatory.
- `READPROXY`/deprecated `READFORWARD` proxy reads but promote/write back for writes or mandatory promotion.

`maybe_promote()` enforces hit-set recency and OSD promote throttling before calling `promote_object()`. `promote_object()` blocks on scrub/laggy conditions, creates an object context for missing objects, chooses source object/locator based on normal cache miss vs redirect/chunk manifest, sets copy-from flags that ignore overlay/cache and preserve map-snap behavior, starts the copy, marks the object blocked, optionally waits the triggering op on that blocked object, and increments promotion stats.

`do_proxy_read()` and `do_proxy_write()` convert an original op into an objecter operation against the base tier or redirect target with `IGNORE_CACHE`/`IGNORE_OVERLAY`. Reads stash mutable op results in `ProxyReadOp`; writes stash an `OpContext` for reply state in `ProxyWriteOp`. Completion validates the tracked tid/object, removes the op from `in_progress_proxy_ops`, increments tier proxy counters, and either builds a read completion context or sends an ACK+ONDISK write reply.

`do_proxy_chunked_op()` decomposes a client extent read into per-chunk reads using the manifest `chunk_map`; `do_proxy_chunked_read()` creates one objecter read per chunk and `C_ProxyChunkRead` copies returned chunk data into the correct offset within the original op's outdata. `can_proxy_chunked_read()` is intentionally narrow: only normal/sync reads are accepted, and every requested byte must be covered by manifest chunks marked missing.

Cancellation paths (`cancel_proxy_read()`, `cancel_proxy_write()`, `cancel_proxy_ops()`, `cancel_manifest_ops()`) mark operations canceled, collect objecter tids for cancellation by the caller, clear output where needed, and optionally requeue original client ops. Their correctness depends on completion callbacks checking both canceled state and `last_peering_reset`.

## Manifest Refcount and Dedup State

Manifest chunk/reference management is visible throughout this chunk:

- `refcount_manifest()` issues `cas.chunk_get_ref`, `cas.chunk_put_ref`, or `cas.chunk_create_or_get_ref` object-class mutations through the objecter against the target chunk object, using the source object's mtime and `IGNORE_CACHE | IGNORE_OVERLAY | RWORDERED` flags.
- `get_adjacent_clones()` and `get_prev_clone_obc()` derive neighbor clone object contexts from the snapset so reference deltas can be computed relative to adjacent clone manifests.
- `inc_refcount_by_set()` computes reference increments/decrements for `SET_CHUNK` or rollback-to-manifest changes. Positive increments are issued before the manifest is updated and block the source object until callbacks complete; negative decrements are deferred until local commit.
- `dec_refcount_by_dirty()`, `update_chunk_map_by_dirty()`, and `dec_all_refcount_manifest()` clean up references when dirty writes remove clean chunk mappings, whole manifest objects are removed, redirects with references are unset, or snap trimming/rollback deletes manifest-bearing objects.
- `recover_adjacent_clones()` and `do_recover_adjacent_clones()` block manifest/chunk operations when adjacent clones needed for reference math are unreadable.

The main risk here is reference-count skew: any early return, cancellation, peering reset, dirty-region miscalculation, or adjacent-clone lookup failure around manifest operations can leak or prematurely drop CAS chunk references. The code mitigates this by blocking objects during in-flight increments, making decrement work commit callbacks, requiring adjacent clone readability, and storing per-subop finishers for re-entry.

## Transaction Execution and Replication

`execute_ctx()` is designed to be idempotent because async reads, copy-from, set-manifest refcount, and promotion callbacks can re-enter it. Each pass resets observed state from the object context, creates a fresh `PGTransaction`, sets snap context and version for writes/cache ops, preserves `user_at_version`, traces prepare timing, and calls `prepare_transaction()`.

If `prepare_transaction()` returns `-EINPROGRESS` or queues async reads, execution pauses. EC async reads are started via `OpContext::start_async_reads()`, and `finish_read()` later pops `in_progress_async_reads` and re-enters `execute_ctx()`. `-EAGAIN` closes the context after the operation has queued itself elsewhere.

For read-only, empty-transaction, or error-without-log-update paths, `execute_ctx()` runs side effects when appropriate and calls `complete_read_ctx()`. For write/cache paths it prepares a `MOSDOpReply`, bounds returnvec output size, updates trim targets, optionally checks debug op ordering, and either:

- records an `ERROR` pg-log entry through `record_write_error()` for `update_log_only` outcomes, preserving duplicate detection and return vectors; or
- registers commit/success/finish callbacks, creates a `RepGather`, calls `issue_repop()`, evaluates completion with `eval_repop()`, and lets later commit callbacks send ACK+ONDISK replies and log stats.

`record_write_error()` appends an `ERROR` log entry with a new version and request id, optional op-return vector, then calls `submit_log_entries()` with an on-complete closure that sends the original reply. This preserves duplicate write/error semantics even when no data transaction is applied.

## Backfill and Snap Trimming

`do_scan()` handles replica scan digest requests and responses. On `OP_SCAN_GET_DIGEST`, it checks backfill-full state, scans a bounded range via `scan_range_replica()`, and replies with encoded interval objects. On `OP_SCAN_DIGEST`, the primary decodes the peer's interval, preserves ordering in `peer_backfill_info`, and finishes the recovery op once all backfill peers have responded.

`do_backfill()` handles finish/progress/ack messages. Progress updates are persisted via `recovery_state.update_backfill_progress()` in an ObjectStore transaction. Finish messages also send `OP_BACKFILL_FINISH_ACK` and queue `RecoveryDone()`. Finish acks on the primary complete the max-object recovery op.

`do_backfill_remove()` removes snap-mapped objects listed by the primary and adjusts local/PG byte stats for remote-backfilling targets before queueing the removal transaction.

`trim_object()` prepares the transaction for trimming one clone from a snapset. It validates clone/head contexts and snapset consistency, computes remaining snaps after removed snap filtering, obtains snaptrimmer write locks on the clone and head, assigns versions, updates snap mappings, deletes the clone or modifies its `clone_snaps`, updates overlap/clone byte/object/whiteout/dirty/omap/cache/manifest stats, decrements manifest references when needed, may remove an unneeded whiteout head, writes updated `SS_ATTR`/`OI_ATTR`, and returns a prepared `OpContextUPtr`. `kick_snap_trim()`, `snap_trimmer_scrub_complete()`, and `snap_trimmer()` drive the state machine only when primary/active/clean conditions and osdmap flags allow.

## Low-Level OSD Ops in This Chunk

`do_osd_ops()` iterates the request's `OSDOp` vector, tracks subop index and processed count, retrieves any stored `OpFinisher`, traces pre/post events, marks user-visible modifications, normalizes legacy truncate encoding, munges tail-zero into truncate where safe, executes the op, stores per-op `rval`, honors `FAILOK` except for `-EAGAIN`/`-EINPROGRESS`, and stops at first hard error.

Read paths:

- `do_read()` trims reads to object/truncate size, supports EC direct local reads, EC sync/coroutine reads, EC async reads with checksum verification, replicated sync reads, full-object data-digest verification, primary repair on `-EIO`, and read stats.
- `do_sparse_read()` trims extents, emulates sparse read with normal async read for EC when direct read is not used, or asks the store for fiemap and reads extents through `objects_readv_sync()`. It also verifies full-object digests when applicable.
- `do_checksum()` validates chunk alignment, parses checksum init values, supports EC async reads, and `finish_checksum()` emits count plus checksum bytes for xxhash32, xxhash64, or crc32c.
- `do_extent_cmp()` trims to the visible extent, reads sync or EC async, and `finish_extent_cmp()` returns `0` on equality or `-MAX_ERRNO - index` for the first mismatch.
- `STAT`, `ISDIRTY`, xattr/omap getters, omap comparisons, list watchers, list snaps, copy-get, tmap-get, and object-class `CALL` are all handled in this switch with class capability enforcement for object-class reads/writes.

Write/data paths:

- `WRITE` handles input length, write fadvise flags, aligned-append pools, truncate sequence races, max object size, create-on-write, zero-length write semantics, transaction write/truncate calls, data digest maintenance, size/usage stats, modified ranges, and clean-region dirty marking.
- `WRITEFULL`, `WRITESAME`, `ZERO`, `TRUNCATE`/`TRIMTRUNC`, `DELETE`, `CREATE`, `APPEND`, `STARTSYNC`, `TMAPPUT`, `TMAPUP`, `TMAP2OMAP`, omap setters/removers, xattr setters/removers, cache pin/unpin, and watch mutation paths update transactions and stats directly or through recursive `do_osd_ops()` calls.
- `CACHE_FLUSH`, `CACHE_TRY_FLUSH`, `CACHE_EVICT`, `TIER_FLUSH`, `TIER_EVICT`, and `TIER_PROMOTE` integrate cache-tier state with object locks, dirty state, manifest state, pinned/watcher constraints, promotion/copy callbacks, and tier counters.
- `SET_REDIRECT`, `SET_CHUNK`, and `UNSET_MANIFEST` update manifest metadata, clear object data/omap where needed, manage reference flags, and use async reference increments before metadata changes when the op requests reference accounting.
- `COPY_FROM` and `COPY_FROM2` decode source locator/snap/version/truncate details, reject self-copy, start copy via `start_copy()`, and resume through `CopyFromFinisher`.

Legacy tmap support remains in this range. `do_tmapup()` implements an optimized sorted update path after reading the full tmap object, falling back to `do_tmapup_slow()` for unsorted input. `do_tmap2omap()` reads the tmap header/value stream, truncates object data, writes an omap header, and sets omap values.

## Rollback and Delete Semantics

`_delete_oid()` decides whether deletion should produce a whiteout based on cache mode and clone/snapset state. It removes object data, marks data and omap regions dirty, updates write/byte/object/clone/whiteout/pinned/manifest stats, disconnects watchers, clears or resets `object_info_t`, and schedules manifest reference decrements unless creating a whiteout. The distinction between `no_whiteout` and `try_no_whiteout` is important for cache eviction and clone safety.

`_verify_no_head_clones()` rejects cache eviction of a head while any clone exists, is missing, or has a pending promote/copy operation.

`_rollback_to()` finds the target snapshot object, blocks on missing/degraded/unreadable clones, ensures adjacent manifest clones are readable for correct chunk reference math, forces promotion/proxy handling when rollback requires cache/manifest materialization, deletes the head if the target snapshot is absent/whiteout and there are no watchers, or prepares to clone the snapshot back to the head. If rolling back to a chunked manifest, it may first increment needed chunk references asynchronously with an `OpFinisher`.

`_do_rollback_to()` begins by removing current head data, decrementing current manifest references if any, cloning the rollback source to the head, adding the rollback object context to the transaction, computing modified ranges by intersecting clone overlaps from the rollback snapshot forward, and then updating cached object context size, bytes, clean regions, and data/omap digests. The chunk ends at line 8766 before this helper completes all object-info field copying and transaction/log details.

## State and Persistence Behavior

Persistent state modified in this range includes:

- ObjectStore transactions for data writes, truncates, zeroing, deletes, clones, creates, attr/xattr mutations, omap mutations, snap-mapper updates, allocation hints, and backfill progress.
- Object metadata attributes `OI_ATTR` and `SS_ATTR`, plus snap mapper updates through `t->update_snaps()` and recovery-local `snap_mapper.add_oid()`.
- PG log entries for normal writes through later `prepare_transaction()`/`issue_repop()` flow, explicit `ERROR` entries in `record_write_error()`, snap trim `DELETE`/`MODIFY` entries, and version/user-version tracking in replies.
- In-memory state maps/lists such as `recovering`, `backfills_in_flight`, `waiting_for_*` queues, `objects_blocked_on_*`, `proxyread_ops`, `proxywrite_ops`, `manifest_ops`, `in_progress_proxy_ops`, `in_progress_async_reads`, `object_contexts`, and `snapset_contexts`.
- PG stats and perf counters including object counts, dirty/omap/whiteout/pinned/manifest counts, byte counts, read/write kb/op counters, tier proxy/promote/evict/whiteout counters, delayed-op counters, and dynamic perf stats.
- Object-level durable semantic state in `object_info_t`: size, truncate sequence/size, data/omap digests, flags, watchers, manifest data, user version, mtime, allocation hints, and dirty/cache-pin/whiteout/lost state.

Many mutations are intentionally deferred to commit callbacks. Examples include manifest decrement calls after dirty/removal changes, reply sending after replicated commit, watch/notify side effects after success, and object cleanup on finish. This protects client-visible behavior from local prepare-only changes that might not commit.

## Dependencies and Integration Points

This chunk depends heavily on:

- `PG`, `PeeringState`, `recovery_state`, and PG state flags for peering, active/clean/readable/laggy/wait, missing-loc, pg-log, backfill, and recovery op state.
- `PGBackend` for object reads, async EC reads, recovery operations, backfill scans, omap iteration, and backend-specific inactive message handling.
- `OSDService`/`OSD` for map requests, messenger sends, objecter operations, ObjectStore transaction queueing, perf counters, throttles, config, cluster/client connections, and repair helpers.
- `ObjectStore` and `PGTransaction` for persistent mutations.
- `ClassHandler` and object-class method/filter execution, including CAS chunk refcount methods.
- `PrimaryLogScrub` and snap-trimmer state machine for scrub/write blocking and snap trim orchestration.
- RADOS protocol structures such as `MOSDOp`, `MOSDOpReply`, `OSDOp`, `MOSDPGScan`, `MOSDPGBackfill`, `MOSDBackoff`, `object_locator_t`, `hobject_t`, `SnapContext`, and snap/list response encodings.
- Cache-tier agent state, hit sets, objecter read/mutate APIs, and base/overlay pool fields (`tier_of`, `cache_mode`, flags).

## Risks and Edge Cases

- The request admission pipeline has many early returns that queue, reply, proxy, or drop requests. Missing one cleanup path can leak locks, contexts, blocked objects, objecter tids, or delayed ops.
- Async operation re-entry relies on `execute_ctx()` and `do_osd_ops()` idempotence plus correct `op_finishers` indexing. A subop order change or missing finisher erase can repeat non-idempotent work such as copy-from or refcount increments.
- Manifest/chunk reference accounting spans snap clones, dirty ranges, rollback, trim, delete, and async objecter mutations. Incorrect adjacent clone recovery, dirty-region marking, or commit-callback ordering can leak references or delete shared chunks too early.
- Cache-tier modes mix proxying, promoting, redirecting, dirty flush, whiteout delete, pinned objects, and hit-set recency. Behavior differs substantially by mode and by whether the object already has a redirect/chunk manifest.
- EC read behavior differs among direct, sync/coroutine, and async paths. Digest verification and read-length mutation are intentionally different to avoid recursive-op breakage; regressions here can corrupt reply lengths or miss checksum failures.
- Duplicate write handling depends on PG-log versions and `waiting_for_ondisk`. Error paths after Kraken record log entries for duplicate detection, which means changing error handling can alter client retry semantics.
- Read/list operations merge store state with PG-log missing/deleted state. Incorrect ordering or filtering in PGLS/PGNLS can expose deleted objects, hide missing-but-log-visible objects, or return invalid handles.
- Whiteout decisions in `_delete_oid()` interact with cache tiering and clones. Deleting vs whiteouting the wrong head can break later read-through, clone visibility, or eviction safety.
- `do_request()` and completion callbacks rely on `last_peering_reset`/epoch checks. Missing these checks in new async paths can complete operations after a PG interval reset.

## Test Signals

Useful validation signals for this chunk include:

- RADOS object read/write/create/delete/truncate/zero/append/writefull/writesame tests, including max object size and truncate-sequence race cases.
- EC pool tests for direct read, sync optimized read, async read, checksum, extent-compare, sparse-read emulation, and injected read-error repair.
- Cache-tier tests for writeback/proxy/readproxy/readonly modes, cache full blocking, hit-set promotion thresholds, dirty flush, try-flush, evict with pinned/watcher/clone constraints, whiteouts, and duplicate proxied replies.
- Manifest/dedup tests for set-redirect, set-chunk, unset-manifest, chunked read proxying, tier-promote/evict/flush, rollback to/from chunked manifests, snap trim with manifest clones, and CAS refcount correctness under cancellation/requeue.
- Recovery/backfill tests that verify unreadable/degraded waits wake on local/global recovery, async recovery targets do not unnecessarily block ordinary writes, backfill scan progress persists, and backfill removes adjust stats.
- PG listing/admin tests for `pgls`, `pgnls`, class filters, namespace filtering, hit-set get/list, `list_unfound`, `mark_unfound_lost`, and scrub debug commands.
- Watch/notify tests for watch, reconnect, ping timeout, unwatch, list-watchers, object delete disconnects, and notify/ack side effects.
- Snap tests for `LIST_SNAPS`, rollback to missing/degraded/unreadable clones, snap trim lock contention, clone overlap/size/snaps consistency, and whiteout head removal after final clone trim.
- Fault-injection tests around peering reset while proxy/copy/refcount/async-read operations are in flight, ensuring callbacks are dropped or requeued and objecter tids are canceled.
