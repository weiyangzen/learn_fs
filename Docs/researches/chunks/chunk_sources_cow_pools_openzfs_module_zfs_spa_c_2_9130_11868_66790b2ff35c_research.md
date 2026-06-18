# Chunk Research: sources/cow-pools/openzfs/module/zfs/spa.c lines 9130-11868

## Scope

This chunk covers the tail of SPA device manipulation, SPA scanning wrappers, asynchronous SPA task processing, transaction group syncing, sync taskq allocator selection, miscellaneous SPA helpers, activity waiters, kernel sysevent posting, exported symbols, and the final module parameters in `spa.c`.

## APIs and Entry Points

- `spa_vdev_split_mirror()` splits selected mirror leaves into a newly created pool, including log reset, config rewriting, per-vdev ZAP transfer, new SPA assembly, property application, original-pool detach/free, and rollback on failure.
- `spa_vdev_resilver_done_hunt()` and `spa_vdev_resilver_done()` locate completed replacements/spare detach candidates and detach them automatically after resilver or rebuild completion.
- `spa_vdev_setpath()` and `spa_vdev_setfru()` update leaf vdev path/FRU strings through `spa_vdev_set_common()`.
- `spa_scrub_pause_resume()`, `spa_scan_stop()`, `spa_scan()`, and `spa_scan_range()` are public scan control wrappers around DSL scan/scrub operations.
- `spa_async_suspend()`, `spa_async_resume()`, `spa_async_request()`, and `spa_async_tasks()` manage pending async SPA work and suspension of async/removal/background zthreads.
- `spa_sync()` is the main TXG sync entry point; `spa_sync_allpools()` forces all active writeable unsuspended pools to sync.
- `spa_sync_tq_create()`, `spa_sync_tq_destroy()`, `spa_acq_allocator()`, `spa_rel_allocator()`, and `spa_select_allocator()` manage sync taskq threads and allocator assignment for write ZIOs.
- `spa_evict_all()`, `spa_lookup_by_guid()`, `spa_upgrade()`, `spa_has_l2cache()`, `spa_has_spare()`, and `spa_total_metaslabs()` provide pool lifecycle, lookup, upgrade, aux-vdev, and accounting helpers.
- `spa_notify_waiters()`, `spa_wake_waiters()`, `spa_wait_tag()`, and `spa_wait()` implement userspace-visible waits for pool activities.
- `spa_event_create()`, `spa_event_post()`, and `spa_event_notify()` wrap kernel ZFS event creation/posting and no-op in libzpool userland.
- `EXPORT_SYMBOL()` declarations expose state, device, aux-vdev, scan, sync, property, and event functions to the kernel module boundary.

## Key Control Flow

Mirror split:
1. `spa_vdev_split_mirror()` enters vdev config context, rejects active/discarding checkpoints, passivates slog state, resets logs, and verifies the target pool name is unused.
2. It validates the supplied vdev-tree nvlist: child count must match the original root excluding trailing holes/logs, and the split config must not include spares or L2ARC.
3. For each child, it accepts matching holes/logs and indirect vdevs, otherwise looks up the selected leaf GUID, requires a healthy writeable concrete non-log non-spare non-l2cache leaf under a mirror, and rejects DTL/resilver-needed devices.
4. It copies top-level metaslab/asize/ashift data plus leaf/top ZAP object IDs into the new config, offlines split leaves, records `ZPOOL_CONFIG_SPLIT`, and dirties the original root config.
5. It creates `newspa`, marks AVZ rebuild state, activates it, suspends its async work, stops initialize/TRIM on split leaves, and imports the new pool using `SPA_CONFIG_SRC_SPLIT` and `SPA_IMPORT_ASSEMBLE`.
6. On success it generates the new pool config, applies properties, syncs the new config, resumes async work, re-enters the original pool, removes DTL list references, calls `vdev_split()`, logs detach history, frees detached vdevs, rebuilds the original AVZ, and optionally exports the new pool.
7. On failure after `newspa` creation it unloads/deactivates/removes the new SPA, re-onlines original leaves, requests initialize/TRIM/autotrim restarts, reopens the root vdev, clears split config state, and exits with the original error.

Resilver completion:
1. `spa_vdev_resilver_done_hunt()` recursively searches children first.
2. For `vdev_replacing_ops`, it detaches the oldest child when the newest child has empty missing/outage DTLs and the old child is no longer required.
3. For `vdev_spare_ops`, it honors `vdev_unspare`, propagates state, and may free extra shared spares when redundant spares are no longer required.
4. `spa_vdev_resilver_done()` holds `SCL_ALL`, gathers GUIDs, drops the config lock to call `spa_vdev_detach()`, repeats until no candidates remain, then notifies waiters when no detach occurred.

Scanning and async work:
1. Scan control rejects pause/stop while resilvering, rejects invalid scan functions, requires `SPA_FEATURE_RESILVER_DEFER` for resilver scans, allows txg ranges only for scrub, and requires `SPA_FEATURE_HEAD_ERRLOG` for error scrub.
2. `spa_async_thread()` snapshots and clears `spa_async_tasks`, then processes config updates, removals, autoexpand notifications, faulting/suspension, resilver/rebuild completion, resilver restart, initialize/TRIM/autotrim restarts, L2ARC trim, and L2ARC rebuild.
3. Async dispatch creates one thread only when tasks are pending, async is not suspended, and no async thread exists. Config-update retries can be throttled by `spa_ccw_fail_time` and `zfs_ccw_retry_interval`.

