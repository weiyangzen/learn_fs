# sources/distributed-fs/ceph/src/mds/MDCache.cc lines 8382-14808

## Scope And Purpose

This chunk is a large operational middle-to-late section of CephFS `MDCache.cc`. It covers request-time metadata traversal, remote inode discovery, active request tracking, snaprealm invalidation, stray scanning, inter-MDS discovery and replica encoding, dentry link/unlink replication, directory fragmentation and rollback, administrative cache dumping and scrub/repair helpers, quiesce and lock-path internal operations, cache upkeep, and file snapshot block-diff support.

The code sits on the hot path for CephFS MDS correctness. It coordinates in-memory metadata objects (`CInode`, `CDir`, `CDentry`), distributed ownership and replica state across MDS ranks, mdlog persistence, object-store I/O, client capability recall, and admin-facing internal operations. Many functions return `1` to mean "asynchronous wait/retry scheduled", `0` for immediate success, and negative errno values for terminal failure.

## Important APIs, Types, And Functions

`MDCache::path_traverse()` is the central path walk engine in this chunk. It accepts an `MDRequestRef`, a retry context factory, a `filepath`, traversal flags, and optional output vectors/pointers for dentries, target inode, and current dirfrag. It handles snapdir traversal, lock acquisition, auth forwarding, damaged metadata checks, incomplete dirfrag fetches, remote dentry opening, discover requests, and null-dentry creation for missing auth dentries.

`maybe_request_forward_to_auth()` is the common forwarding guard used by traversal. It waits on ambiguous auth, forwards client/internal work to the authoritative MDS rank when this rank is not auth, and returns `0`, `1`, or `2` to distinguish local success, wait, and actual forwarding.

`cache_traverse()`, `open_remote_dirfrag()`, `get_dentry_inode()`, `open_remote_dentry()`, and `_open_remote_dentry_finish()` are local/remote object helpers. They find cached paths without network I/O, discover remote dirfrags, link cached remote inodes into dentries, open remote inode backtraces, and mark bad remote inodes through `DamageTable`.

The open-by-inode path is implemented by `_open_ino_backtrace_fetched()`, `_open_ino_parent_opened()`, `_open_ino_traverse_dir()`, `_open_ino_fetch_dir()`, `open_ino_traverse_dir()`, `open_ino_finish()`, `do_open_ino()`, `do_open_ino_peer()`, `handle_open_ino()`, `handle_open_ino_reply()`, `kick_open_ino_peers()`, `open_ino_batch_start()`, `open_ino_batch_submit()`, and `open_ino()`. The state carrier is `open_ino_info_t` in `MDCache.h`, with ancestors, checked peers, current checking rank, auth hint, backtrace/discover flags, replica/xlock wants, pool, last error, and waiters.

The older peer path lookup helper uses `find_ino_peers()`, `_do_find_ino_peer()`, `handle_find_ino()`, `handle_find_ino_reply()`, and `kick_find_ino_peers()`. Its `find_ino_peer_info_t` tracks the target ino, tid, finisher, path-locking requirement, current hint/checking rank, and checked ranks.

Request lifecycle APIs include `get_num_client_requests()`, `request_start()`, `request_start_peer()`, `request_start_internal()`, `request_get()`, `request_finish()`, `request_forward()`, `dispatch_request()`, `request_cleanup()`, and `request_kill()`. These functions create op-tracker-backed `MDRequestImpl` instances, route client/peer/internal operations, handle peer-commit reentry, update internal-op counters, release locks/pins/session links, abort quiesce children, and preserve replay sequencing.

Snaprealm operations include `create_global_snaprealm()`, `do_realm_invalidate_and_update_notify()`, `send_snap_update()`, `handle_snap_update()`, and `notify_global_snaprealm_update()`. They invalidate cached snap state across realm subtrees, build `MClientSnap` updates, notify replica MDS ranks with `MMDSSnapUpdate`, and signal the snap client on committed global snap operations.

Stray and purge-adjacent helpers include `scan_stray_dir()`, `fetch_backtrace()`, `stray_status()`, `maybe_eval_stray()`, and `clear_dirty_bits_for_stray()`. They iterate `strays[]`, fetch incomplete stray dirfrags, mark orphan inodes, dump stray state for admin sockets, fetch inode parent xattrs, enqueue purge candidates through `StrayManager`, and clear dirty bits under stray directories.

