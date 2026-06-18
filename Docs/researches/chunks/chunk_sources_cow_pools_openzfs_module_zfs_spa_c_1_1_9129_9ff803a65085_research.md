# Chunk Research: sources/cow-pools/openzfs/module/zfs/spa.c lines 1-9129

## Scope

This chunk covers the beginning and majority of OpenZFS `spa.c`, the Storage Pool Allocator implementation for pool properties, activation/deactivation, pool load/open/import/create/export, auxiliary vdev loading, MMP activity checks, livelist maintenance workers, and the first device-management APIs through vdev initialize/TRIM. The requested range stops at line 9129 in the middle of the device manipulation section; later vdev removal/split/setpath/sync definitions are cross-chunk dependencies.

## Primary APIs and Responsibilities

- `spa_prop_get_nvlist()`, `spa_prop_get()`, `spa_prop_set()`, `spa_prop_clear_bootfs()`: pool property retrieval/update, combining live metrics, MOS ZAP-backed properties, user properties, feature flags, and special cases like `bootfs`, `cachefile`, `multihost`, and suspended-pool failure mode.
- `spa_configfile_set()`: updates the in-core cachefile list and optionally schedules `SPA_ASYNC_CONFIG_UPDATE`.
- `spa_change_guid()`: validates checkpoint/health/namespace constraints, updates the root vdev GUID/guid sum through a sync task, writes cachefile, and posts a reguid event.
- `spa_config_parse()`: recursively allocates a vdev tree from an nvlist using `vdev_alloc()`.
- `spa_taskq_dispatch()`: routes `zio_t` work to per-pool, per-I/O-type taskqs.
- `spa_load_spares()`, `spa_load_l2cache()`, `spa_l2cache_drop()`: load, validate, activate, publish, and drop auxiliary vdevs.
- `spa_load()`, `spa_load_best()`, `spa_open()`, `spa_open_rewind()`, `spa_import()`, `spa_tryimport()`: pool load/open/import orchestration, including retry/rewind and diagnostics.
- `spa_create()`: full pool creation path, including vdev creation, MOS setup, DDT/BRT creation, feature/property initialization, sync startup, cachefile write, and events.
- `spa_destroy()`, `spa_export()`, `spa_reset()`: wrappers around `spa_export_common()`.
- `spa_vdev_add()`, `spa_vdev_attach()`, `spa_vdev_detach()`, `spa_vdev_initialize()`, `spa_vdev_trim()`: first device-management APIs in this chunk.

## Control Flow

Property retrieval starts with `spa_prop_get_config()`, which requires `spa_props_lock` and emits live values from vdevs, metaslab classes, DSL accounting, DDT/BRT stats, checkpoint state, feature-derived limits, altroot, compatibility, and cachefile state. `spa_prop_get()` then walks the MOS pool properties ZAP. `spa_prop_validate()` enforces property rules and converts `bootfs` dataset names to object IDs before `spa_prop_set()` chooses version sync, feature activation, or generic `spa_sync_props()`.

`spa_activate()` initializes an uninitialized pool into active state: mode, txg roots, metaslab classes, taskqs, dirty/error lists, OS hooks, keystore, and worker taskqs. `spa_deactivate()` destroys those structures after unload and waits for outstanding txg zios and optional platform spa threads.

`spa_unload()` tears down a loaded pool: stops async work, initialize/TRIM/autotrim/rebuild/L2ARC rebuild, txg sync, MMP, async zios, removal/condense/checkpoint/livelist/raidz zthreads, DSL pool, vdev tree, DDT/BRT, log spacemap metadata, aux vdevs, comments, compatibility, and checkpoint/raidz transient state.

Pool load is staged:

