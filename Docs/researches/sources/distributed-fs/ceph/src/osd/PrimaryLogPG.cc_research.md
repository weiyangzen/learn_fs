# Research: sources/distributed-fs/ceph/src/osd/PrimaryLogPG.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006945`: lines 1-8766, `Docs/researches/chunks/subset-b-006945_research.md`
- `subset-b-006946`: lines 8767-16309, `Docs/researches/chunks/subset-b-006946_research.md`

## Chunk Research

### subset-b-006945: lines 1-8766

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

### subset-b-006946: lines 8767-16309

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
