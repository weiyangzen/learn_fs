# File Research: sources/cow-pools/openzfs/module/zfs/spa.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9129, source bytes 262084, report `Docs/researches/chunks/chunk_sources_cow_pools_openzfs_module_zfs_spa_c_1_1_9129_9ff803a65085_research.md`
- chunk 2: lines 9130-11868, source bytes 78596, report `Docs/researches/chunks/chunk_sources_cow_pools_openzfs_module_zfs_spa_c_2_9130_11868_66790b2ff35c_research.md`

## Chunk Research

### Chunk 1: lines 1-9129

# Chunk Research: sources/cow-pools/openzfs/module/zfs/spa.c lines 1-9129

## Scope

This chunk covers the beginning and majority of OpenZFS `spa.c`, the Storage Pool Allocator implementation for pool properties, activation/deactivation, pool load/open/import/create/export, auxiliary vdev loading, MMP activity checks, livelist maintenance workers, and the first device-management APIs through vdev initialize/TRIM. The requested range stops at line 9129 in the middle of the device manipulation section; later vdev removal/split/setpath/sync definitions are cross-chunk dependencies.

## Primary APIs and Responsibilities

- `spa_prop_get_nvlist()`, `spa_prop_get()`, `spa_prop_set()`, `spa_prop_clear_bootfs()`: user-visible and internal pool property retrieval/update. They combine live in-core metrics, MOS ZAP-backed properties, user properties, feature flags, and special handling for `bootfs`, `cachefile`, `multihost`, and suspended-pool failure mode.
- `spa_configfile_set()`: updates the in-core cachefile list from `ZPOOL_PROP_CACHEFILE` and optionally schedules `SPA_ASYNC_CONFIG_UPDATE`.
- `spa_change_guid()`: validates checkpoint/health/namespace constraints, runs a sync task to update the root vdev GUID/guid sum, then updates cachefile and posts a reguid event.
- `spa_config_parse()`: recursively allocates a vdev tree from an nvlist using `vdev_alloc()`.
- `spa_taskq_dispatch()`: routes `zio_t` work to per-pool, per-I/O-type taskqs, with allocator-stable dispatch for write issue queues.
- `spa_load_spares()`, `spa_load_l2cache()`, `spa_l2cache_drop()`: load, validate, activate, publish, and drop auxiliary vdevs for hot spares and L2ARC devices.
- `spa_load()`, `spa_load_best()`, `spa_open()`, `spa_open_rewind()`, `spa_import()`, `spa_tryimport()`: pool load/open/import orchestration, including retry/rewind behavior and tryimport diagnostics.
- `spa_create()`: full pool creation path: namespace insertion, vdev tree creation, aux vdev validation, DSL pool/DDT/BRT creation, MOS object setup, feature/property initialization, sync startup, cachefile write, events.
- `spa_destroy()`, `spa_export()`, `spa_reset()`: wrappers around `spa_export_common()` for state transition and unload.
- `spa_vdev_add()`, `spa_vdev_attach()`, `spa_vdev_detach()`, `spa_vdev_initialize()`, `spa_vdev_trim()`: beginning of the device manipulation surface in this chunk.

## Control Flow

Property retrieval starts with `spa_prop_get_config()`, which requires `spa_props_lock` and emits live values from the root vdev, metaslab classes, DSL pool accounting, DDT/BRT statistics, checkpoint info, feature-derived max block/dnode sizes, altroot, compatibility, and cachefile state. `spa_prop_get()` then walks the MOS pool properties ZAP, translating numeric and string entries into the standard `{source,value}` nvlist form and resolving `bootfs` object IDs to dataset names. Setting properties first calls `spa_prop_validate()`, which mutates `bootfs` strings into dataset object IDs and enforces feature/version, boolean, cachefile path, comment, and multihost hostid constraints. `spa_prop_set()` chooses between version sync tasks, feature activation, or generic `spa_sync_props()`.

Pool activation is split from loading. `spa_activate()` moves an uninitialized `spa_t` to `POOL_STATE_ACTIVE`, sets mode/final txg/read-spacemaps state, creates normal/log/embedded/special/dedup metaslab classes, creates ZIO taskqs, per-txg root zios, dirty/error lists, OS activation, keystore, zvol/metaslab/prefetch/upgrade taskqs. `spa_deactivate()` is the inverse: waits for evicting objsets, destroys taskqs and lists, waits for txg zios, destroys metaslab classes, drains errlogs, finalizes keystore and OS state, and joins the optional illumos spa process.

