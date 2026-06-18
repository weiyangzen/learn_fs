# Group Research: group_524_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_4a9b59f7db08

Scope: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa.c

## Role In The Source Tree

`spa.c` is the central illumos ZFS Storage Pool Allocator implementation for persistent pool-level state transitions. It owns high-level pool lifecycle operations: property get/set, pool open/import/create/export/destroy/reset, root-pool import, auxiliary vdev loading, vdev topology changes, async pool tasks, transaction group syncing, activity waiting, and ZFS sysevent posting.

The file sits above vdev, metaslab, DSL, DMU, ZIO, ZIL, DDT, scrub/scan, MMP, removal, checkpoint, initialize, trim, L2ARC, and feature-flag code. Most of its functions are orchestration points that lock the SPA namespace/config, call lower layers in strict order, and persist derived pool state into MOS objects, vdev labels, and the config cache.

## Major Responsibilities

- Defines ZIO taskq topology per I/O type and priority, including fixed, batch, and multi-taskq modes.
- Provides zpool property retrieval, validation, mutation, and sync-time persistence.
- Activates/deactivates an in-core `spa_t`, including metaslab classes, per-pool taskqs/process, txg root zios, dirty lists, errlists, keystore, and upgrade taskq.
- Loads/unloads pools through staged config parsing, vdev open/validate, uberblock selection, MOS opening, trusted-config replacement, feature checks, aux vdev loading, vdev metadata loading, DDT loading, log verification, pool verification, ZIL claiming, sync-thread startup, and async restart.
- Creates, imports, exports, destroys, resets, and tries imports for pools.
- Implements vdev add, attach/replace/spare, detach, split mirror, set path/FRU, initialize, TRIM, scan/scrub entry points, and resilver-completion cleanup.
- Dispatches async maintenance for config updates, remove/probe, autoexpand, resilver, initialize/TRIM/autotrim restart, and L2ARC rebuild.
- Implements `spa_sync()` transaction group commit and convergence.
- Provides activity wait APIs and kernel sysevent helpers.

## Important Data And State

- `zio_taskqs`: maps each `ZIO_TYPE_*` and `ZIO_TASKQ_*` lane to taskq creation rules.
- `spa->spa_config`, `spa->spa_config_object`, `spa->spa_config_syncing`, and `spa->spa_config_txg`: in-core, MOS-backed, syncing, and committed pool configuration.
- `spa->spa_root_vdev`: rebuilt from untrusted config, then replaced by MOS-trusted config during normal load.
- `spa->spa_trust_config`: gates writeability and strict blkptr/vdev assumptions.
- `spa->spa_load_info`: import diagnostics such as missing devices, unsupported features, MMP status, rewind data, load time, and error counts.
- `spa->spa_spares` and `spa->spa_l2cache`: auxiliary vdev state and packed-nvlist MOS object tracking.
- `spa->spa_async_tasks`, `spa->spa_async_thread`, and `spa->spa_async_suspended`: deferred pool maintenance coordination.
- `spa->spa_activities_lock`: race-free waiting for checkpoint discard, frees, initialize, replace, remove, resilver, and scrub activity.

## Lifecycle And Load Path

`spa_load()` records load state and calls `spa_load_impl()`, while `spa_load_best()` wraps it with rewind retry behavior. The load path first parses the supplied config, opens and validates vdevs, selects an uberblock, opens the MOS root block, loads the trusted MOS config, rebuilds/reopens the vdev tree, and can force a reload if the original config omitted too many top-level vdevs.

After a trusted config is established, `spa_load_impl()` optionally rewinds to a checkpoint, reads checkpoint txg metadata, loads indirect vdev/removal metadata, verifies feature support, opens DSL special directories, loads pool properties, opens spares and L2ARC devices, loads vdev metadata and DTLs, loads DDTs, verifies ZIL logs, verifies pool block reachability, updates deflated-space accounting, claims log blocks, starts sync/MMP threads, schedules resilver/restart work, logs history, starts auxiliary zthreads, and restarts initialize/TRIM/autotrim state.

## Pool Properties

`spa_prop_get_config()` reports derived state such as size, allocated/free bytes, checkpoint bytes, fragmentation, expandable space, read-only state, capacity, dedup ratio, health, version, GUID, altroot, comment, max block size, max dnode size, and cachefile source. `spa_prop_get()` merges those with persistent MOS pool properties.