TXG sync:
1. `spa_sync()` waits open-context IO for the TXG, applies pending BRT updates, enters config locks, converts state-dirty vdevs into config-dirty vdevs, creates an assigned tx, arms the deadman timer, handles legacy RAIDZ deflate upgrade state, adjusts queue depths, and starts indirect-map condensing if needed.
2. `spa_sync_iterate_to_convergence()` loops sync passes: syncs pool config and aux devices, error logs, DSL pool, frees/deferred frees, BRT/DDT, scan/error-scrub, removal, upgrades, metaslab flushes, and vdev syncs until the MOS stops being dirty.
3. The first sync pass has special no-op detection and an extra config sync after sync tasks, because sync tasks can dirty config and should still make the TXG non-no-op.
4. `spa_sync_rewrite_vdev_config()` writes the uberblock/config either to a random minimum set of visible top-level vdevs when no config is dirty, or to all root children when config is dirty; label write failures suspend IO and retry after resume.
5. After commit, `spa_sync()` clears dirty config, publishes `spa_config_syncing`, completes DSL/vdev sync state, evicts old metaslabs, closes syncing log spacemaps, updates dspace/autotrim, asserts no late dirty state, updates `spa_ubsync`, exits config lock, handles ignored writes, and dispatches async tasks.

Waiters and events:
1. Waiters increment `spa_waiters` under `spa_activities_lock`, close the SPA reference to avoid blocking export/destroy, then loop checking activity state and waiting on `spa_activities_cv`.
2. Activity checks cover checkpoint discard, async free/livelist delete, initialize/trim by optional vdev GUID tag, replace, remove, resilver/rebuild, scrub, and RAIDZ expansion.
3. Locking intentionally holds `spa_activities_lock` during state checks but may drop/reacquire it to acquire config or vdev initialize/trim locks in the same order used by completing threads.
4. `spa_wake_waiters()` cancels waiters during export and blocks until `spa_waiters` reaches zero.
5. Kernel builds create zevents through `zfs_event_create()` and post them via `zfs_zevent_post()`; userland libzpool compiles these paths as no-ops.

## State and Dependencies

Important mutated SPA/vdev state includes `spa_config_splitting`, `spa_avz_action`, `spa_config_txg`, `spa_config_source`, `spa_is_splitting`, `spa_async_tasks`, `spa_async_suspended`, `spa_async_thread`, `spa_config_dirty_list`, `spa_state_dirty_list`, `spa_config_syncing`, `spa_syncing_txg`, `spa_sync_pass`, `spa_ubsync`, `spa_uberblock`, `spa_waiters`, `spa_waiters_cancel`, vdev offline flags, vdev initialize/TRIM state, vdev DTL lists, aux-vdev `sav_sync`/`sav_object`, allocator rotors, and sync-thread allocator assignment.

Major dependencies include nvlist/fnvlist config APIs, vdev tree operations, per-vdev ZAP/AVZ operations, DSL scan/scrub/rebuild machinery, BRT/DDT/svr/removal sync paths, bpobj/bplist free processing, ZIO sync/free/config-label IO, metaslab class balancing/eviction, zthr/taskq/thread primitives, SPA namespace/config/state locks, ZAP/MOS object updates, feature flags, sysevent/zevent APIs, and exported kernel module parameter macros.

## Risks and Edge Cases

- `spa_vdev_split_mirror()` calls `nvlist_lookup_string(props, ...)` before the later `props != NULL` guard; callers must pass a valid props nvlist or this path risks a null dereference depending on nvlist API behavior.
- Mirror split mutates the caller-provided `config` nvlist in place by adding pool identity, state, version, per-vdev ZAPs, metaslab info, and split metadata.
- The split child-count logic treats trailing holes/logs specially via `lastlog`; unusual root layouts can fail validation even before per-child GUID checks.
- Split validation skips indirect vdev children and config holes, so `vml[c]` can remain `NULL`; later loops depend on repeated null checks.
- During split, selected leaves are marked offline and the root is reopened before the new pool is fully loaded. The rollback path restores this, but injected panics and mid-operation failures are explicitly modeled.
- If `dmu_tx_assign()` fails during final original-pool update, the code still calls `vdev_split()`/`vdev_free()` and exits `spa_vdev_exit(..., 0)` while suppressing history commit; this relies on preceding sync/import work and surrounding invariants.
- `spa_vdev_resilver_done()` drops `SCL_ALL` before detach, so it stores GUIDs rather than vdev pointers; callers must tolerate topology changes between hunt and detach.
- `spa_async_request()` only sets bits; dispatch happens later from sync/end paths, so requested work can remain pending while async is suspended or config update retry throttling is active.
- `spa_sync_iterate_to_convergence()` can keep looping while MOS dirty state is regenerated; config sync is deliberately limited after pass 1 to avoid self-dirtying non-convergence.
- `spa_sync_rewrite_vdev_config()` retries forever after label-write failure, suspending and waiting for IO resume each time.
- Waiter activity checks mix lock domains. The comments document missed-wakeup prevention, but future activity types must preserve the lock ordering with `spa_activities_lock`.
- `spa_rel_allocator()` clears `sau_inuse` without taking `sau_lock`, unlike acquisition; this appears to depend on external serialization or benign per-sync-thread ownership.

## Cross-Chunk References

- `spa_vdev_split_mirror()` follows the attach/detach implementation from the previous chunk; it calls `vdev_split()` and shares detach/history semantics with earlier device-manipulation code.
- `spa_vdev_resilver_done_hunt()` explicitly relies on child ordering established by `spa_vdev_attach()` earlier in `spa.c`.
- `spa_vdev_resilver_done()` calls `spa_vdev_detach()`, defined before this chunk, to remove completed replacement/spare leaves.
- `spa_sync_config_object()` comments refer back to earlier config-dirty and vdev-ZAP setup behavior around pool load/import and vdev changes.
- The chunk ends at the final line of `spa.c`; final merge should connect this report with earlier chunk coverage for file-level initialization, import/open/create/destroy, property validation, and the attach/detach paths.