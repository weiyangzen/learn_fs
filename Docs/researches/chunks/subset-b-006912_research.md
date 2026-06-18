# sources/distributed-fs/ceph/src/mds/MDCache.cc lines 1-8381

## Scope

This chunk covers the first 8,381 lines of CephFS MDS `MDCache.cc`. It includes construction, configuration refresh, system inode/bootstrap creation, root and per-rank directory opening, stray-directory setup, subtree authority bookkeeping, snapshot/COW and recursive-stat journaling helpers, peer commit/rollback recovery, resolve and rejoin protocols, capability reconnect/import/export handling, file-size and truncate recovery, purge completion journaling, cache trimming and replica expiry, memory reporting, shutdown progression, stray export during shutdown, and the start of MDS cache message dispatch.

The chunk ends immediately after `MDCache::dispatch()` and before the path traversal implementation that begins in the next chunk. It depends heavily on types declared in `MDCache.h`, `CInode`, `CDir`, `CDentry`, `Mutation`, `MDRequest`, `Locker`, `Migrator`, `MDLog`, `SnapRealm`, `StrayManager`, and the `messages/` and `events/` families.

## Purpose

`MDCache` is the in-memory metadata cache and recovery coordinator for a CephFS MDS rank. This section owns the early lifecycle of the cache, the authoritative subtree map, snapshot-aware metadata mutation journaling, distributed MDS recovery handshakes, cache replica trimming, and shutdown draining.

At runtime it keeps inode, dentry, and directory-fragment objects connected to MDS authority, lock, journal, and client-capability state. During normal operation it maintains subtree ownership and recursive accounting as metadata changes are projected and journaled. During failure recovery it exchanges resolve and rejoin messages so ranks agree on subtree authority, replayed peer mutations, cache replicas, scatterlock state, and client caps. During memory pressure or shutdown it trims clean cache objects and tells authoritative peers which replicas have expired.

## Important APIs, Types, and Functions

`MDCacheContext` and `MDCacheLogContext` are local callback bases that retain an `MDCache*` and resolve `get_mds()` for ordinary MDS contexts and journal-log contexts. The chunk defines many concrete callbacks, such as `C_MDC_CreateSystemFile`, `C_MDS_RetryOpenRoot`, `C_MDC_CommittedLeader`, `C_MDC_PeerCommit`, `C_MDC_RejoinOpenInoFinish`, `C_MDC_RejoinSessionsOpened`, `C_MDC_ReIssueCaps`, truncate I/O callbacks, and purge/shutdown callbacks.

`MDCache::MDCache()` initializes major subsystems and policy knobs: `Migrator`, `OpenFileTable`, `Filer`, `StrayManager`, `RecoveryQueue`, trim and quiesce decay counters, cache memory limits, cache reservation and health thresholds, ephemeral export-pin settings, symlink recovery, dirfrag and shutdown killpoints, global snaprealm sequencing, LRU midpoint, decay halflife, and the upkeep thread. `handle_conf_change()` updates these values live and pushes relevant changes into `Migrator` and `MDBalancer`.

The inode/bootstrap helpers are `add_inode()`, `remove_inode()`, `gen_default_file_layout()`, `gen_default_log_layout()`, `init_layouts()`, `create_unlinked_system_inode()`, `create_system_inode()`, `create_root_inode()`, `create_empty_hierarchy()`, `create_mydir_hierarchy()`, `_create_system_file()`, and `_create_system_file_finish()`. They populate the root inode, rank-local `mdsdir`, stray directories, system dentries, default layouts, base inode auth, snaprealms, and initial dirty journal/store state.

The root and stray opening path is handled by `open_root_inode()`, `open_mydir_inode()`, `open_mydir_frag()`, `open_root()`, `advance_stray()`, `populate_mydir()`, `open_foreign_mdsdir()`, and `get_stray_dir()`. These methods fetch or discover root and rank-local metadata, create missing stray system files, pin strays, open all stray dirfrags, activate `StrayManager`, and rotate among stray dirs while pre-fragmenting future stray dirs when needed.

