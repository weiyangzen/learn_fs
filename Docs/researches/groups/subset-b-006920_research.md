# Research Group subset-b-006920

This grouped report covers the Ceph MDS files assigned to `subset-b-006920`. Each file section is bounded by reconciliation markers and preserves the original source path in the section title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Server.h -->
# sources/distributed-fs/ceph/src/mds/Server.h

Purpose: Declares the central CephFS MDS `Server` class that dispatches client, peer, session, reconnect, metadata mutation, xattr, snapshot, and recall operations for an `MDSRank`.

Important APIs and types: `Server::dispatch`, `handle_client_request`, `dispatch_client_request`, `respond_to_request`, `journal_and_reply`, and `submit_mdlog_entry` form the request/journal/reply surface. Session recovery APIs include `handle_client_session`, `reconnect_clients`, `handle_client_reconnect`, `prepare_force_open_sessions`, `finish_force_open_sessions`, `flush_client_sessions`, reclaim helpers, `recall_client_state`, and `force_clients_readonly`. Namespace mutation APIs cover open/create/truncate, mkdir/mknod/symlink, link/unlink/rmdir, rename, snapshot operations, snapdiff, and blockdiff. `RecallFlags` is a bitmask enum for steady recall, max enforcement, trimming, and liveness enforcement.

Control flow: Incoming `Message` objects are categorized into client session, client request/reply, peer request/reply, reclaim, reconnect, and OSD-map update paths. Client operations resolve and lock paths through helpers such as `rdlock_path_pin_ref`, `rdlock_path_xlock_dentry`, `rdlock_two_paths_xlock_destdn`, and `try_open_auth_dirfrag`, then use operation-specific handlers. Mutating operations build `EMetaBlob`/`EUpdate` journal payloads and only reply once the journal context is safe.

State and persistence behavior: The header owns pointers to `MDSRank`, `MDCache`, `MDLog`, `PerfCounters`, and `MetricsHandler`; reconnect state (`client_reconnect_gather`, denied set, timers), feature bitsets, throttles, and laggy-client state are in-memory control state. Durable changes are delegated to mdlog events, session map versions, inode table versions, and snapshot/table events. The xattr handler table centralizes validation and mutation of projected xattr maps before journaling.

Dependencies and integration points: Integrates with MDS cache objects (`CInode`, `CDentry`, `CDir`), client messages (`MClientRequest`, `MClientSession`, `MClientReconnect`, `MClientReclaim`), peer messages (`MMDSPeerRequest`), journal events (`EMetaBlob`, `EUpdate`), `SessionMap`, `SnapRealm`, `OSDMap`, `MetricsHandler`, and perf counters.

Risks: The class is a high-blast-radius coordinator: lock ordering, peer prepare/commit/rollback sequencing, projected inode/xattr state, and reconnect/session state must stay consistent. Xattr validation has policy risk because it distinguishes Ceph virtual xattrs from allowed user-settable Ceph-prefixed xattrs. Feature gating is critical for layout namespace support, vxattrs, charmap, and snapshot trace formats.

Test signals: Exercise client request families, replay of peer updates, forced session open/close, reconnect denial/finish, xattr validation paths, cap recall throttling, old/new client feature negotiation, and OSD-full handling. Regression tests should include rename/link/rmdir rollback and snapshot operations crossing multiple MDS ranks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SessionMap.cc -->
# sources/distributed-fs/ceph/src/mds/SessionMap.cc

Purpose: Implements MDS session tracking, OMAP-backed persistence, legacy load migration, perf counters, request-load accounting, completed-request writeback, and session filtering.

Important APIs/functions: `SessionMap::load`, `_load_finish`, `load_legacy`, `_load_legacy_finish`, `save`, `_save_finish`, `save_if_dirty`, `mark_projected`, `mark_dirty`, `replay_dirty_session`, `replay_open_sessions`, `add_session`, `remove_session`, `set_state`, `touch_session`, `Session::check_access`, `notify_recall_sent`, `notify_cap_release`, and `SessionFilter::parse/match`.

Control flow: `load()` reads the sessionmap object's OMAP header and batched values using `Objecter`; `_load_finish()` decodes the header once, decodes value batches until `more_session_vals` is false, rebuilds `by_state`, and completes waiters. Missing OMAP header triggers legacy full-object loading, after which all sessions are marked dirty so the next save writes the OMAP format. `save()` writes the version header, dirty session keys, and removed session keys; it may truncate the old object data after legacy import.

State and persistence behavior: The durable store is object `mds<rank>_sessionmap` in the metadata pool with OMAP header `version` and per-session OMAP values keyed by entity name. `version`, `projected`, `committing`, and `committed` enforce journal/writeback ordering. `dirty_sessions` and `null_sessions` determine which OMAP values are set or removed. `save_if_dirty()` can persist dirty completed request/flush lists ahead of normal sessionmap version writeback.

Dependencies and integration points: Uses `MDSRank`, `Objecter`, `Finisher`, `MDCache`, `Capability`, `CDentry`, `CInode`, `MDSAuthCaps`, `PerfCounters`, and config keys such as `mds_sessionmap_keys_per_op`, `mds_session_metadata_threshold`, and decay rates. It calls `MDSRank::evict_client` when session metadata exceeds threshold.

Risks: The code aborts or damages the rank on corrupt sessionmap reads. `mark_projected` and `mark_dirty` must occur in the same global order; mismatches assert via projected versions. Large client metadata causes eviction/blocklisting. Legacy decode contains an old-format branch with delicate duplicate-session recovery. `Session::check_access` has subtle path handling for stray/snapshotted deleted directories.

Test signals: Cover OMAP load pagination, missing-header legacy upgrade, corrupt header/value handling, dirty/null key save batches, threshold eviction, completed-request preemptive saves, config-change decay reset, session filter parser errors, and replay of force-open sessions across versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SessionMap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SessionMap.h -->
# sources/distributed-fs/ceph/src/mds/SessionMap.h

Purpose: Defines `Session`, `SessionFilter`, `SessionMapStore`, and `SessionMap`, the core in-memory and durable representation of client/MDS sessions.

Important APIs/types: `Session` exposes state transitions (`STATE_CLOSED`, `OPENING`, `OPEN`, `CLOSING`, `STALE`, `KILLING`), preallocated inode delegation, completed request/flush tracking, cap/lease LRU lists, recall counters, access checks, and connection metadata. `SessionMapStore` provides encode/decode/dump for session state outside a live MDS. `SessionMap` adds live indices, load/save, version projection/commit, replay helpers, perf counters, and dirty writeback.