Discovery and replica exchange are handled by `_send_discover()`, `discover_base_ino()`, `discover_dir_frag()`, both `discover_path()` overloads, `kick_discovers()`, `handle_discover()`, `handle_discover_reply()`, `encode_replica_dir()`, `encode_replica_dentry()`, `encode_replica_inode()`, `decode_replica_dir()`, `decode_replica_dentry()`, `decode_replica_inode()`, `encode_replica_stray()`, and `decode_replica_stray()`. They move serialized authoritative metadata to replicas and wake waiters once requested base inodes, dirfrags, dentries, or inodes have arrived.

Replica update/link APIs include `send_dir_updates()`, `handle_dir_update()`, `encode_remote_dentry_link()`, `decode_remote_dentry_link()`, `send_dentry_link()`, `handle_dentry_link()`, `send_dentry_unlink()`, and `handle_dentry_unlink()`. They maintain directory replication hints and propagate primary/remote dentry linkage changes, including rename-to-stray transitions.

Directory fragmentation is a major subsystem in this chunk. `adjust_dir_fragments()` and `force_dir_fragment()` mutate in-memory fragtree and subtree maps. `can_fragment()`, `split_dir()`, `merge_dir()`, `fragment_freeze_dirs()`, `fragment_mark_and_complete()`, `fragment_frozen()`, `dispatch_fragment_dir()`, `_fragment_logged()`, `_fragment_stored()`, `_fragment_committed()`, `_fragment_old_purged()`, `fragment_drop_locks()`, `fragment_maybe_finish()`, `handle_fragment_notify_ack()`, `handle_fragment_notify()`, `add_uncommitted_fragment()`, `finish_uncommitted_fragment()`, `rollback_uncommitted_fragment()`, `wait_for_uncommitted_fragments()`, and `rollback_uncommitted_fragments()` implement the freeze, journal prepare, store, notify, commit, purge-old, finish, and recovery/rollback paths. `fragment_info_t` records live operation state; `ufragment` records uncommitted persisted state.

Admin/debug and maintenance helpers include `force_readonly()`, `maybe_fragment()`, `show_subtrees()`, `show_cache()`, `cache_status()`, `dump_tree()`, `dump_cache()` overloads, `dump_inode()`, `dump_dir()`, `handle_mdsmap()`, `is_ready_to_trim_cache()`, and `upkeep_main()`.

Scrub, uninline, repair, and flush operations include `enqueue_scrub()`, `enqueue_scrub_work()`, `uninline_data_work()`, `repair_dirfrag_stats()`, `repair_dirfrag_stats_work()`, `repair_inode_stats()`, `repair_inode_stats_work()`, `rdlock_dirfrags_stats()`, `rdlock_dirfrags_stats_work()`, `flush_dentry()`, and `flush_dentry_work()`.

Quiesce and lock-path helpers include `quiesce_overdrive_fragmenting_async()`, `dispatch_quiesce_inode()`, `add_quiesce()`, `dispatch_quiesce_path()`, `quiesce_path()`, `dispatch_lock_path()`, and `lock_path()`. `LockPathConfig` in `MDCache.h` carries target path, requested lock strings, optional lifetime, and auth-pin behavior.

The final block-diff helpers are `file_blockdiff()` and `aggregate_snap_sets()`, with `C_ListSnapsAggregator` collecting object `list_snaps` results before converting clone overlap information into byte extents.

## Control Flow

Path traversal starts by resolving the base inode, with special handling for foreign MDS directories and strays. It optionally attaches lock-cache state, takes snap/layout locks, then loops over path components. For each component it opens or discovers the selected dirfrag, checks damage records, optionally forwards to auth, looks up the dentry, acquires path/dentry locks, resolves null/primary/remote linkages, fetches incomplete auth dirs, discovers non-auth paths, or returns auth-forward status. Successful traversal updates request snap state and lock-state flags.

Open-by-inode flow first coalesces concurrent waiters in `opening_inodes`. It checks local cache, asks peers using `MMDSOpenIno`, fetches the inode backtrace xattr when needed, opens/traverses parent directories from backtrace ancestors, discovers replica metadata if a caller requested it, and finally completes every waiter with either the auth rank or errno. Batched mode defers multiple directory fetches into one `fetch_keys()` per `CDir`.

Peer `find_ino` flow is path-oriented: this rank asks active peers whether they have an inode. A positive reply carries a path; the requester calls `path_traverse(... MDS_TRAVERSE_DISCOVER ...)` to materialize it locally. If traversal fails, the checked set is reset and peers are retried.