Subtree authority management centers on `subtrees`, a map from subtree-root `CDir*` to its child-bound `CDir*` set. `adjust_subtree_auth()`, `try_subtree_merge()`, `try_subtree_merge_at()`, `eval_subtree_root()`, `adjust_bounded_subtree_auth()`, `get_force_dirfrag_bound_set()`, `map_dirfrag_set()`, `get_subtree_root()`, `get_projected_subtree_root()`, `remove_subtree()`, `get_subtree_bounds()`, `get_wouldbe_subtree_bounds()`, `verify_subtree_bounds()`, `project_subtree_rename()`, and `adjust_subtree_after_rename()` create, merge, split, and validate subtree roots and bounds. They also handle projected renames and popularity adjustment.

Snapshot and metadata journaling helpers include `pick_inode_snap()`, `cow_inode()`, `journal_cow_dentry()`, `journal_dirty_inode()`, `project_rstat_inode_to_frag()`, `_project_rstat_inode_to_frag()`, `project_rstat_frag_to_inode()`, `broadcast_quota_to_client()`, and `predirty_journal_parents()`. These functions clone old inode/dentry versions for snapshots, project recursive stats between inodes and dirfrags, update quota clients and MDS replicas, and populate `EMetaBlob` records for journal entries.

Peer commit and resolve APIs include `log_leader_commit()`, `_logged_leader_commit()`, `committed_leader_peer()`, `logged_leader_update()`, `finish_committed_leaders()`, `_logged_peer_commit()`, `create_subtree_map()`, `resolve_start()`, `send_resolves()`, `send_peer_resolves()`, `send_subtree_resolves()`, `handle_mds_failure()`, `handle_mds_recovery()`, `set_recovery_set()`, `handle_resolve()`, `process_delayed_resolve()`, `maybe_resolve_finish()`, `handle_resolve_ack()`, `add_uncommitted_peer()`, `finish_uncommitted_peer()`, `finish_rollback()`, and ambiguous import helpers. Together these reconcile in-flight peer mutations, subtree claims, ambiguous imports, snap table commits, and rollback/commit decisions across rank failure.

Rejoin is implemented by `rejoin_start()`, `rejoin_send_rejoins()`, `rejoin_walk()`, `handle_cache_rejoin()`, `handle_cache_rejoin_weak()`, `rejoin_scour_survivor_replicas()`, `rejoin_invent_inode()`, `rejoin_invent_dirfrag()`, `handle_cache_rejoin_strong()`, `handle_cache_rejoin_ack()`, `rejoin_trim_undef_inodes()`, `rejoin_gather_finish()`, `process_imported_caps()`, `choose_lock_states_and_reconnect_caps()`, `rejoin_send_acks()`, and snaprealm/cap helpers. Weak rejoins advertise recovering cache connectivity; strong rejoins advertise survivor authoritative state; ACKs return full base records, lock states, replica nonces, imported caps, and corrected dirfrag topology.

File recovery and persistence helpers include `queue_file_recover()`, `identify_files_to_recover()`, `start_files_to_recover()`, `do_file_recover()`, `truncate_inode()`, `_truncate_inode()`, `truncate_inode_write_finish()`, `truncate_inode_finish()`, `truncate_inode_logged()`, `add_recovered_truncate()`, `remove_recovered_truncate()`, `start_recovered_truncates()`, `start_purge_inodes()`, and `purge_inodes()`. They coordinate post-rejoin file size recovery, OSD truncation through `Filer`, fscrypt last-block writeback, journaled truncate completion, and release of purged inode numbers.

Cache lifecycle APIs include `trim_lru()`, `trim()`, `send_expire_messages()`, `trim_dentry()`, `trim_dirfrag()`, `trim_inode()`, `trim_non_auth()`, `trim_non_auth_subtree()`, `try_trim_non_auth_subtree()`, `standby_trim_segment()`, `handle_cache_expire()`, `process_delayed_expire()`, `inode_remove_replica()`, `dentry_remove_replica()`, `trim_client_leases()`, `check_memory_usage()`, `shutdown_start()`, `shutdown_pass()`, `shutdown_export_strays()`, and `dispatch()`.