Control flow: A session begins closed, moves through open/opening/stale/closing/killing, and can have an independent `importing_count`. `SessionMap::mark_projected()` advances a projected version and stores it on the session; `mark_dirty()` later advances committed sessionmap version and pops the expected projection. `SessionFilter` parses admin-socket style selectors by id, state, auth name, metadata, or reconnecting status.

State and persistence behavior: `session_info_t info` is the durable session payload, including inst, metadata, completed requests, flushes, and preallocated inos. Ephemeral fields include connection, request list, cap/lease LRU, decay counters, waiters, and `human_name`. `SessionMap` tracks `by_state`, `dirty_sessions`, `null_sessions`, `commit_waiters`, `waiting_for_load`, and average birth time.

Dependencies and integration points: Depends on Ceph entity/session types, `interval_set`, `MDSAuthCaps`, `DecayCounter`, `Message`, `Mutation`, and MDS context/gather helpers. It is consumed by `Server`, journal replay events (`ESession`, `ESessions`, `EMetaBlob` inode allocation fields), reconnect, cap recall, and admin session operations.

Risks: Refcount/list invariants are strict; the destructor asserts the session is off state lists. Preallocated inode intervals must remain consistent across `pending_prealloc_inos`, `free_prealloc_inos`, `delegated_inos`, and durable `info.prealloc_inos`. Completed request trimming controls idempotency; premature trimming can duplicate client operations.

Test signals: Unit/dencoder coverage should include session encode/decode, state names, dirty completed request flags, prealloc delegation/take paths, projected-version asserts, filter parsing, and `SessionMapStore::generate_test_instances`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SessionMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SimpleLock.cc -->
# sources/distributed-fs/ceph/src/mds/SimpleLock.cc

Purpose: Implements the non-inline behavior for MDS `SimpleLock`, including lazy unstable state allocation, xlock ownership, wait/cap shift mappings, cache tracking, dumping, and printing.

Important APIs/functions: `more`, `try_clear_more`, `get_xlock`, `set_xlock_done`, `put_xlock`, `get_xlock_by`, `dump`, `get_wait_shift`, `get_cap_shift`, `get_cap_mask`, `add_cache`, `remove_cache`, `get_active_caches`, and `_print`.

Control flow: The lock allocates `unstable_bits_t` only when gather sets, wrlocks, xlocks, exclusive clients, or lock caches are needed. `get_xlock()` asserts valid states, pins the parent with `PIN_LOCK`, records the mutation/client owner, and increments xlock count. `set_xlock_done()` clears mutation ownership and moves non-local locks to `LOCK_XLOCKDONE`. `put_xlock()` decrements count, unpins the parent, clears owner fields at zero, and frees unstable bits if empty.

State and persistence behavior: The state machine state is stored on `SimpleLock`; unstable fields are in-memory. `dump()` omits fully sync/unlocked locks, reducing diagnostic noise. The encode/decode behavior is declared in the header and persists state plus gather set for replay/rejoin rather than lock holder refs.

Dependencies and integration points: Relies on `MDSCacheObject` pin/waiter APIs, `MutationImpl`, `locks.h` state constants, `MDLockCache`, and Ceph cap bit constants. Wait shifts map lock types into reserved high bits of `MDSCacheObject::waitmask_t`.

Risks: Incorrect state assertions in xlock paths indicate protocol violations. Wait-shift or cap-mask mistakes can wake wrong waiters or grant incorrect caps. Lazy unstable cleanup must not drop active cache items or lock holders. `get_active_caches()` filters invalidating caches, so invalidation state changes need care.

Test signals: Cover xlock lifecycle for local and non-local locks, `LOCK_XLOCKDONE` transition, cache add/remove, waiter shift uniqueness for every lock type, cap mask/shift mappings, and dencoder round trips for sync and non-sync states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SimpleLock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SimpleLock.h -->
# sources/distributed-fs/ceph/src/mds/SimpleLock.h

Purpose: Defines the MDS metadata lock abstraction used by dentries, inodes, scatter locks, file locks, local locks, and cap permission derivation.

Important APIs/types: `LockType` maps Ceph lock IDs to state-machine tables (`sm_simplelock`, `sm_scatterlock`, `sm_filelock`, `sm_locallock`). `SimpleLock` defines wait masks, state/action/type names, lease/rdlock/wrlock/xlock APIs, gather-set APIs, cache APIs, state encode/decode, replica/rejoin helpers, cap calculation helpers, and formatter/print support.

Control flow: State-machine tables determine whether clients or auth MDS can lease/read/rdlock/wrlock/xlock. Waiters are translated into parent-object waiter bits via lock-specific shifts. Auth locks initialize gather sets from replicas for distributed state transitions; replica import/export helpers remove gather participants and decide when a transition has completed.

State and persistence behavior: Durable/replayable state is `state` plus gather set. Local pinning state (`num_rdlock`, `num_wrlock`, `num_xlock`, xlock owner, exclusive client, caches) is transient. `set_state_rejoin()` marks locks needing recovery when a replica survived an auth failover with non-sync state.

Dependencies and integration points: Depends on `MDSCacheObject`, `locks.h`, `MutationImpl`, Ceph cap constants, `MDLockCache`, and MDS waiter contexts. It is foundational for cache authority, replica coherence, capability issuance, and journal replay of locked metadata.

Risks: `WAIT_XLOCK` and `WAIT_STABLE` intentionally share the same bit, so callers must use them consistently. Capability grants vary by auth/replica/loner/xlocker state; bugs can produce stale cache permissions. Replica state export/rejoin is sensitive to auth failover and unsafe request replay.

Test signals: Validate state/action/type string coverage, every lock type's state-machine pointer, cap grants under auth/replica/loner/xlocker modes, gather removal during export/import, rejoin recovery marking, and encode/decode compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SimpleLock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SnapClient.cc -->
# sources/distributed-fs/ceph/src/mds/SnapClient.cc

Purpose: Implements the MDS table client cache for the global snapshot table, including query refresh, sync, prepare requests, commit notifications, and snapshot lookup/filtering.

Important APIs/functions: `resend_queries`, `handle_query_result`, `handle_notify_prep`, `notify_commit`, `prepare_create`, `prepare_create_realm`, `prepare_destroy`, `prepare_update`, `refresh`, `sync`, `get_snaps`, `filter`, `get_snap_info`, `get_snap_infos`, and `dump_cache`.

Control flow: `refresh()` sends a full-table query with the cached version and optionally records waiters by desired version. `handle_query_result()` decodes either an up-to-date marker or a full table payload, updates cached live and pending maps, advances last-created/destroyed sequences, clears committed tids, and releases waiters once synced and sufficiently fresh. Notify-prep messages reuse query decoding and send a notify ack.