`spa_unload()` tears down a loaded pool. It removes import progress, wakes waiters, optionally flushes txg-time and log spacemap state before final txg selection, suspends async work, stops initialize/TRIM/autotrim/rebuild/L2ARC rebuild, stops txg sync and MMP, waits for async zios, destroys removal/condense/checkpoint/livelist/raidz zthreads, closes bpobjs, frees the vdev tree and DSL pool, unloads DDT/BRT/log spacemap metadata, drops L2ARC, frees aux vdev lists, clears comments/compatibility, and leaves `spa_checkpoint_txg`/raidz state reset. Export paths intentionally set `spa_final_txg` before unload so unload does not redo final-TXG prep.

Pool load is implemented as a staged state machine:

1. `spa_ld_mos_init()` parses the supplied config, opens and validates vdevs, selects the best uberblock, performs MMP activity checks when required, verifies features-for-read from the selected label, and opens the MOS rootbp through `dsl_pool_init()`.
2. `spa_ld_trusted_config()` loads the MOS config object, verifies host ownership on open, rebuilds a trusted vdev tree, copies device paths from the untrusted tree when needed, reopens and validates vdevs, checks for missing top-level vdev hazards, performs the MMP claim phase for write imports, checks missing log devices, and verifies guid sums.
3. `spa_ld_mos_with_trusted_config()` runs those stages and reloads if the MOS config differs enough from the supplied config to risk an involuntary extreme rewind.
4. `spa_load_impl()` optionally rewinds to checkpoint state and reloads, drops the namespace lock for long work, then reads checkpoint txg, initializes indirect-vdev/removal metadata, checks full feature flags, opens DSL special directories, loads properties, opens aux vdevs, loads vdev metadata/log spacemaps, DDT, BRT, verifies logs and data, updates deflated-space accounting, and if writable starts import completion: raidz reflow scratch copy, ZIL claim, txg sync/MMP start, config update scheduling, resilver/rebuild restart, history logging, removal/livelist/checkpoint/condense worker startup, inconsistent objset cleanup, temp userref cleanup, initialize/TRIM/autotrim restart, and L2ARC rebuild request.
5. `spa_load_best()` wraps `spa_load()` with retry/rewind policy. It preserves initial load info for non-recovery loads, records rewind diagnostics, and avoids retrying for checkpoint absence, remote MMP activity, stale host/config cases, and user interruption.

Open/import/create/export share namespace discipline. `spa_open_common()` looks up an existing `spa_t`, activates and loads it on first open, handles stale cachefile `EBADF` by removing the namespace entry and cachefile, returns config/load info on failures, and creates zvol minors after first successful open. `spa_import()` creates a new `spa_t` from user config, supports verbatim import, suspends async work until load and property setting succeed, allows read-only mode from props, overrides aux-device definitions with user-supplied devices after load, resumes async work, updates cachefile, schedules autoexpand, logs history, posts import events, and creates zvol minors. `spa_tryimport()` creates a temporary read-only spa named with `TRYIMPORT_NAME`, forces missing-log tolerance to collect more complete diagnostics, returns generated config/load info/bootfs/aux stats if a root vdev was parsed, and always unloads/removes the temporary spa.

Creation (`spa_create()`) is a one-way path after vdev/metaslab instantiation. It validates namespace uniqueness and properties, detects enabled feature properties including encryption/allocation-classes/dRAID/dRAID fail domains, rejects special vdevs without allocation-class support, parses/creates root vdevs and virtual dRAID spares, validates aux devices, expands top-level metaslabs, creates aux lists, creates the DSL pool, DDT and BRT, allocates MOS objects for config, creation version, deflate, deferred frees, checksum salt, history, properties/features, starts txg sync and MMP, waits for initial txg, spawns aux threads, writes cachefile, and imports OS/zvol state.