## Control Flow

Startup begins by initializing layouts and opening base metadata. A root rank creates or fetches `CEPH_INO_ROOT`, adjusts root dirfrag authority, fetches its contents if needed, then opens its rank-local `mdsdir`. Non-root ranks discover the root inode from the root rank and fetch their own `mdsdir`. `populate_mydir()` ensures all `strayN` system directories exist, fetches all stray dirfrag leaves, pins them, activates `StrayManager`, marks the cache open, and wakes open waiters.

Subtree authority updates follow a root/bounds model. `adjust_subtree_auth()` either changes the auth on an existing subtree root or creates a new subtree root beneath the current root, moves nested child bounds under it, and inserts it as a bound of the parent. `try_subtree_merge_at()` removes redundant subtree roots when parent and child auth match and neither export-bound nor auxiliary state blocks merging. Bounded authority changes force dirfrags when necessary, create requested bounds, swallow intervening ambiguous subtrees, verify the final bounds, and evaluate subtree-root locks outside replay/resolve.

Metadata mutation journaling first projects the object being changed, then `predirty_journal_parents()` propagates directory mtime, fragstat, and rstat changes up the parent chain while respecting auth pins, scatterlock writability, dirstat propagation throttling, and snapshot rstat mode. It adds the final dir context and dirty parent inodes to the `EMetaBlob`. `journal_cow_dentry()` and `cow_inode()` split dentries/inodes into old snapshot intervals when a mutation crosses snap boundaries or touches ambiguous auth state.

Peer request recovery has two layers. Leaders journal `ECommitted` only after peer acknowledgements are safe. During resolve, ranks exchange `MMDSResolve` messages that include uncommitted peer requests, subtree claims, ambiguous imports, and table commits. The receiver replies with commit/abort decisions for peer requests, may attach imported-cap assignments for rename cap exports, and applies subtree claims with `adjust_bounded_subtree_auth()`. `maybe_resolve_finish()` waits for all resolves, resolve ACKs, and rollback journaling before trimming unlinked objects, recalculating auth bits, and finishing resolve.

MDS failure handling rewrites all recovery gathers and cleans affected active requests. Peer operations prepared against the failed rank are marked for resolve or rollback; leader requests drop failed witnesses or delay ACKs if they still need another peer; fragment operations are cancelled or completed; open-ino/find-ino peer probes are kicked. Recovery handling wakes waiters below subtrees whose authority has returned active and retries peer inode lookup/open work.

Rejoin starts after resolve. A recovering rank sends weak rejoins for non-auth regions it cached; a survivor sends strong rejoins to recovering authorities. `rejoin_walk()` recursively enumerates dirfrags, dentries, inodes, replica nonces, lock states, and dirty scatterlock state. Weak handlers on survivors immediately build ACKs with authoritative base and lock records, import caps, update replica maps, and scour stale replicas. Weak handlers on recovering ranks record cap exports and possible scatterlock updates for later reconciliation.

Strong rejoins are consumed only by recovering ranks. `handle_cache_rejoin_strong()` creates placeholder `REJOINUNDEF` inodes/dirfrags when survivor state references objects missing locally, fixes dirfrag-fragmentation mismatches, reconstructs missing dentries, records remote auth pins, frozen auth pins, xlocks, and wrlocks into peer `MDRequest` objects, updates replica nonces, infers scatterlock states, and tracks unlinked inodes that the survivor still references. ACK processing then adjusts local dirfrags and dentries to authoritative linkage, decodes full inode/dirfrag bases, restores lock states, sends client cap export notifications, invalidates snaprealms, and advances to snaprealm opening when all gathers complete.

Capability reconnect flows through `process_imported_caps()`. It prefetches open-file-table inodes, opens missing cap inodes through `open_ino()`, force-opens client sessions by journaling `ESessions`, imports peer rename caps, reconnects client caps, exports caps that belong to another authority, and records `reconnected_caps` and snaprealm reconnect information. `open_snaprealms()` then rebuilds needed snapflush state, sends split/update snap messages to clients, notifies global snaprealm updates, and completes rejoin.