Request flow is centralized. Client, peer, and internal requests enter `active_requests`; `dispatch_request()` routes them to server handlers or internal work functions. `request_finish()` handles peer commit callbacks before cleanup, while `request_forward()` forwards client messages or cancels internal operations with `-EXDEV`. `request_cleanup()` is responsible for dropping locks, auth pins, cache pins, sticky dirs, waiter queues, session links, quiesce children, and active-map membership. `request_kill()` is careful around peer updates and committing requests, delaying or no-oping when rollback would be unsafe.

Discovery flow sends `MDiscover` requests keyed by tid and pins the base object. The auth side builds a `MDiscoverReply` by serializing a path prefix of dirs, dentries, and inodes until the requested path is satisfied, missing, frozen, xlocked, incomplete, non-auth, or damaged. The requester decodes the trace, creates replica objects as needed, adjusts subtree auth, and wakes base-dir/dentry waiters or finishes them with `-ENOENT`.

Replica link/unlink flow is asynchronous best-effort to known replicas and skips peers that are not ready or already witnessed in a mutation. Link notifications serialize either a primary inode replica or a remote inode tuple. Unlink notifications may also serialize the stray directory path and moved inode so replicas can relink the inode under their stray dentry and preserve snaprealm state.

Fragmentation flow begins with balancer/admin-triggered split or merge. The code validates that the filesystem is writable, not degraded, not in stray/system/root directories, not quiesced, and auth-owned. It freezes source dirfrags, pins their dentries, waits for completion/freeze, acquires dirfrag tree and scatter locks, performs the in-memory refragmentation, journals an `EFragment::OP_PREPARE`, stores new dirfrag objects, notifies replicas, journals `OP_COMMIT`, removes or truncates old dirfrag objects, journals `OP_FINISH`, drops locks after required notify ACKs, and finally unpins/unmarks result fragments. Recovery can finish committed fragments or journal rollback entries to restore old frags.

Scrub and repair flows create internal requests so they reuse MDCache locking, retry, and cleanup. Enqueue scrub traverses to an inode with path locks and hands a `ScrubHeader` to `ScrubStack`. Dirfrag repair auth-pins and locks a single complete dirfrag, recalculates `frag_info_t` and `nest_info_t`, and journals corrected fnode fields. Inode-stat repair fetches every dirfrag leaf, marks scatterlocks dirty, forces gather by taking read locks, and compares the inode-level projected stats after gather.

Quiesce path flow traverses to the root inode, creates `CEPH_MDS_OP_QUIESCE_INODE` subrequests recursively, and keeps the root request alive until the caller kills it. Each inode quiesce takes an xlock on `quiescelock`, cap-related locks, honors `F_QUIESCE_BLOCK`, optionally drops cap locks for split-auth mode while retaining the quiesce lock, recursively schedules children, and records aggregate state in the parent request's `quiesce_ops`. It also tries to abort still-freezing fragmentation/export paths asynchronously to avoid deadlocks.

Lock-path flow traverses once, drops traversal locks, parses configured `type:kind` lock strings, maps types such as `quiesce`, `snap`, `file`, `nest`, `dft`, `auth`, `link`, `xattr`, and `flock` to `SimpleLock` objects, acquires read/write/x locks, optionally drops auth pins for stealth mode, then deliberately leaves the request live until lifetime expiry or explicit kill.

Upkeep flow runs in a dedicated `mds-cache-trim` thread. It periodically samples memory, locks `mds_lock`, calls `check_memory_usage()`, trims client leases and metadata cache when the rank is trimmable, recalls client state with stronger flags if the cache is too full, and periodically calls `ceph_heap_release_free_memory()`.

Block-diff flow compares two snapshot inodes with matching layouts. It scans a bounded number of object IDs with RADOS `list_snaps`, aggregates clone lists, identifies the clone positions for both snap IDs, subtracts overlap regions, returns modified extents for the current scan window, advances `scan_idx`, and uses positive completion from `aggregate_snap_sets()` to tell callers to continue scanning.

## State And Persistence Behavior

The chunk mutates persistent metadata through the MDS journal and the metadata/data object stores. Fragmentation journals `EFragment` prepare/commit/finish/rollback records and persists new dirfrag objects before purging old ones. Uninline writes inline file data to the backing object, updates the `inline_version` xattr, then journals inode state changes. Repair paths journal `EUpdate` entries with corrected fnode/inode state. Snaprealm updates serialize snap blobs to peer MDS ranks and client snap traces, while backtrace fetches read the persistent `"parent"` xattr from inode objects.

The dominant in-memory state includes `active_requests`, `opening_inodes`, `find_ino_peer`, `discovers`, `waiting_for_base_ino`, `inode_map`, `snap_inode_map`, `subtrees`, `fragments`, `uncommitted_fragments`, `export_pin_delayed_queue`, `export_ephemeral_pins`, `strays[]`, and queue state in `stray_manager` and `recovery_queue`.