Export/destroy/reset use `spa_export_common()`. It rejects read-only global mode, serializes with `spa_is_exporting`, holds a temporary pool reference, suspends async and zvol minors, waits for sync/eviction, rejects active references and injection refs, blocks non-forced export when an active shared spare exists, stops initialize/TRIM/autotrim/rebuild/L2ARC rebuild, marks final on-disk state dirty unless hard-forced, flushes txg-time/log spacemaps when needed, sets `spa_final_txg`, unloads/deactivates, writes cachefile removal and namespace removal for true export/destroy, and wakes namespace waiters.

Device management begins with `spa_vdev_add()`, which enters vdev config mutation, parses a candidate root, validates it has children or aux devices, creates new top-level vdevs and dRAID spares, validates aux devices, rejects incompatible additions during removal/indirect-vdev history, optionally enforces ashift uniformity, splices new top-level children into the root vdev, merges aux configs, increments dRAID features through sync tasks, exits through `spa_vdev_exit()`, and then calls `spa_config_update()` so added vdevs are config-synced before metaslabs are initialized for allocation. `spa_vdev_attach()` handles mirror attach, replacement, rebuild, and raidz expansion. It rejects checkpoint activity, rebuild/resilver/removal conflicts, unsupported topology, spare/log/special/dRAID-spare mismatches, too-small or ashift-incompatible devices, unsafe raidz expansion cases, inserts mirror/replacing/spare parents when needed, marks DTLs, starts resilver/rebuild or raidz attach sync, posts events, commits config, and logs history. `spa_vdev_detach()` rejects checkpoint and topology/race hazards, checks DTL safety, erases labels, removes and compacts children, handles unspare removal across all pools, collapses one-child mirror/replacing/spare parents, autoexpands if configured, marks detached DTL cleanup, posts events, exits vdev config, logs history, and may call `spa_vdev_resilver_done()` for follow-up spare cleanup.

`spa_vdev_initialize()` and `spa_vdev_trim()` are batch wrappers over per-vdev helpers. Both hold the namespace lock across the batch, validate each GUID under config/state locks, take per-vdev initialize/TRIM locks, reject detached/non-leaf/non-concrete/non-writeable devices and incompatible command states, start/cancel/suspend/uninitialize or start/cancel/suspend TRIM, collect per-GUID errors in an nvlist, wait for stopped worker threads, sync state to disk, and return an error count.

## State and Data Structures

- Global tunables include taskq sizing (`zio_taskq_batch_pct`, `zio_taskq_batch_tpq`, `zio_taskq_write_tpq`), load verification (`spa_load_verify_*`), missing top-level vdev allowances, txg-time logging intervals, and livelist test pause/cancel counters.
- `spa_t` state touched here includes `spa_state`, `spa_mode`, `spa_final_txg`, `spa_first_txg`, `spa_load_state`, `spa_load_max_txg`, `spa_extreme_rewind`, `spa_load_info`, `spa_config_source`, `spa_trust_config`, `spa_missing_tvds*`, `spa_activity_check`, `spa_async_suspended`, `spa_sync_on`, `spa_claiming`, `spa_claim_max_txg`, `spa_checkpoint_txg`, `spa_checkpoint_info`, `spa_failmode`, `spa_autoreplace`, `spa_autoexpand`, `spa_multihost`, `spa_autotrim`, `spa_dedup_table_quota`, `spa_avz_action`, `spa_feat_refcount_cache`, `spa_feat_stats`, and several zthread/taskq/list fields.
- Vdev state is manipulated through `vdev_state`, `vdev_guid`, `vdev_guid_sum`, `vdev_top`, `vdev_parent`, `vdev_children`, `vdev_islog`, `vdev_isspare`, `vdev_isl2cache`, `vdev_detached`, `vdev_rz_expanding`, `vdev_removing`, DTLs, metaslab arrays, aux pointers, paths/devids, initialize/TRIM state and worker thread pointers.
- Persistent MOS objects loaded or created include pool config, deferred-free bpobj, pool properties, features-for-read/write/descriptions/enabled-txg, error logs, scrub txg, deleted clones/livelists, history, spares, l2cache, all-vdev-ZAP map, checksum salt, txg-time RRD ZAP entries, and checkpoint uberblock.
- Synchronization is layered: namespace lock serializes pool lifecycle, `spa_config_enter()` SCL locks protect config/state/allocation trees, DSL pool config locks protect dataset/property walks, per-vdev locks serialize initialize/TRIM state transitions, `spa_props_lock` protects property/claim counters, `spa_feat_stats_lock` protects cached feature stats, and txg sync tasks perform on-disk mutations.