State and persistence behavior: `SnapClient` itself is a cache; authoritative persistence is in `SnapServer`/`MDSTableServer` journaled state. The cache tracks live snaps, pending update/destroy records, committing tids, version waiters, sync request id, and last create/destroy sequence overlays so readers see local committing transactions.

Dependencies and integration points: Uses `MMDSTableRequest`, `MDSTableClient`, `MDSRank`, `MDSMap`, `SnapInfo`, and `SnapRealm`. `SnapRealm` calls `get_snaps`, `filter`, and `get_snap_infos` to compute inherited realm snapshots.

Risks: Snapshot visibility relies on overlaying `committing_tids` in sorted order. If sync request ids are mishandled after resend or server-ready transitions, waiters may complete too early or stall. Cache APIs assert `cached_version > 0`, so callers must sync before use.

Test signals: Cover full and up-to-date query replies, notify prep/ack, resend after reconnect, create/destroy/update prepares, pending transaction overlay, sync waiters, dump refusal before sync, and filtering around simultaneously pending create and destroy tids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SnapClient.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SnapClient.h -->
# sources/distributed-fs/ceph/src/mds/SnapClient.h

Purpose: Declares the snapshot `MDSTableClient` specialization used by non-table-server MDS ranks to prepare snapshot table mutations and maintain a local cache.

Important APIs/types: Public methods cover table protocol hooks (`resend_queries`, `handle_query_result`, `handle_notify_prep`, `notify_commit`), mutation prepares (`prepare_create`, `prepare_create_realm`, `prepare_destroy`, `prepare_update`), synchronization (`refresh`, `sync`, `wait_for_sync`, `is_synced`), sequence accessors, snapshot set filtering, info lookup, and cache dumping.

Control flow: Callers prepare a table transaction, receive a table tid and optional reply buffer, and later observe commit notifications. Cache refresh waits are keyed by target version. `sync()` forces a query and marks the client unsynced until the reply for that request id or newer arrives.

State and persistence behavior: The class stores `cached_version`, last-created/destroyed sequences, `cached_snaps`, pending update/destroy maps, committing tids, version waiters, and sync status. No direct persistent I/O happens here; persistence is table-server journal state.

Dependencies and integration points: Inherits from `MDSTableClient` with `TABLE_SNAP`, depends on `snap.h`/`SnapInfo`, and is consumed by `Server` snapshot handlers and `SnapRealm` cache construction.

Risks: Header-level invariants require callers not to use cached snap data before sync. Pending destroy stores both removed snap and resulting sequence, which must remain aligned with server semantics. `wait_for_sync()` asserts unsynced state.

Test signals: Mock table-server replies should validate cache version, wait-for-version completion, mutation buffer encoding, and last sequence accessors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SnapClient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SnapRealm.cc -->
# sources/distributed-fs/ceph/src/mds/SnapRealm.cc

Purpose: Implements snapshot realm inheritance, cache rebuilding, snap context/trace generation, snap name resolution, realm split/merge, and parent adjustment.

Important APIs/functions: `build_snap_set`, `check_cache`, `get_snaps`, `get_snap_context`, `get_snap_info`, `get_snapname`, `resolve_snapname`, `adjust_parent`, `split_at`, `merge_to`, `get_snap_trace`, `get_snap_trace_new`, `build_snap_trace`, and `prune_past_parent_snaps`.

Control flow: `check_cache()` recomputes cached state when local sequence, global last-destroyed, last-modified, or change-attr moves forward. `build_snap_set()` combines local snaps, filtered past-parent snaps, and current parent snaps since `current_parent_since`. `build_snap_trace()` emits old and new trace formats, appending parent traces for inheritance. Split/merge operations move child realms and inodes-with-caps across realm boundaries.

State and persistence behavior: Persistent realm data lives in `srnode` on the inode. Cached fields (`cached_seq`, `cached_snaps`, `cached_snap_context`, trace bufferlists, subvolume ino, modified/change attrs) are derived and invalidated via `invalidate_cached_snaps` or sequence checks. Split/merge updates in-memory realm topology and cap ownership; durable changes come from journaling the inode's projected srnode through `EMetaBlob`.

Dependencies and integration points: Integrates with `MDCache`, `MDSRank::snapclient`, `CInode`, `CDentry`, `CDir`, `Capability`, `SnapInfo`, `SnapRealmInfo`, and `SnapRealmInfoNew`. `Server` uses traces for client snap notifications.

Risks: Parent inheritance is subtle for global realms, past parents, snapdir visibility, and long snapshot names. Split traversal reserves based on `CDir::count()` and relies on `is_ancestor_of`; stale topology can misplace caps. Cache invalidation must include destruction sequence and change attrs, not only creation.

Test signals: Cover local/global realm cache builds, parent changes, past-parent pruning, old/new trace encoding, long-name resolution, split/merge with open children and caps, subvolume inheritance, and snapshots deleted while realms still reference past parents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SnapRealm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SnapRealm.h -->
# sources/distributed-fs/ceph/src/mds/SnapRealm.h

Purpose: Defines `SnapRealm`, the MDS cache object that represents a snapshot namespace boundary and derives visible snapshots for inodes beneath it.

Important APIs/types: The class exposes snap existence, parent pruning, snap set/context/info access, trace access, snap name resolution, parent adjustment, split/merge, cap membership tracking, and cache invalidation. Core persistent data is `sr_t srnode`; in-memory topology is `parent`, `open_children`, `inodes_with_caps`, and `client_caps`.

Control flow: Users call accessors such as `get_snaps`, `get_snap_context`, `get_last_created`, or `get_newest_seq`; these funnel through `check_cache()` to rebuild derived state lazily. Cap add/remove functions maintain per-client lists for efficient client snap notifications during realm changes.

State and persistence behavior: `srnode` is journaled as inode metadata. Cached derived fields are mutable so const accessors can rebuild them lazily. `global` distinguishes the global snap realm from ordinary inode-rooted realms. `cached_subvolume_ino`, modified time, and change attr make new snap trace generation sensitive to subvolume and visibility metadata.

Dependencies and integration points: Includes `Capability`, `mdstypes`, `snap.h`, `xlist`, `elist`, and common snap types. Used by `CInode`, `MDCache`, `Server`, `SnapClient`, and stray purge/truncate logic to obtain snap contexts.

Risks: `remove_cap` assumes the cap item is singular when erasing the map entry and asserts map consistency. Cache consumers must call `invalidate_cached_snaps()` after mutating realm relationships or srnode fields. Parent pointers are raw and require lifecycle discipline with inode cache objects.

Test signals: Validate cap list membership, lazy cache refresh, split/merge topology, global realm behavior, and trace buffer stability across repeated reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SnapRealm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SnapServer.cc -->
# sources/distributed-fs/ceph/src/mds/SnapServer.cc

