# sources/distributed-fs/ceph/src/mds/MDCache.h

## Purpose

`MDCache.h` declares `MDCache`, the central in-memory metadata cache controller for a Ceph MDS rank. It owns inode and dirfrag lookup tables, subtree authority state, request tracking, cache trim policy, replay/rejoin/resolve state, strays, open-file tracking, file-size recovery, directory fragmentation, snaprealm coordination, replica/discovery messaging, and admin operations such as cache dumps, scrub enqueue, quiesce, path locking, and forced read-only mode.

## Important APIs, Types, And State

Discovery uses `discover_info_t`, `_create_discover`, `_send_discover`, `discover_base_ino`, `discover_dir_frag`, `discover_path`, and `kick_discovers`. Subtree authority management uses `adjust_subtree_auth`, `adjust_bounded_subtree_auth`, `try_subtree_merge`, `eval_subtree_root`, `get_subtree_bounds`, `project_subtree_rename`, `adjust_subtree_after_rename`, and summary helpers such as `get_auth_subtrees`.

Request handling exposes `request_start`, `request_start_peer`, `request_start_internal`, `request_finish`, `request_forward`, `dispatch_request`, `request_cleanup`, and `request_kill`, backed by `active_requests`. Mutation and journal helpers include `pick_inode_snap`, `cow_inode`, `journal_cow_dentry`, `journal_dirty_inode`, `project_rstat_*`, `broadcast_quota_to_client`, and `predirty_journal_parents`.

Recovery coordination is represented by `uleader`, `upeer`, `uncommitted_leaders`, `uncommitted_peers`, `ambiguous_peer_updates`, ambiguous import maps, `resolve_*` methods, and rejoin state such as `rejoin_gather`, `rejoin_imported_caps`, `cap_exports`, `cap_imports`, `rejoin_undef_inodes`, and `rejoin_done`. Path and object loading use `path_traverse`, `maybe_request_forward_to_auth`, `cache_traverse`, `open_remote_dirfrag`, `open_remote_dentry`, `open_ino`, `find_ino_peers`, and peer handlers for open/find replies.

Cache lifecycle includes `trim`, `trim_non_auth_subtree`, `standby_trim_segment`, `expire_recursive`, `trim_client_leases`, `check_memory_usage`, `shutdown_start`, `shutdown_check`, `shutdown_pass`, `shutdown`, and `shutdown_export_strays`. In-memory state includes `inode_map`, `snap_inode_map`, `root`, `myin`, `strays`, `subtrees`, `base_inodes`, `lru`, `bottom_lru`, memory thresholds, `Filer`, `OpenFileTable`, `StrayManager`, `RecoveryQueue`, `global_snaprealm`, `uncommitted_fragments`, `fragments`, and an upkeep thread.

## Control Flow And Persistence Behavior

`MDCache` is not a persistence format itself; it orchestrates when metadata changes become persistent through `MDLog`, `EMetaBlob`, inode/dirfrag store operations, purge queue work, and journaled segment references. Requests enter through `request_start*`, traverse paths with `path_traverse`, acquire locks/auth pins elsewhere, dirty or COW metadata with journal helpers, then finish through request cleanup and journal callbacks. Replay and rejoin rebuild cache and capability state from journal events and peer messages; ambiguous imports, uncommitted peer updates, and uncommitted fragments are retained until resolve/rejoin can prove the final authority and namespace state.

The cache open path initializes layouts, system inodes, root, `.ceph/mds*` hierarchy, stray dirs, and snaprealms. Shutdown is phased: stop or cap logging, trim, export strays, terminate sessions, journal subtree state, trim all possible segments, drop strays and system inodes, and wait for subtrees to empty. Directory fragmentation keeps rollback and old-frag state in `ufragment` and `fragment_info_t`; persistence depends on journaled fragment events plus follow-up store/purge completions.

## Dependencies And Integration Points

This header depends directly on MDS object types (`CInode`, `CDentry`, `CDir`), message types (`MDiscover`, `MMDSResolve`, `MMDSCacheRejoin`, `MMDSOpenIno`, `MCacheExpire`, `MDirUpdate`, fragment messages), `MDSContext`, `LogSegmentRef`, `Filer`, `RecoveryQueue`, `StrayManager`, and `OpenFileTable`. `MDLog` calls `create_subtree_map`, `advance_stray`, `standby_trim_segment`, and trim helpers. `MDSDaemon` and `MDSRankDispatcher` indirectly drive map handling, shutdown, and admin socket commands. `Locker`, `Migrator`, `MDBalancer`, event classes, and fragment context classes are friends because they need access to internal maps during replay, migration, locking, and journal event processing.

## Risks And Test Signals

The largest risks are state-machine coupling and lifecycle ordering: a wrong `MDSContext` completion can leave waiters pinned, a missed uncommitted-peer entry can trim or delete namespace state before commit, and a fragment or import rollback bug can corrupt subtree authority. Cache trim must avoid referenced dentries/inodes and must send correct expire messages to authoritative peers. Memory thresholds and upkeep thread behavior need tests for both ordinary trim pressure and read-only mode. Test signals should include multi-MDS failover/rejoin, standby replay, import/export interruption, fragmented directory split/merge rollback, strays purge after unlink/rename, cap reconnect, journal replay after crash at each shutdown and fragment killpoint, path traversal with forwarding/discovery, and admin operations such as `cache drop`, `dump cache`, `quiesce path`, and `lock path`.