Locking state is part of both request and metadata-object persistence semantics. `MutationImpl::locking_state` flags remember path/snap/all-lock progress. Individual `SimpleLock`, scatterlock, auth pin, remote auth pin, cache pin, and freeze states control when retries are scheduled and when requests may finish.

Fragment state is especially durable. `fragment_info_t` tracks the live in-memory operation, result frags, notify ACKs, deadlock-detection counters, and the owning request. `ufragment` tracks uncommitted log-segment state, old frags, rollback buffer, and waiters. The log segment's `uncommitted_fragments` set ties cleanup/recovery to mdlog trimming.

Quiesce state intentionally keeps internal requests live so locks are retained. The parent `CEPH_MDS_OP_QUIESCE_PATH` request owns the aggregate `QuiesceState`, and child `CEPH_MDS_OP_QUIESCE_INODE` requests keep quiesce locks until the parent operation is killed/cleaned. `request_cleanup()` explicitly tears down quiesce children from `mdr->more()->quiesce_ops`.

Admin dump state can be large but is output-only. `dump_cache()` writes either formatter sections or a new exclusive `cachedump.<epoch>.mds<rank>` file, respects configured cache-size thresholds, and can time out after every 1000 dumped inodes.

## Dependencies And Integration Points

This code depends on core MDS types and subsystems: `MDSRank`, `Server`, `Locker`, `Migrator`, `MDBalancer`, `MDLog`, `Objecter`, `SnapClient`, `SessionMap`, `DamageTable`, `ScrubStack`, `StrayManager`, `PurgeQueue`, `MDSMap`, `PerfCountersBuilder`, `MemoryModel`, `Striper`, and RADOS object operations.

It integrates with CephFS protocol messages including `MClientRequest`, `MMDSOpenIno`, `MMDSOpenInoReply`, `MMDSFindIno`, `MMDSFindInoReply`, `MDiscover`, `MDiscoverReply`, `MMDSSnapUpdate`, `MClientSnap`, `MDirUpdate`, `MDentryLink`, `MDentryUnlink`, `MMDSFragmentNotify`, and `MMDSFragmentNotifyAck`.

The mdlog integration is central: `EUpdate`, `EFragment`, `EMetaBlob`, log segments, and mutation callbacks decide when projected metadata becomes committed, when old objects may be purged, and when locks can be dropped. Many callbacks are `MDCacheContext`, `MDCacheLogContext`, `MDCacheIOContext`, `MDSInternalContext`, or `MDSIOContext` subclasses that re-enter MDCache after async I/O or logging.

Client-facing integration happens through `Server::dispatch_client_request()`, `respond_to_request()`, `rdlock_path_pin_ref()`, `recall_client_state()`, `force_clients_readonly()`, client snap updates, cap export via `Migrator`, and lock/cap recall through `Locker`.

Admin integration includes asok-style stray dumps, cache dumps, scrub enqueue, repair stats, flush dentry, lock path, quiesce path, inode/dir dumps, and performance counters under the `mds_cache` namespace.

## Risks And Edge Cases

The traversal API has many flag combinations. Misusing `MDS_TRAVERSE_DISCOVER`, `PATH_LOCKED`, `WANT_DENTRY`, `WANT_INODE`, `WANT_AUTH`, snap-lock flags, or xlock flags can cause incorrect forwarding, missing locks, null dentry exposure, or waiters that retry in the wrong state.

The code relies heavily on `ceph_assert()` for invariants. Unexpected states such as missing fragment records, bad dentry linkage, malformed lock-path strings after partial acquisition, missing dirfrag during fragment notify, corrupt backtrace decode, or inconsistent subtree maps can abort the MDS rather than returning an error.

Remote/discovery races are subtle. Replies can be duplicate or obsolete, authorities can change, dirfrags can refragment while discovery is in flight, dentries can be xlocked/frozen, and remote dentries can point at damaged or missing inodes. The code uses auth hints, waiters, tid maps, and retry factories to mitigate this, but this is a high-risk integration area.

Request cleanup is high blast radius. Leaking locks, pins, session links, quiesce children, or active map entries can hang clients or block cache trimming. Premature cleanup can drop quiesce/lock-path locks that are intentionally held past callback completion.

Fragmentation has multiple crash/recovery windows. The prepare/store/notify/commit/purge/finish sequence must match `uncommitted_fragments` recovery behavior. Errors around notify ACK waits, old-frag purge, rollback old-frag reconstruction, or subtree-map updates can leave peers with inconsistent dirfragtree or cache authority state.