1. `spa_ld_mos_init()` parses supplied config, opens/validates vdevs, selects uberblock, performs MMP checks, verifies label features-for-read, and opens MOS rootbp.
2. `spa_ld_trusted_config()` reloads the trusted MOS config, rebuilds the vdev tree, reopens/validates devices, checks missing-vdev hazards, performs MMP claim for write imports, checks missing logs, and validates guid sums.
3. `spa_ld_mos_with_trusted_config()` reloads if the MOS config differs enough to risk unintended rewind.
4. `spa_load_impl()` loads checkpoint txg, indirect-vdev metadata, features, DSL directories, properties, aux vdevs, vdev metadata, DDT/BRT, logs, and pool data; writable imports then claim ZIL blocks, start sync/MMP, update configs, restart resilver/rebuild/removal/initialize/TRIM/autotrim, spawn aux threads, and clean inconsistent state.
5. `spa_load_best()` wraps load retry and rewind policy.

`spa_open_common()` handles first open, activation, load, stale-cachefile cleanup, returning config/load info on failure, and zvol minor creation. `spa_import()` creates a new spa from user config, handles read-only/verbatim import, applies import props, overrides aux devices, resumes async work, updates cachefile, posts events, and creates zvol minors. `spa_tryimport()` uses a temporary read-only spa to return generated config/load diagnostics.

`spa_create()` validates namespace/properties/features, creates root and aux vdevs, expands metaslabs, creates DSL/DDT/BRT/MOS objects, initializes properties/features, starts txg sync and MMP, waits for initial sync, spawns aux threads, writes cachefile, and imports OS state.

`spa_export_common()` serializes export/destroy/reset, suspends async/zvol work, rejects active refs, handles active shared spares, stops background vdev activity, marks exported/destroyed state, flushes time/log metadata, sets final txg, unloads/deactivates, updates cachefile/namespace, and wakes waiters.

Device management begins with config mutation helpers. `spa_vdev_add()` parses and validates new top-level/aux devices, handles dRAID features, rejects incompatible additions during removal, splices children into the root, syncs config before allocation. `spa_vdev_attach()` supports mirror attach, replacement, rebuild, and raidz expansion while checking checkpoint/removal/resilver conflicts, topology, spares, size, ashift, and DTL setup. `spa_vdev_detach()` validates parent/child stability, DTL safety, label removal, tree compaction, unspare handling across pools, autoexpand, DTL cleanup, events, and history. Initialize/TRIM batch APIs validate each target, apply state transitions, collect per-GUID errors, wait for worker stop, and sync state.

## State and Dependencies

Key state touched includes `spa_state`, `spa_mode`, `spa_final_txg`, `spa_first_txg`, `spa_load_state`, `spa_load_max_txg`, `spa_extreme_rewind`, `spa_load_info`, `spa_config_source`, `spa_trust_config`, missing-vdev counters, MMP activity flags, async/sync flags, checkpoint info, failmode/autoreplace/autoexpand/multihost/autotrim, dedup quota, all-vdev-ZAP action, feature caches, taskqs, zthreads, and aux vdev lists.

Major dependencies are vdev open/validate/create/load/config/DTL/metaslab operations, DSL/DMU/ZAP sync and object APIs, ZIO/ZIL/scrub/resilver traversal, DDT/BRT, feature flags, device removal/condense, MMP, L2ARC, zvol minors, sysevents, ereports, and cachefile/OS integration.

## Risks and Cross-Chunk References

Important risks include untrusted-vs-MOS config divergence, missing top-level vdev recovery, MMP remote activity, checkpoint rewind irreversibility for writable imports, missing log-device handling, load verification thresholds, livelist condense races, config-before-allocation for added vdevs, replacement/detach races, DTL safety, active references during export, and hardforce export skipping label/cachefile updates.

Cross-chunk references: `spa_sync_version()`, `spa_sync_props()`, `spa_has_active_shared_spare()`, `spa_ld_log_spacemaps()`, `spa_vdev_enter()`, `spa_vdev_exit()`, `spa_vdev_detach_enter()`, `spa_vdev_config_enter()`, `spa_vdev_config_exit()`, `spa_vdev_remove()`, `spa_vdev_resilver_done()`, `spa_sync_config_object()`, removal/split/setpath APIs, and the main `spa_sync()` implementation are declared, called, or referenced here but defined later.