File recovery scans authoritative head file inodes after rejoin. If `client_ranges` reference clients without caps, it places the inode in `LOCK_PRE_SCAN` and queues file recovery. Otherwise it checks max size and issues caps where appropriate. Truncate recovery pins the inode and log segment, waits for pending snapflushes if buffered write caps exist, writes fscrypt last-block data when needed, issues the OSD truncate through `Filer`, journals a "truncate finish" update, clears truncate state, drops locks/pins, and wakes `WAIT_TRUNC` waiters.

Cache trimming first expires bottom-LRU entries, then ordinary LRU entries until a count is met or memory pressure clears, subject to `mds_cache_trim_threshold` throttling. `trim_dentry()` can recursively trim linked inodes, clear directory completeness, add bloom entries, and queue `MCacheExpire` records for remote auth ranks with replica nonces. `trim_inode()` recursively closes dirfrags, may invoke stray purge evaluation for auth inodes, sends remote inode expiry notices, unlinks the parent dentry, and removes the inode. `trim()` also trims non-auth subtrees, exports empty imports, handles root/stopping rank special cases, expires other ranks' `mdsdir` contents, and emits batched expire messages.

Shutdown is a repeated pass. It exports/purges stray contents to rank 0, trims the cache, exports remaining auth subtrees from nonzero ranks, terminates sessions, logs a final subtree map if needed, trims the metadata log, drops stray pins, waits for migration and replica/auth-pin drain, caps the mdlog, waits for objecter I/O, drains LRU state, removes the rank-local subtree and `myin`, removes the global snaprealm inode, and returns complete only when the cache is empty and stable.

`dispatch()` demultiplexes MDS cache messages in this chunk for resolve, resolve ack, cache rejoin, discover/discover reply, dir update, cache expire, dentry link/unlink, fragment notify/ack, find-ino, open-ino, and snap update. Several handlers for these message types live later in the file and are outside this chunk.

## State and Persistence Behavior

The primary resident cache maps are `inode_map` for head inodes and `snap_inode_map` for old/snapshot inodes. Base inode pointers such as `root`, `myin`, `strays[]`, and `base_inodes` are maintained as inodes are added or removed. `remove_inode()` clears dirty, parent-dirty, scatter-dirty, client-writeable, export-pin, ephemeral-pin, cap, open-file, and replay-taken state before deleting an unreferenced inode.

`subtrees` is durable in memory and is periodically persisted through `ESubtreeMap`. `create_subtree_map()` serializes auth subtrees, bounds, ambiguous imports, projected subtree renames, directory contexts, and the journaler expire position. On replay and recovery, this map is simplified and reconciled with peer resolve data.

Journal persistence uses `EUpdate`, `ECommitted`, `EPeerUpdate`, `EImportFinish`, `ESubtreeMap`, `ESessions`, `EPurged`, and `ELid`. Mutations project inode/fnode/dentry versions before journaling and apply the projected state only after log callbacks complete. Log segments retain lists for dirty objects, open files, truncating inodes, purging inodes, uncommitted leaders, and uncommitted peers so replay, trimming, and recovery can finish interrupted work.

Snapshot persistence is represented by inode/dentry `first` and `last` ranges, `old_inodes`, `dirty_old_rstats`, snaprealms, client snapflush tracking, and snap table commits exchanged in resolve. `cow_inode()` and `journal_cow_dentry()` materialize old versions and record need-snapflush state for clients that held write caps across snap boundaries.

Client capability state crosses MDS failures. Rejoin maps include cap exports, cap imports, imported-cap acknowledgements, client entity addresses, client metadata, `reconnected_caps`, `reconnected_snaprealms`, `cap_imports_missing`, and waiter maps. Successful cap import sends `MClientCaps` import/export operations to clients and may assign new cap IDs after peer rename recovery.

Replica state persists in memory through per-object replica maps and nonces. Cache expiry messages carry those nonces so stale expiry notices can be ignored. Rejoin ACKs increment and return replica nonces for dirfrags, dentries, and inodes; replica removal also updates lock replica/gather state.