Quiesce can deadlock with fragmentation/export/freezing unless the asynchronous overdrive paths keep working. The code explicitly aborts fragment operations before all source dirs freeze and asks the migrator to overdrive export. Regressions in this area can block subvolume quiesce or metadata operations indefinitely.

`dump_cache()` is intentionally guarded because dumping large caches can hang or kill an MDS. Raising thresholds or using formatter output on huge caches is operationally risky.

Repair helpers recalculate and journal metadata stats, so mistakes can persist incorrect accounting. They also depend on complete dirfrags and scatter-gather behavior; damaged dirfrags return `-EIO`, but less obvious logical corruption may only be logged as "failed to fix".

`aggregate_snap_sets()` assumes useful clone ordering and uses `std::prev(clones.end())` when a snap is not found. Empty clone lists would be dangerous unless RADOS `list_snaps` guarantees a head entry for successful results. This deserves focused coverage because it is near the end of the chunk and uses external object metadata.

## Test Signals

Path traversal tests should cover local auth hit, incomplete dir fetch, non-auth discover, forwarding to auth, ambiguous auth wait, snapdir name resolution, damaged dirfrag/dentry/remote inode, null dentry creation, remote dentry opening, path locks, dentry xlocks, and quiesced-parent import behavior.

Open-by-inode tests should cover cached inode hits, peer-discovered auth rank without replica materialization, peer-discovered replica materialization, backtrace fetch and decode failure, stale/empty backtrace, pool retry, parent-open retry, batched dir fetch, peer failure/kick behavior, and all-peers-checked failure.

Request lifecycle tests should verify duplicate client request handling, forward-race behavior against peer requests, internal request counters, peer commit reentry, killed committing requests, quiesce child cleanup, lock/pin/session release, replay queue progression, and request forwarding of internal operations as `-EXDEV`.

Discovery/replica tests should exercise discover of base inode, base dirfrag, nested path, xlocked tail with and without path-locked permission, frozen inode/dir wait, non-auth auth-hint replies, incomplete-dir fetch-and-retry, null dentry replies, duplicate discover replies, replica dir/dentry/inode decode, alternate dentry names, lock recovery flags, and stray replica encode/decode.

Dentry link/unlink tests should include primary link, remote link, witness skip, peer state skip, unlink to stray with snap blob, remote unlink without stray, cap export after replica unlink, and trim race for decoded stray dentries.

Fragmentation tests should cover split and merge, refusal under read-only/degraded/stray/root/system/quiesced/scrub/frozen/not-auth conditions, freeze waits, incomplete dir fetch before marking, prepare mdlog content, storing result frags, notify ACK wait, old object removal/truncation, finish cleanup, stale freeze cancellation, rollback before and after commit, subtree-root fragmentation, and peer `MMDSFragmentNotify` decode.

Scrub/repair/uninline/flush tests should cover successful enqueue with generated and explicit tags, busy scrub rejection, uninline success and OSD failure, inline-version compare behavior, MDSDIR skip, dirfrag stats no-op and repair journal path, inode stats scatter-gather path, damaged dirfrag `-EIO`, rdlock-only stats request, and flush of an auth inode.

Quiesce and lock-path tests should cover inactive MDS rejection, blocked quiesce policy, split-auth true/false behavior, recursive child scheduling, trimmed child inode, already-quiesced conflict, fragment/export overdrive, failed-child propagation, parent kill cleanup, lock string parse errors, every supported lock type/kind, `ap_dont_block`, `ap_freeze`, stealth auth-pin drop, and lifetime cancellation.

Maintenance and admin tests should cover cache dump threshold and timeout behavior, formatter/file output paths, subtree display assertions in debug builds, MDSMap max_mds export-pin draining, ephemeral pin redistribution, upkeep trim intervals, cache-toofull recall flags, and heap free-memory release interval.

Block-diff tests should cover differing layouts, equal object extents, EOF growth extents, truncation, bounded scan windows, RADOS `list_snaps` `-ENOENT` handling, nonzero error propagation, same-clone no-op, overlap subtraction, holes, `scan_idx` advancement, and repeated calls until completion.

## Cross-Chunk Notes

This chunk depends on earlier `MDCache.cc` code for constructors, cache insertion/removal, subtree auth primitives, journaling helpers, trimming/shutdown logic, and many caller paths. It also depends on `MDCache.h` for state structs and public declarations. The final per-file MDCache research should reconcile this chunk with earlier trim/recovery/rejoin code and with later code if any exists beyond line 14808.