Purpose: Implements the authoritative MDS snapshot table server, including mutation prepare/commit/rollback, client query/notify, OSD snapshot purge tracking, state reset, encode/decode, and forced repair.

Important APIs/functions: `reset_state`, `encode_server_state`, `decode_server_state`, `_prepare`, `_get_reply_buffer`, `_commit`, `_rollback`, `_server_update`, `_notify_prep`, `handle_query`, `check_osd_map`, `can_allow_multimds_snaps`, `handle_remove_snaps`, `dump`, `generate_test_instances`, and `force_update`.

Control flow: `_prepare()` decodes table ops: create allocates a new snap id or records a realm-create noop, destroy bumps `last_snap` as a sequence and records `(removed_snap, seq)`, and update records new metadata. `_commit()` moves pending creates/updates into `snaps`, removes destroyed snaps, updates last-created/destroyed, and adds snap ids/sequences to per-pool `need_to_purge`. `_rollback()` drops pending state. Queries return up-to-date or full table snapshots.

State and persistence behavior: The table-server encoded state includes `last_snap`, `snaps`, `need_to_purge`, pending update/destroy/noop maps, `last_created`, `last_destroyed`, and `snaprealm_v2_since`. `MDSTableServer` journals table operations; `_server_update()` persists removal from `need_to_purge` after OSD/monitor acknowledgement.

Dependencies and integration points: Uses `MDSTableServer`, `MMDSTableRequest`, `MRemoveSnaps`, `OSDMap`, `Objecter`, `MonClient`, `MDSMap`, and `SnapInfo`. `SnapClient` consumes query/notify payloads; monitors receive `MRemoveSnaps` for OSD data pool purge.

Risks: `last_snap` doubles as allocation counter and realm sequence, so destroy must bump it even though no new snapshot is created. Purge state includes both removed snap and destroy sequence per data pool. Multi-MDS snapshots are allowed only when no old-format realms remain. Legacy decode has older pending-destroy format conversion.

Test signals: Cover create/update/destroy prepare/commit/rollback, noop realm create, full/up-to-date queries, notify prep payloads, OSD map purge detection, monitor remove-snaps acknowledgements, upgrade format, forced update reset, and legacy decode versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SnapServer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SnapServer.h -->
# sources/distributed-fs/ceph/src/mds/SnapServer.h

Purpose: Declares the snapshot `MDSTableServer` specialization that owns global snapshot ids, live `SnapInfo` records, pending table mutations, and snap purge state.

Important APIs/types: Public methods include constructors, `handle_remove_snaps`, `reset_state`, `upgrade_format`, `check_osd_map`, `can_allow_multimds_snaps`, encode/decode/dump, `generate_test_instances`, and `force_update`. Overridden protected methods implement table-server state encoding, prepare/reply/commit/rollback, server update, notify prep, and query handling.

Control flow: Clients submit table mutations through the base table protocol; the server prepares pending changes by tid, notifies clients, commits or rolls back, and serves cache refresh queries. OSD-map checks reconcile `need_to_purge` against removed-snap state and monitor acknowledgements.

State and persistence behavior: Persistent fields are `last_snap`, `last_created`, `last_destroyed`, `snaprealm_v2_since`, `snaps`, `need_to_purge`, and pending maps. `last_checked_osdmap` is transient throttling state. `force_update()` can replace persistent state and reset the base table server if repair detects divergence.

Dependencies and integration points: Depends on `MDSTableServer`, `SnapInfo`, `MRemoveSnaps`, `MonClient`, and Ceph object ids. It is paired with `SnapClient` and feeds `SnapRealm` computations across ranks.

Risks: Header exposes direct table invariants: `upgrade_format()` asserts active state and `last_snap > 0`; callers must not run it before activation. `snaprealm_v2_since` gates multi-MDS snapshot behavior and must be upgraded once.

Test signals: Dencoder tests should include generated populated state, pending maps, purge maps, and force-update conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SnapServer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/StrayManager.cc -->
# sources/distributed-fs/ceph/src/mds/StrayManager.cc

Purpose: Implements asynchronous evaluation, truncation, purge, migration, and reintegration of MDS stray dentries/inodes.

Important APIs/functions: `eval_stray`, `_eval_stray`, `eval_remote`, `_eval_stray_remote`, `queue_delayed`, `advance_delayed`, `enqueue`, `_enqueue`, `purge`, `_purge_stray_purged`, `_purge_stray_logged`, `truncate`, `_truncate_stray_logged`, `reintegrate_stray`, `migrate_stray`, `activate`, and stray counter notifications.

Control flow: `_eval_stray()` only acts on auth stray dentries after startup. If `nlink == 0`, it prunes/purges stale snap data, checks directory snap parents, replication, leases, caps, recovery, and refcounts, then enqueues either a full purge or a HEAD truncate for files with old snap metadata. If links remain, `_eval_stray_remote()` tries to reintegrate into an auth remote dentry or migrates the stray to the remote authority.

State and persistence behavior: Purge data removal is enqueued to `PurgeQueue` before metadata cleanup is journaled with `EUpdate`. Full purge journals a null dentry and destroyed inode, applies mutation, unlinks/removes cache objects, and clears purging pins. Truncate purge journals zeroed size/max-size/client ranges but keeps the metadata so snap data remains valid. Counters track total, delayed, and enqueuing strays.

Dependencies and integration points: Uses `MDSRank`, `MDCache`, `MDLog`, `PurgeQueue`, `ScrubStack`, `SnapRealm`, `EUpdate`, `MClientRequest`, `BatchOp`, `CDir`, `CDentry`, and `CInode`. Reintegration and migration are expressed as internal rename client requests.

Risks: Refcount assertions intentionally abort on rogue references after purge. Directory stray purge waits for past parent snaps to disappear. Freezing dirs delay auth pin acquisition. Race comments around reintegration note that projected remote dentries must be rechecked in rename. Dirty-parent bits are cleared early to avoid backtrace writes during purge.

Test signals: Cover purge eligibility gates, delayed queue behavior, frozen dir retry, purge queue completion, full purge journal apply, truncate-then-reevaluate, remote reintegration, remote migration during shutdown, stale snap remote cleanup, and scrub-stack removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/StrayManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/StrayManager.h -->
# sources/distributed-fs/ceph/src/mds/StrayManager.h

Purpose: Declares the stray-management component consumed by `MDCache` to evaluate orphaned/unlinked metadata and either purge, truncate, migrate, or reintegrate it.