## Dependencies and Integration Points

This chunk depends broadly on OpenZFS subsystems:

- Vdev layer: allocation/open/validate/create/load/reopen/free/config-generate/config-sync/state/DTL/metaslab operations, raidz/dRAID expansion and spare helpers, device initialize/rebuild/TRIM/autotrim.
- DSL/DMU/ZAP: `dsl_pool_*`, `dsl_dataset_*`, `dsl_dir_*`, `dsl_sync_task*`, `dmu_tx_*`, `dmu_objset_*`, `zap_*`, object allocation/read/update, deadlist/bplist/bpobj operations.
- ZIO/ZIL/scan: root zios, async zio roots, `zio_read/free/wait/nowait`, ZIL claim/reset/check, scrub/resilver scan restart and traversal.
- Feature, dedup, block cloning, and removal: `spa_feature_*`, `spa_features_check()`, `ddt_*`, `brt_*`, `spa_remove_init()`, `spa_condense_init()`.
- MMP: uberblock activity detection and claim through `mmp_*`, hostid/hostname label fields, import progress reporting.
- ARC/L2ARC and OS integration: L2ARC add/remove/rebuild, zvol minors, sysevents, ereports, cachefile writes, platform-specific taskq/process hooks.

## Risks and Edge Cases

- Import safety depends on distinguishing untrusted cachefile/scan configs from trusted MOS configs. Missing top-level vdev tolerance is deliberately restricted; writable imports with missing top-level vdevs are rejected once the config is trusted.
- MMP import has two phases: passive observation during tryimport/open and active claim for writable import. Incorrect hostid, stale tryimport info, interrupted waits, or changed uberblocks return distinct errors and load-info diagnostics.
- Checkpoint presence blocks GUID changes, attach, and detach paths to avoid orphaning checkpointed metadata. Checkpoint rewind rewrites the checkpoint uberblock with a newer txg/timestamp for writable rewind, then reloads from that state.
- Log devices are special: missing log devices can either fail import or clear/drop ZIL depending on `ZFS_IMPORT_MISSING_LOG`; slog metaslab groups can be passivated/reactivated while checking logs.
- `spa_load_verify()` can issue speculative scrub-priority reads bounded by ARC-size-derived in-flight bytes; metadata/data error thresholds and dry-run mode affect whether load fails or only records diagnostics.
- Livelist condense/delete workers split expensive open-context processing from syncing-context mutations. The condense path explicitly accounts for block pointers appended while the worker was processing old entries.
- `spa_vdev_add()` intentionally syncs config before new metaslabs become allocatable, preventing post-crash DVAs from referencing vdevs absent from cache/labels.
- Replacement/detach code guards several races: parent GUID mismatch during detach, double-spare insertion, in-place replacement path aliasing, replacement completion racing with user detach, unspare GUID changes, and DTL-only-copy safety.
- Export must handle dirty objsets, active refs, active shared spares, zvol minor teardown, final TXG setting, and optional hardforce behavior that skips label/cachefile updates.

## Cross-Chunk References

- `spa_sync_version()` and `spa_sync_props()` are declared and called in this chunk but defined later, so the exact on-disk property/feature sync behavior is outside this range.
- `spa_has_active_shared_spare()` is declared and used by `spa_export_common()` but defined later.
- `spa_ld_log_spacemaps()` is called during vdev metadata load but its definition is outside this chunk.
- `spa_vdev_enter()`, `spa_vdev_exit()`, `spa_vdev_detach_enter()`, `spa_vdev_config_enter()`, and `spa_vdev_config_exit()` are heavily used by device mutation but are defined later.
- `spa_vdev_remove()` and `spa_vdev_resilver_done()` are called by detach/unspare logic, with their definitions after this chunk.
- `spa_sync_config_object()` is referenced by comments about deferred all-vdev-ZAP map initialization/destruction and by later sync logic outside this range.
- The requested range ends immediately before the next device-management API section continues, so removal/split/setpath and the main `spa_sync()` implementation are unresolved in this chunk.

### Chunk 2: lines 9130-11868

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