Truncate and purge persistence bridges MDS journal and OSD objects. Truncating inodes are pinned in log segments until OSD truncate and journaled completion finish. Purged inode ranges are sent to `Filer::purge_range()`, then journaled in `EPurged`; the inotable release is applied only from the log callback.

Shutdown state includes `shutdown_export_next`, `shutdown_exporting_strays`, killpoint checks, mdlog capped state, outstanding objecter work, stray pins, and subtree/migration state. It is intentionally iterative because most steps depend on asynchronous migration, session close, log trim, or OSD completion.

## Dependencies and Integration Points

`MDCache` is tightly coupled to `MDSRank`: it reads MDS state, MDS map, root rank, recovery set, session map, table clients, objecter, finisher, timer, clog/logger, mdlog, server, locker, balancer, migrator, snapclient, inotable, and metrics handler.

`CInode`, `CDir`, and `CDentry` provide the cache object model. This chunk manipulates their projected versions, locks, auth bits, replica maps, dirfragtree, LRU items, dirty lists, ref pins, parent linkage, snaprealm pointers, quota fields, old inode maps, and recursive stat fields.

Journal integration uses `MDLog`, `LogSegmentRef`, `Journaler`, `EMetaBlob`, and event classes. The code relies on submit/flush callbacks to convert projected or pending state into applied state and to wake waiters safely after persistence.

Distributed-MDS integration uses messages `MMDSResolve`, `MMDSResolveAck`, `MMDSCacheRejoin`, `MCacheExpire`, `MMDSPeerRequest`, `MClientCaps`, `MClientQuota`, `MGatherCaps`, `MClientSnap`, and the message handlers wired by `dispatch()`. It also interacts with peer request state in `MDRequestImpl` and server rollback handlers for link, rename, and rmdir.

Storage integration is through `Filer` operations for truncate, fscrypt last-block writes, and object purging. `SnapRealm` and `SnapClient` provide snap contexts, snap traces, snap table commit synchronization, and client snap update messages.

Balancer and migrator integration appears in subtree popularity adjustment, ephemeral export pins, dirfrag split/merge queues, import/export disambiguation, export of empty imports, shutdown subtree exports, and stray migration to rank 0.

Operational integration includes perf counters, memory model sampling, admin/log diagnostics, heartbeat resets during long loops, configurable killpoints for testing, and debug dump helpers such as `show_cache()` and `show_subtrees()`.

## Risks and Edge Cases

Subtree authority is assertion-heavy and sensitive to ambiguous auth, projected renames, forced fragmentation, and export/import boundary states. Incorrect bounds or premature merging can make two ranks believe they are auth or leave a subtree unreachable from the root.

Recovery paths depend on precise ordering. Resolve must finish peer commits/rollbacks and snap table synchronization before subtree resolve completion; rejoin must not send cache rejoins while imported caps are still being opened; ACK processing must wait for full inode/lock state before opening snaprealms. Reordering these steps risks stale linkage, lost caps, or lock-state divergence.

Snapshot COW and rstat projection have many interval-splitting cases. Bugs in `first`/`last` handling, dirty old rstat sparse maps, or `mds_snap_rstat` branches can silently misaccount recursive stats or miss client snapflush obligations. The code contains comments noting incomplete propagation to old parents after directory rename.

Lock and pin state are central correctness hazards. `predirty_journal_parents()` can only safely update dirfrag/inode stats when required locks are held or force-acquired; rejoin reconstructs auth pins, frozen auth pins, xlocks, wrlocks, and scatterlocks from peer messages; replica removal must not remove gathering participants in cases where rejoined wrlocks may still exist.

Cache trimming must avoid removing objects that are unreadable but about to receive replication updates, dirfrags under fragmentation, non-auth subtree roots needed for rejoin, stopping-rank strays with live hardlinks, and inodes being purged rather than simply trimmed. Expire messages are nonce-protected, but missing or mismatched dirfrags still lead to assertions in several paths.