Important APIs/types: Public methods include `activate`, `eval_stray`, `queue_delayed`, `advance_delayed`, `eval_remote`, `migrate_stray`, stray count setters/getters, and create/remove notifications. `StrayEvalRequest` is an internal `MDSMetaRequest` wrapper that pins a dentry while an internal rename performs reintegration or migration.

Control flow: Callers can queue dentries for later evaluation when not inside another metadata operation. Remote dentries can trigger evaluation of their primary stray. Protected methods split the pipeline into evaluation, enqueue/retry, purge/truncate execution, completion, and reintegration/migration helpers.

State and persistence behavior: The manager itself stores in-memory queues/counters and a set of trimmed stray names. Persistent cleanup occurs through `PurgeQueue` plus mdlog updates in the implementation. `num_strays_enqueuing` marks dentries accepted for purge but not yet durably recorded by the queue.

Dependencies and integration points: Depends on `MDSMetaRequest`, `CDentry`, `PurgeQueue`, `MDSRank`, `CInode`, `MutationImpl`, and perf counters. Friend context classes are used for IO/log/context callback access.

Risks: The API assumes only started managers enqueue work. `StrayEvalRequest` manipulates `reintegration_reqid` and `PIN_PURGING`; leaks or duplicate requests would block future reintegration. Counters must be balanced across create/remove/enqueue/completion.

Test signals: Validate delayed list membership, request pin lifetime, counters, `started` gating, and public migration/evaluation entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/StrayManager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/balancers/greedyspill.lua -->
# sources/distributed-fs/ceph/src/mds/balancers/greedyspill.lua

Purpose: Implements a simple Lua MDS balancer policy that spills half of the local metadata load to the next rank when this rank is loaded and the neighbor is idle.

Important APIs/functions: Local functions `mds_load`, `when`, and `where` operate on the balancer-provided globals `mds`, `whoami`, and `BAL_LOG`. The returned `targets` table maps ranks to desired exported load amounts.

Control flow: The script initializes every rank target to zero, computes `mds[rank].load` from `all.meta_load`, logs selected metrics, checks whether `mds[whoami+1]` exists, and if local load is above `0.01` while the next rank is below `0.01`, assigns half the local load to the neighbor.

State and persistence behavior: No persistent state. It mutates the in-memory `mds` table by assigning `load` and returns a target map to the balancer framework.

Dependencies and integration points: Depends on the MDS balancer Lua environment exposing rank metrics and logging. Uses metrics `auth.meta_load`, `all.meta_load`, `req_rate`, `queue_len`, and `cpu_load_avg`.

Risks: The comment says Lua tables are 1-indexed, but the code also treats rank adjacency as `whoami+1`; correctness depends on how Ceph passes rank keys. It only considers the next rank and only spills from nonzero to near-zero load, so it can leave imbalance among active ranks untouched.

Test signals: Run with synthetic `mds` maps for last-rank, loaded/idle neighbor, loaded/loaded neighbor, and missing metrics. Verify returned target keys match balancer rank indexing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/balancers/greedyspill.lua -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/cephfs_features.cc -->
# sources/distributed-fs/ceph/src/mds/cephfs_features.cc

Purpose: Implements name lookup, reverse lookup, stringification, and formatter dumping for CephFS client/MDS feature bits.

Important APIs/functions: `cephfs_feature_name`, `cephfs_feature_from_name`, `cephfs_stringify_features`, and `cephfs_dump_features`. `feature_names` is a fixed array aligned to `CEPHFS_FEATURE_MAX + 1`.

Control flow: Name lookup returns the indexed string unless the id is beyond the known array. Reverse lookup rejects `"reserved"` and performs a linear scan. Stringify and dump iterate the array, outputting only bits set in `feature_bitset_t`.

State and persistence behavior: Stateless utility code. Feature bits are serialized elsewhere as bitsets; this file only provides human-readable views.

Dependencies and integration points: Depends on `cephfs_features.h`, `mdstypes.h` for `feature_bitset_t`, `Formatter`, `CachedStackStringStream`, and `fmt::format`. Used by session feature negotiation, admin output, and logs.

Risks: `cephfs_feature_name` checks `id > feature_names.size()` rather than `>=`, so `id == size()` would index past the array. Any new macro in the header must update the array and keep the static assert passing.

Test signals: Unit test every feature id, unknown id at `size()` and greater, reserved reverse lookup, stringify ordering, and formatter field names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/cephfs_features.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/cephfs_features.h -->
# sources/distributed-fs/ceph/src/mds/cephfs_features.h

Purpose: Defines CephFS feature bit constants, supported feature sets, metric feature sets, current release marker, and utility function declarations.

Important APIs/types: Macros define release and capability bits from reserved 0-4 through `CEPHFS_FEATURE_BLOCKDIFF` at max 23. `CEPHFS_FEATURES_ALL`, `CEPHFS_METRIC_FEATURES_ALL`, `CEPHFS_FEATURES_MDS_SUPPORTED`, and `CEPHFS_FEATURES_CLIENT_SUPPORTED` are aggregate initializer macros. Declared utilities convert/dump feature bitsets.

Control flow: No runtime control flow. The header comments document the required maintenance path when adding releases: update current release, add feature bit, add it to all features, and update `Server::update_required_client_features()`.

State and persistence behavior: Feature numbers are protocol state; changing values is wire-compatibility sensitive. Some historical release aliases intentionally share bit values (`MULTI_RECONNECT`/`NAUTILUS`, `DELEG_INO`/`OCTOPUS`).

Dependencies and integration points: Depends on release macros, client metric type constants, `feature_bitset_t`, and `Formatter`. Used by MDS/client feature negotiation and required-client-feature policy.

Risks: Adding bits without updating all aggregate macros can make features undiscoverable. Shared aliases must be preserved for compatibility. Feature sets gate client behavior, so incorrect support claims can break older clients.

Test signals: Compile-time static assertions in the implementation, feature negotiation tests, admin dump tests, and required-client-feature policy tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/cephfs_features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ECommitted.h -->
# sources/distributed-fs/ceph/src/mds/events/ECommitted.h

Purpose: Declares a journal event recording that a metadata request identified by `metareqid_t` has committed.

Important APIs/types: `ECommitted` stores `reqid`, implements print/encode/decode/dump/test-instance generation, and replays against `MDSRank`. `update_segment()` is intentionally empty.

Control flow: The event is emitted after a peer or client metadata request reaches committed state; replay can mark the request committed/idempotent without replaying metadata changes from this event itself.

State and persistence behavior: Persistent payload is only the request id. Segment accounting is not updated here, making it a marker/control event rather than metadata payload.

Dependencies and integration points: Inherits `LogEvent`, includes `EMetaBlob` for related metadata event context, and integrates with mdlog replay.

