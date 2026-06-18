# File Research: sources/cow-pools/openzfs/module/zfs/dsl_pool.c

## Summary
Implements OpenZFS DSL pool construction, opening, closing, txg sync orchestration, dirty-data throttling, write-log throttling, special-directory management, clone upgrade helpers, temporary user-hold storage, and the DSL configuration-lock API.

## Main Responsibilities
- Allocates and initializes `dsl_pool_t` and core txg/list/taskq infrastructure.
- Opens existing pool metadata: root dir, `$MOS`, `$FREE`, `$ORIGIN`, free/obsolete bpobjs, bptree, empty bpobj, and temporary user refs.
- Creates new pool metadata, feature ZAP objects, origin snapshot, and the root dataset/objset.
- Coordinates txg sync ordering for dirty datasets, user accounting, dirty dirs, MOS sync, and sync tasks.
- Tracks dirty space and write-log bytes for throttling and txg kicks.
- Computes pool adjusted and unreserved space with slop, checkpoints, deferred frees, and metaslab deferred allocations.
- Upgrades older clone metadata layouts.
- Stores and cleans temporary snapshot user holds in a pool-wide ZAP.
- Provides `dp_config_rwlock` enter/exit/held helpers and documents its dataset-layer locking contract.

## Key APIs
- Pool lifecycle: `dsl_pool_init()`, `dsl_pool_open()`, `dsl_pool_close()`, `dsl_pool_create()`, `dsl_pool_open_special_dir()`.
- Special objects: `dsl_pool_create_obsolete_bpobj()`, `dsl_pool_destroy_obsolete_bpobj()`, `dsl_pool_create_origin()`.
- Sync: `dsl_pool_sync()`, `dsl_pool_sync_done()`, `dsl_pool_sync_context()`, `dsl_pool_mos_diduse_space()`.
- Throttling/accounting: `dsl_pool_dirty_space()`, `dsl_pool_undirty_space()`, `dsl_pool_need_dirty_delay()`, `dsl_pool_wrlog_count()`, `dsl_pool_need_wrlog_delay()`, `dsl_pool_adjustedsize()`, `dsl_pool_unreserved_space()`, `dsl_pool_deferred_space()`.
- Upgrades: `dsl_pool_upgrade_clones()`, `dsl_pool_upgrade_dir_clones()`.
- User holds: `dsl_pool_clean_tmp_userrefs()`, `dsl_pool_user_hold()`, `dsl_pool_user_release()`.
- Locking: `dsl_pool_hold()`, `dsl_pool_rele()`, `dsl_pool_config_enter()`, `dsl_pool_config_enter_prio()`, `dsl_pool_config_exit()`, `dsl_pool_config_held()`, `dsl_pool_config_held_writer()`.

## Important Behavior
`dsl_pool_open_impl()` builds the in-memory pool shell: config rrwlock, txg state, MMP state, dirty txg lists, sync task lists, sync taskq, ZIL clean taskq, zrele taskq, unlinked-drain taskq, locks, CVs, and write-log aggsums.

`dsl_pool_open()` assumes the meta objset has been opened, enters the config lock as writer, opens the root DSL directory, special dirs, origin snapshot, bpobjs, optional leak dir, async-destroy bptree, empty bpobj, temporary userrefs object, and scan state.

`dsl_pool_create()` creates the MOS, pool directory, root dir, `$MOS`, optional `$FREE` and free bpobj, optional `$ORIGIN`, feature ZAP objects, optional encryption feature enablement, root dataset, root objset, and kernel ZPL filesystem structures.

`dsl_pool_sync()` encodes the txg sync order. Early sync tasks run before dirty blocks. Dirty datasets sync under a root zio, then user/group/project accounting completion runs, then datasets dirtied by accounting sync again. Dataset sync-done processing moves dead blocks/livelists and releases dirty holds. Dirty dirs sync next, `$MOS` accumulated deltas are applied, the MOS is synced, dirty-space accounting is reconciled, and normal sync tasks run after the MOS dd holds have been cleared.

`dsl_pool_sync_done()` cleans dirty ZILs after sync, clears per-txg write-log accounting, and asserts the MOS is no longer dirty for that txg.

Dirty-data throttling maintains per-txg and total dirty byte counters under `dp_lock`. Crossing `zfs_dirty_data_sync_percent` kicks a txg; crossing `zfs_delay_min_dirty_percent` is exposed to transaction-delay code. Write-log throttling uses aggsums to track copied ZIL write records separately through `zfs_wrlog_data_max`.

`dsl_pool_adjustedsize()` subtracts checkpoint space, SPA deferred frees, and a slop-space reservation according to `zfs_space_check_t`. `dsl_pool_unreserved_space()` further subtracts metaslab deferred allocation space.

Clone upgrade helpers attach legacy clones to `$ORIGIN`, create next-clone ZAPs, create `$FREE` infrastructure for dir clones, and populate origin dir clone maps.

Temporary user holds are stored as `<dsobj-hex>-<tag>` entries in a pool-wide ZAP. `dsl_pool_clean_tmp_userrefs()` reconstructs an nvlist grouped by dataset object and calls the dataset user-release path.

## State and Synchronization
`dp_config_rwlock` protects dataset-layer state. The long comment at the end establishes the rule: hold the pool config lock before holding datasets or dirs, except for explicit long holds or ownership operations that prevent destruction while the config lock is dropped.

Dirty data and MOS delta counters are protected by `dp_lock`; write-log byte counters use `aggsum`. Dirty datasets, dirs, zilogs, and sync tasks are organized in txg lists keyed by txg. Sync-context checks include the txg sync thread, pool initialization, and membership in `dp_sync_taskq`.

Close ordering releases opened DSL objects, closes bpobjs, evicts the MOS, destroys txg lists/taskqs, flushes ARC buffers for the spa, finalizes MMP/txg/scan state, waits for DMU buffer user eviction, destroys locks/CVs/aggsums, and frees the pool.

## Dependencies
Depends on SPA/vdev state, DMU objsets and transactions, DSL dirs and datasets, DSL scan, ZAP, bpobj/bptree, ZIL, ARC flushing, metaslab deferred-space accounting, feature flags, MMP, taskqs, aggsum, txg machinery, and ZFS root filesystem creation in kernel builds.

## Risks
`dsl_pool_sync()` ordering is correctness-critical. Moving sync tasks, MOS sync, user-accounting completion, dirty-dir sync, or dirty-space reconciliation can affect snapshot consistency, destroy checks, userquota state, and dirty throttling.

Dirty byte accounting has fallback cleanup for paths that dirty or undirty unexpectedly. Bugs can lead to permanent throttling, missed throttling, or assertions during pool close.

Pool close must coordinate object references from datasets, dirs, ZILs, ARC, taskqs, and DMU buffer users. Reordering teardown can leave callbacks pointing at freed pool state.

The config-lock contract is central to the DSL layer. Code that holds datasets or dirs without `dsl_pool_config_enter()` or a legitimate long hold can race destroy, rename, or property changes.

Temporary userref parsing mutates the ZAP attribute name at the first `-`; malformed names would violate assumptions made by `dsl_pool_clean_tmp_userrefs()`.