`spa_prop_validate()` enforces feature syntax, version upgrade bounds, boolean property ranges, multihost hostid requirements, bootfs validation, suspended-pool failure-mode handling, cachefile path validation, printable and length-bounded comments, and dedup ditto minimums. `spa_prop_set()` routes version/feature changes through `spa_sync_version()` and general property changes through `spa_sync_props()`.

## Vdev And Auxiliary Device Operations

`spa_config_parse()` recursively builds vdev trees from nvlists via `vdev_alloc()`. `spa_load_spares()` and `spa_load_l2cache()` reload auxiliary devices from MOS nvlists, open/validate devices, reconcile active spares/L2ARC presence, and regenerate status-rich configs.

Main mutation APIs include `spa_vdev_add()`, `spa_vdev_attach()`, `spa_vdev_detach()`, `spa_vdev_split_mirror()`, `spa_vdev_initialize()`, `spa_vdev_trim()`, `spa_vdev_setpath()`, and `spa_vdev_setfru()`. Checkpoint presence or checkpoint discard blocks unsafe topology operations, and active device removal further constrains add/attach cases.

## Sync Pipeline

`spa_sync()` waits for open-context txg zios, acquires config locks, converts pending vdev state dirties into config dirties, creates an assigned DMU tx, programs the deadman cyclic, handles version upgrade edge cases, adjusts allocation queue depths, starts indirect mapping condensation if appropriate, then iterates to MOS convergence.

`spa_sync_iterate_to_convergence()` repeatedly syncs config and aux objects, error logs, DSL pool state, frees or deferred frees, DDTs, scans, removal state, upgrades, log spacemap/metaslab data, and dirty vdevs until the MOS is clean. `spa_sync_rewrite_vdev_config()` then writes uberblocks/config labels either to selected healthy top-level vdevs or all dirty vdevs, retrying after I/O suspension/resume if necessary.

## Import, Export, And Recovery Details

`spa_open_common()` opens pools from namespace/cachefile state, applies load policy, handles recover mode, returns load diagnostics on failure, and removes stale exported/destroyed entries. `spa_import()` imports non-root pools from user config/properties and handles verbatim import, read-only mode, rewind policy, aux-device replacement, cachefile updates, autoexpand scheduling, history, and events. `spa_tryimport()` uses temporary `$import` state for discovery.

`spa_export_common()` implements export, destroy, and reset. It suspends async tasks, checks references, rejects export with active shared spares unless forced, stops initialize/TRIM/autotrim work, marks final pool state for labels, unloads/deactivates, optionally returns old config, writes/removes cachefile state, and removes the SPA for real export/destroy.

## Concurrency And Locking

The file relies on `spa_namespace_lock`, `spa_config_enter/exit()` over SCL classes, subsystem locks for props/async/proc/scrub/initialize/trim/activities, and DSL sync tasks for MOS mutation. It carefully drops locks around waits or recursive opens.

The activity wait subsystem prevents missed wakeups by holding `spa_activities_lock` while checking state and waiting, while completers call `spa_notify_waiters()` after state transitions. `spa_wake_waiters()` cancels and drains waiters during unload/export.

## Notable Invariants And Safety Checks

- Pools with missing top-level vdevs are forced read-only once the trusted config is used.
- Writeability depends on trusted config, avoiding writes based only on cachefile/scan data.
- Normal load rejects unsupported read features; tryimport distinguishes unsupported write features from read-only usability.
- MMP activity checks guard against importing pools active on another host.
- Topology changes are blocked while checkpoints exist or are being discarded.
- New vdevs are added without metaslab initialization until config labels/cache are safely synced.
- `spa_sync()` must reach MOS convergence before label rewrite and asserts no late dirties remain.
- Waiters are cancelled and drained before unload.

## Research Notes

This file is a high-value architecture reference for learning ZFS because it shows how pool-level correctness is assembled from lower layers: nvlist configs, vdev labels, uberblocks, MOS ZAP objects, txg sync, ZIL replay/claim, feature flags, DTLs, MMP, and async repair. Most functions are not local algorithms in isolation; their correctness depends on call ordering, lock ordering, sync-task context, and the distinction between in-core state, MOS state, vdev labels, and user-visible cachefile state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa.c -->