Risks: Request id correctness matters for duplicate suppression. If replay semantics diverge from request tracking, unsafe requests may be retried incorrectly.

Test signals: Encode/decode and replay idempotency around duplicate client/peer requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ECommitted.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EExport.h -->
# sources/distributed-fs/ceph/src/mds/events/EExport.h

Purpose: Declares the journal event for exporting a directory subtree to another MDS rank.

Important APIs/types: `EExport` stores an `EMetaBlob` for exported metadata, base `dirfrag_t`, boundary dirfrags, and target rank. It exposes `get_bounds`, `get_metablob`, encode/decode/dump/test instances, and replay.

Control flow: During export, the event records the subtree root and boundaries plus enough metadata for replay to reconstruct/export state. The print path describes base, target, and metablob.

State and persistence behavior: Persistent state includes base dirfrag, bounds, target, and serialized metablob. Replay depends on metablob content to reconstruct cache objects and subtree authority.

Dependencies and integration points: Uses `MDSRank`, `LogEvent`, `EMetaBlob`, `CDir`, and MDS migration/export logic.

Risks: Incorrect bounds can corrupt subtree authority after replay. Metablob completeness is essential for migrated metadata.

Test signals: Export/replay of subtrees with multiple bounds, dirty/importing dirs, and target rank failover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EExport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EFragment.h -->
# sources/distributed-fs/ceph/src/mds/events/EFragment.h

Purpose: Declares journal records for directory fragmentation split/merge prepare, commit, rollback, and finish phases.

Important APIs/types: `dirfrag_rollback` stores prior fnode state. `EFragment` stores `metablob`, operation code, inode, base fragment, split/merge bits, original fragments, and rollback buffer. `add_orig_frag` records original frags and optional rollback data.

Control flow: Fragment operations journal phase-specific events; replay uses op code and rollback payload to complete or undo split/merge changes. Positive `bits` means split from basefrag, negative means merge to basefrag.

State and persistence behavior: The event persists metadata changes in `EMetaBlob`, original fragment layout in `orig_frags`, and optional rollback data in a bufferlist.

Dependencies and integration points: Uses `LogEvent`, `EMetaBlob`, `CDir::fnode`, `frag_t`, `frag_vec_t`, and MDS dirfrag management.

Risks: Rollback correctness depends on ordering between orig frags and encoded rollback records. Wrong bit sign or basefrag can orphan dirfrags.

Test signals: Split/merge prepare/commit/rollback replay, orphan fragment finish, and dencoder coverage for rollback records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EFragment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EImportFinish.h -->
# sources/distributed-fs/ceph/src/mds/events/EImportFinish.h

Purpose: Declares the event marking completion of a subtree import attempt.

Important APIs/types: `EImportFinish` stores base imported dirfrag and a success flag, with encode/decode/dump/test generation and replay.

Control flow: Import code writes this after an import succeeds or fails; replay can finalize or unwind import state based on `success`.

State and persistence behavior: Persistent payload is minimal: base dirfrag plus boolean outcome. It does not expose a metablob.

Dependencies and integration points: Uses `MDSRank`, `LogEvent`, and migration/import state machines.

Risks: Missing or wrong success state can leave an imported subtree ambiguous or incorrectly authoritative after replay.

Test signals: Replay success and failure imports, especially after importer/exporter failover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EImportFinish.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EImportStart.h -->
# sources/distributed-fs/ceph/src/mds/events/EImportStart.h

Purpose: Declares the event that begins importing a subtree from another MDS rank.

Important APIs/types: `EImportStart` stores base dirfrag, boundary vector, source rank, `EMetaBlob`, encoded client map, and client map version. It overrides `get_metablob`, `update_segment`, and replay.

Control flow: On import start, the event records incoming subtree metadata and any client/session map needed to force-open sessions for imported caps. Replay rebuilds imported metadata and session context before later finish events.

State and persistence behavior: Durable payload includes subtree metadata, boundaries, source rank, client map buffer, and cmap version. Segment updates account for metablob contents.

Dependencies and integration points: Uses `MDLog`, `MDSRank`, `EMetaBlob`, `LogEvent`, and import migration code.

Risks: Client map version and encoded client insts must align with sessionmap replay. Boundary omissions can produce incorrect authority maps.

Test signals: Import replay with client caps, multiple boundary fragments, and interrupted import followed by finish/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EImportStart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ELid.h -->
# sources/distributed-fs/ceph/src/mds/events/ELid.h

Purpose: Declares a major segment-boundary journal event carrying a log segment id.

Important APIs/types: `ELid` inherits both `LogEvent` and `SegmentBoundary`, stores `seq` through the base boundary, and implements encode/decode/dump/replay/test instances. `is_major_segment_boundary()` returns true.

Control flow: The event marks a durable boundary during journal processing and replay; print emits `ELid(seq)`.

State and persistence behavior: Persistent state is segment sequence from `SegmentBoundary`. It is boundary metadata, not filesystem metadata.

Dependencies and integration points: Depends on `LogEvent`, `SegmentBoundary`, and `LogSegment` sequence types.

Risks: The explicit constructor initializes `LogEvent(EVENT_SEGMENT)` rather than `EVENT_LID`, which is noteworthy because the default constructor uses `EVENT_LID`; tests should confirm intentional compatibility.

Test signals: Dencoder and replay tests around segment boundary classification and event type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ELid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EMetaBlob.h -->
# sources/distributed-fs/ceph/src/mds/events/EMetaBlob.h

Purpose: Defines the main metadata payload container embedded in MDS journal events to describe inode, dentry, dirfrag, table, inode-allocation, truncate, destroy, and idempotency updates.

Important APIs/types: `fullbit` records a primary dentry and inode snapshot with dirty flags, xattrs, dirfrag tree, symlink, snap realm buffer, and old inodes. `remotebit` records a remote dentry link. `nullbit` records a null dentry. `dirlump` groups all dentry records and fnode state for one dirfrag with complete/dirty/new/importing/dirty-dft flags. Top-level `EMetaBlob` tracks roots, ordered lumps, table tids, opened inode, renamed dir fragments, inode/session allocation versions, truncate starts/finishes, destroyed inodes, client request/flush idempotency records, and touched inodes.

Control flow: Mutation code calls helpers like `add_dir_context`, `add_dir`, `add_primary_dentry`, `add_remote_dentry`, `add_null_dentry`, `add_root`, `set_ino_alloc`, `add_table_transaction`, and truncate/destroy/idempotency helpers while building a journal event. Replay decodes the blob and applies root/lump/table/allocation/truncate/destroy/client-request side effects to `MDSRank` and cache state.