Client capability recovery is exposed to missing sessions, missing inodes, peer rename cap exports, reassigned cap IDs, stale client caps, and snaprealm mismatch. Failures are partly converted into stale export notifications and warnings, but many invariant violations assert.

Truncate recovery spans journal, locks, client snapflush, fscrypt last-block data, and OSD calls. The code assumes truncate sizes are below `1ULL << 63`, handles `-ENOENT` as acceptable I/O completion, and adds block size to fscrypt truncate length to avoid missing the last object.

Shutdown may stall on strays, exported subtrees, unclosed sessions, untrimmed log segments, replicated `myin`, auth pins, active objecter operations, or residual LRU entries. Rank 0 special-casing and stray migration to rank 0 mean shutdown behavior differs by MDS rank.

The chunk boundary cuts after `dispatch()`. Message handlers for discovery, dir update, dentry link/unlink, fragment notify, find/open ino, snap update, and traversal are referenced here but implemented later in the file, so full per-file analysis must combine the next chunk.

## Test Signals

Useful coverage for this chunk includes MDS bootstrap tests that create an empty filesystem, recreate missing/bad `mdsdir` fragments, create root and stray directories, open remote roots, and verify default file/log layouts and base inode auth.

Subtree tests should cover authority adjustment, bounded auth with forced dirfrag bounds, projected rename across subtree roots, import/export ambiguity, merge suppression for export-bound/auxiliary subtrees, and serialized `ESubtreeMap` replay.

Snapshot and accounting tests should mutate files and directories across snapshots, renames, hardlinks, and quota roots, then validate dentry/inode COW intervals, snapflush requirements, recursive rstats, fragstats, quota broadcasts, and single-frag consistency checks.

Resolve/rejoin tests should simulate leader/peer MDS crashes before and after peer prepare, before and after peer commit ACK, during ambiguous import/export, during fragment operations, and with pending snap table commits. Expected signals are correct commit/abort decisions, rollback journaling, uncommitted peer cleanup, subtree auth convergence, and no stuck resolve/rejoin gathers.

Rejoin cache tests should include weak/strong/ACK exchanges with missing dirfrags, refragmented directories, stale snap dentries, missing sessions, imported/exported caps, peer rename cap exports, dirty scatterlocks, remote auth pins, frozen auth pins, xlocks, wrlocks, and placeholder `REJOINUNDEF` objects that must be opened or trimmed.

Capability and snaprealm tests should reconnect clients with dirty caps, stale realm sequence numbers, snapflush-in-progress state, missing cap inodes, and clients that moved realms. Expected outputs are correct `MClientCaps` import/export messages, `MClientSnap` split/update messages, rebuilt need-snapflush records, and lock state selection.

File recovery and truncate tests should cover client range recovery without caps, max-size checks, recovered truncates from old log segments, snapflush-delayed truncates, fscrypt last-block writeback, hole truncation, OSD `-ENOENT`, journaled truncate finish, and wakeup of truncate waiters.

Cache trim and expire tests should exercise LRU and bottom-LRU trimming, trim threshold throttling, non-auth subtree trimming, stopping-rank `mdsdir` expiry, stale nonce expiry drops, delayed expires during export, dirfrag mismatch during refragmentation, unreadable replica locks, and standby replay segment cleanup.

Shutdown tests should cover nonzero-rank subtree export to rank 0, stray export/purge batching, session termination, mdlog subtree-map insertion and cap, objecter-active waiting, pinned/replicated `myin`, global snaprealm removal, and every configured shutdown killpoint.

Instrumentation signals include perf counters for inode/cache sizes, trim throttle, stray counts, recovery counts, memory RSS/heap samples, heartbeat reset behavior in long loops, `show_subtrees()`/`show_cache()` diagnostics, and assertions around replica counts, subtree bounds, lock states, and dirty list cleanup.

## Cross-Chunk Notes

The next chunk begins with `path_traverse()` and contains many handlers referenced by `dispatch()` here, including discovery, dir updates, dentry replication, fragmentation, open/find inode, request lifecycle, and later mutation paths. The final per-file report should merge this document with `subset-b-006913` before drawing conclusions about the complete `MDCache.cc` behavior.