State and persistence behavior: `EMetaBlob` is a compact persistent representation of projected metadata. `dirlump` lazily encodes/decodes dentry vectors in `dnbl`. `fullbit` stores a complete inode image rather than a delta, while flags indicate how replay should mark dirty parent/pool/snapflush/ephemeral-random state. Inode allocation fields coordinate inotable and sessionmap versions.

Dependencies and integration points: Uses `CInode`, `CDir`, `CDentry`, `LogSegment`, `LogSegmentRef`, `interval_set`, snap realm encoding, and `MDPeerUpdate`. It is embedded by `EUpdate`, `EOpen`, `EExport`, `EImportStart`, `EFragment`, `ESubtreeMap`, and `EPeerUpdate`.

Risks: This is replay-critical. The header warns that modified inode versions must be updated manually. Encoding version changes require updating constructors and encode paths. Incomplete dir context, missing dirty-parent flags, or wrong inotable/sessionmap versions can cause replay divergence or prevent log trimming.

Test signals: Dencoder coverage for every nested type, replay of primary/remote/null dentries, roots, imports, table tids, inode allocation/preallocation, truncate start/finish rewrite, destroyed inodes, client idempotency, and old/new feature encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EMetaBlob.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ENoOp.h -->
# sources/distributed-fs/ceph/src/mds/events/ENoOp.h

Purpose: Declares a no-op journal event with optional padding size.

Important APIs/types: `ENoOp` stores `pad_size`, implements encode/decode, empty dump, and replay.

Control flow: Used to insert journal records that do not change metadata, potentially for padding or protocol progress. Replay should consume the event without metadata side effects.

State and persistence behavior: Persistent payload is padding size and any encoded padding performed by implementation.

Dependencies and integration points: Inherits `LogEvent`.

Risks: Padding decode must stay bounded and compatible; no-op records should not affect segment accounting unexpectedly.

Test signals: Encode/decode with zero and nonzero padding, replay no side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ENoOp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EOpen.h -->
# sources/distributed-fs/ceph/src/mds/events/EOpen.h

Purpose: Declares a journal event that records clean/open inodes needed for recovery.

Important APIs/types: `EOpen` stores an `EMetaBlob`, base inode vector `inos`, and snap inode vector `snap_inos`. `add_clean_inode` adds parent dentry context and records either base or snap vino; `add_ino` records a raw inode number.

Control flow: Open-file state is journaled so replay can reopen/recover clean inodes and keep cache state for active clients. `update_segment()` accounts for opened inodes.

State and persistence behavior: Persistent payload is metablob context plus inode ids. It does not itself represent a mutation but preserves open-file recovery information.

Dependencies and integration points: Uses `LogEvent`, `EMetaBlob`, `CInode`, and MDLog replay.

Risks: Omitting parent dentry context for non-base inodes can make replay unable to locate them. Snap inodes must use `vinodeno_t` to distinguish snapshots.

Test signals: Replay clean base and snap inodes, segment update accounting, and encode/decode with metablob context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EOpen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EPeerUpdate.h -->
# sources/distributed-fs/ceph/src/mds/events/EPeerUpdate.h

Purpose: Declares peer-update journal events for multi-MDS link, rename, and rmdir prepare/commit/rollback flows, including rollback payload formats.

Important APIs/types: Rollback structs include `link_rollback`, `rmdir_rollback`, and `rename_rollback` with nested `drec`. `EPeerUpdate` stores operation type, request id, leader rank, phase op, original op, commit `EMetaBlob`, and encoded rollback data.

Control flow: Peer participants journal prepare, commit, or rollback. The commit metablob records the metadata update; rollback buffer contains enough old state for replay to manually undo if the distributed operation did not commit.

State and persistence behavior: Persistent payload includes both forward and rollback metadata because old dirty metadata may become trim-safe before final outcome. Replay applies either commit or rollback semantics by phase and original operation.

Dependencies and integration points: Uses `LogEvent`, `EMetaBlob`, `metareqid_t`, snap bufferlists, dirfrag/dentry records, and distributed `Server` peer link/rename/rmdir handlers.

Risks: Rollback records are operation-specific and must include snapbl/ctime/mtime/rctime details to restore visible metadata. Missing rollback data can break recovery after leader failure.

Test signals: Distributed link/rename/rmdir failover during prepare, commit replay, rollback replay, dencoder for all rollback structs, and log trimming with previously dirty metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EPeerUpdate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EPurged.h -->
# sources/distributed-fs/ceph/src/mds/events/EPurged.h

Purpose: Declares a journal event recording purged inode intervals and associated inode-table version.

Important APIs/types: `EPurged` stores `interval_set<inodeno_t> inos`, log segment sequence, and `inotablev`, and implements encode/decode/dump/print/update_segment/replay.

Control flow: After purge work frees inode ranges, this event lets replay advance inode-table purge/free state and update segment accounting.

State and persistence behavior: Persistent payload is the interval set, segment seq, and inotable version. It links purge completion to inode-table durability.

Dependencies and integration points: Uses `LogEvent`, `interval_set`, and `LogSegment` sequence types; consumed by purge/inotable replay.

Risks: The print string says `Eurged`, likely a typo but harmless unless tests assert text. Incorrect intervals can leak or double-free inode numbers.

Test signals: Interval encode/decode, replay inotable version advancement, and segment update accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EPurged.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EResetJournal.h -->
# sources/distributed-fs/ceph/src/mds/events/EResetJournal.h

Purpose: Declares a major segment-boundary event that resets the MDS journal.

Important APIs/types: `EResetJournal` inherits `LogEvent` and `SegmentBoundary`, returns true from `is_major_segment_boundary`, and implements encode/decode/dump/test/replay.

Control flow: Replay treats this as a reset boundary rather than a metadata mutation.

State and persistence behavior: Persistent payload is boundary/reset metadata handled by implementation.

Dependencies and integration points: Uses `LogEvent` and `SegmentBoundary`; integrated with `MDLog` journal reset handling.

Risks: Reset events must be recognized as major boundaries to prevent replay from crossing invalid journal history.

Test signals: Journal reset replay, segment-boundary detection, and dencoder compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EResetJournal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ESegment.h -->
# sources/distributed-fs/ceph/src/mds/events/ESegment.h

Purpose: Declares a normal journal segment-boundary event carrying a log segment sequence.

Important APIs/types: `ESegment` inherits `LogEvent` and `SegmentBoundary`, stores sequence via the base class, and implements print, encode/decode/dump/replay/test instances.

Control flow: Used by mdlog to mark segment boundaries during write and replay.

State and persistence behavior: Persistent state is segment sequence metadata only.

Dependencies and integration points: Depends on `LogEvent`, `SegmentBoundary`, and `LogSegment::seq_t`.

Risks: Segment sequence mismatch can affect log trimming and replay ordering.

Test signals: Encode/decode of boundary seq and replay segment transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ESegment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ESession.h -->
# sources/distributed-fs/ceph/src/mds/events/ESession.h

Purpose: Declares the journal event for a single client session open or close.

Important APIs/types: `ESession` stores client inst, open/close flag, client map version, inode intervals to free/purge, inotable version, client metadata, and auth name. It implements encode/decode/dump/test/update_segment/replay and exposes `get_client_inst`.

Control flow: Server session handling journals opens and closes. Replay recreates session state, frees/purges inode intervals on close, and advances sessionmap/inotable state.

State and persistence behavior: Persistent payload includes session identity, metadata, auth name for reclaim, and inode cleanup intervals. `update_segment()` accounts for session-related log segment state.

Dependencies and integration points: Uses `LogEvent`, entity/session types, `interval_set`, `SessionMap`, `InoTable`, and `Server` session lifecycle.

Risks: Auth name persistence is required for session reclaim after journal recreation. Inode free/purge intervals must align with inotable version and session close order.

Test signals: Open replay with metadata/auth name, close replay with free/purge intervals, dencoder old/new compatibility, and reclaim after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ESession.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ESessions.h -->
# sources/distributed-fs/ceph/src/mds/events/ESessions.h

Purpose: Declares a batched session-open journal event for forcing multiple sessions open, usually during import/recovery.

Important APIs/types: `ESessions` stores client map version, old-encoding flag, `client_map`, and `client_metadata_map`. It supports old/new decode paths, encode/dump/test/update_segment/replay, and `mark_old_encoding`.

Control flow: Batch session events are replayed by opening all encoded sessions and marking sessionmap versions accordingly. Old-style encoding exists for compatibility.

State and persistence behavior: Persistent state is maps of client ids to entity insts and metadata plus cmap version. Replay interacts with sessionmap version projection.

Dependencies and integration points: Uses `LogEvent`, client metadata/entity types, `SessionMap::replay_open_sessions`, and import/force-open server paths.

Risks: Batch size and version math must match sessionmap replay; old/new encoding mismatch can corrupt client map decode.

Test signals: Old and new dencoder tests, replay with partially already-saved sessions, and metadata merge behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ESessions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ESubtreeMap.h -->
# sources/distributed-fs/ceph/src/mds/events/ESubtreeMap.h

Purpose: Declares a major segment-boundary event that records the MDS subtree authority map.

Important APIs/types: `ESubtreeMap` stores an `EMetaBlob`, `subtrees` map from root dirfrag to bounds, `ambiguous_subtrees`, and `expire_pos`. It exposes `get_metablob`, replay, dump, dencoder test generation, and `is_major_segment_boundary`.

Control flow: Written to checkpoint subtree authority and cache metadata; replay restores subtree map and ambiguous subtrees at a major boundary.

State and persistence behavior: Persistent payload includes metablob metadata plus subtree maps and expiration position. It is both metadata payload and journal boundary.

Dependencies and integration points: Uses `LogEvent`, `SegmentBoundary`, `EMetaBlob`, `MDCache` subtree authority, and mdlog trimming/replay.

Risks: Stale or incomplete subtree maps can assign authority incorrectly after failover. `expire_pos` must align with journal expiry.

Test signals: Replay of subtree checkpoints with ambiguous subtrees, metablob restoration, and major-boundary handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ESubtreeMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ETableClient.h -->
# sources/distributed-fs/ceph/src/mds/events/ETableClient.h

Purpose: Declares journal records for client-side table operations.

Important APIs/types: `ETableClient` stores table id, operation, and tid. It prints table and operation names through `get_mdstable_name` and `get_mdstableserver_opname`, and implements encode/decode/dump/test/replay.

Control flow: Table clients journal prepare/commit/rollback progress so replay can resume table transactions.

State and persistence behavior: Persistent payload is table/op/tid. The table-specific mutation payload is handled elsewhere by table server or metablob records.

Dependencies and integration points: Depends on `mds_table_types`, `LogEvent`, and `MDSTableClient` replay logic.

Risks: Wrong table/op names are diagnostic only, but wrong tid breaks transaction recovery.

Test signals: Replay table client op sequences for snap/inotable/session-related tables and dencoder coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ETableClient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ETableServer.h -->
# sources/distributed-fs/ceph/src/mds/events/ETableServer.h

Purpose: Declares journal records for authoritative table-server operations and mutations.

Important APIs/types: `ETableServer` stores table id, operation, request id, source MDS, mutation buffer, tid, and table version. It implements encode/decode/dump/test/update_segment/replay.

Control flow: Table-server prepare/commit/rollback/update events persist distributed table mutations. Replay applies table operation, request id, source rank, tid, and version to the appropriate `MDSTableServer`.

State and persistence behavior: Persistent payload includes both transaction metadata and opaque table mutation buffer. `update_segment()` accounts table transactions for log trimming.

Dependencies and integration points: Depends on `mds_table_types`, `LogEvent`, `MDSTableServer`, and specific tables such as snapshot server.

Risks: Mutation buffer schema is table-specific; mismatched table/op decoding can corrupt table state. Version must remain monotonic.

Test signals: Snap table server prepare/commit/rollback replay, server update replay, request deduplication by reqid/bymds, and dencoder tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/ETableServer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EUpdate.h -->
# sources/distributed-fs/ceph/src/mds/events/EUpdate.h

Purpose: Declares the general metadata update journal event used by most MDS namespace and inode mutations.

Important APIs/types: `EUpdate` stores an `EMetaBlob`, operation type string, encoded client map, client map version, request id, and `had_peers` flag. It exposes `get_metablob`, encode/decode/dump/test/update_segment/replay.

Control flow: Server mutation handlers populate the metablob, optional client map/request metadata, and submit the event to mdlog. Replay applies the metablob and uses request/client/peer metadata for idempotency and distributed operation recovery.

State and persistence behavior: Persistent state is the full metablob plus request/session context. Segment updates are delegated to metablob and event-specific fields.

Dependencies and integration points: Uses `LogEvent`, `EMetaBlob`, `Server` mutation paths, `SessionMap`, `InoTable`, table clients, and peer request handling.

Risks: As the generic update event, missing metablob fields or wrong `had_peers`/reqid/cmapv can affect replay, duplicate suppression, and peer rollback. The type string is diagnostic but useful for debugging journal contents.

Test signals: Replay create/unlink/rename/setattr/xattr/snapshot updates, idempotent client request completion, peer-involved updates, and dencoder compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/events/EUpdate.h -->
