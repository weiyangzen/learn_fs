# Group Research: group_1437_openzfs_sources_cow_pools_openzfs_module_zfs_dsl_dir_c_sources_cow__7ab5cf75c7f8

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_dir.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dsl_dir.c

## Summary
Implements OpenZFS DSL directory lifetime, naming, hierarchy lookup, space accounting, quotas, reservations, filesystem/snapshot count limits, rename accounting, livelist cleanup, and wait-for-activity support. A `dsl_dir_t` is the metadata container for a head dataset's place in the dataset tree and the accounting boundary used by pool and dataset code.

## Main Responsibilities
- Holds and releases `dsl_dir_t` objects by object number or dataset path.
- Maintains parent/child directory names and ZAP child maps.
- Initializes and enforces filesystem and snapshot count limits.
- Tracks used, compressed, uncompressed, quota, reservation, and used-breakdown accounting.
- Performs temporary reservations and estimated write accounting for DMU transactions.
- Applies actual sync-time space deltas and rolls accounting up parent dirs.
- Sets `quota` and `reservation` properties through sync tasks.
- Validates and performs filesystem rename between DSL directories.
- Opens, closes, and removes clone livelists.
- Supports waiting for directory-backed activities such as ZPL delete-queue draining.

## Key APIs
- Lifetime and lookup: `dsl_dir_hold_obj()`, `dsl_dir_hold()`, `dsl_dir_rele()`, `dsl_dir_async_rele()`, `dsl_dir_name()`, `dsl_dir_namelen()`.
- Creation and metadata: `dsl_dir_create_sync()`, `dsl_dir_zapify()`, `dsl_dir_is_zapified()`, `dsl_dir_dirty()`, `dsl_dir_sync()`.
- Limit accounting: `dsl_dir_activate_fs_ss_limit()`, `dsl_fs_ss_limit_check()`, `dsl_fs_ss_count_adjust()`, `dsl_dir_get_filesystem_count()`, `dsl_dir_get_snapshot_count()`.
- Space accounting: `dsl_dir_space_available()`, `dsl_dir_tempreserve_space()`, `dsl_dir_tempreserve_clear()`, `dsl_dir_willuse_space()`, `dsl_dir_diduse_space()`, `dsl_dir_transfer_space()`, `dsl_dir_diduse_transfer_space()`.
- Property-backed controls: `dsl_dir_set_quota()`, `dsl_dir_set_reservation()`, `dsl_dir_set_reservation_sync_impl()`.
- Rename and transfer: `dsl_dir_rename()`, `dsl_dir_transfer_possible()`.
- Livelist and activity: `dsl_dir_livelist_open()`, `dsl_dir_livelist_close()`, `dsl_dir_remove_livelist()`, `dsl_dir_wait()`, `dsl_dir_cancel_waiters()`.

## Important Behavior
`dsl_dir_hold_obj()` attaches an in-memory `dsl_dir_t` to the bonus buffer using `dmu_buf_set_user_ie()`. It loads the parent dir, local name, clone origin creation txg, optional encryption key object, optional livelist, and snapshot-change timestamp. The in-memory object keeps both open-to-close and instantiate-to-evict SPA references.

`dsl_dir_hold()` parses pool-relative paths component by component, walking child-dir ZAP objects and optionally returning a tail component for create or snapshot cases.

Filesystem and snapshot limits are lazy-initialized. When the feature first becomes active or a limit is set, `dsl_dir_init_fs_ss_count()` recursively counts visible child filesystems and snapshots, skipping hidden `$` dirs and temporary `%` snapshots. Later create, destroy, rename, and receive paths use `dsl_fs_ss_limit_check()` and `dsl_fs_ss_count_adjust()` to validate and roll counts up initialized ancestors.

Limit enforcement can be bypassed for callers allowed to modify the limit, primarily to permit privileged recursive snapshot operations. Delegated-permission cases can still enforce limits above the dataset where the caller has permission.

Space accounting distinguishes estimated open-context reservations from sync-time committed usage. Temporary reservations use ARC memory reservation plus per-dir `dd_tempreserved[]`; estimated writes use `dd_space_towrite[]`; actual sync-time usage updates `dsl_dir_phys_t` and parent accounting using `parent_delta()` so reservations affect parent-visible usage correctly.

Quota checks include pool adjusted size at the root, deferred frees, inflight dirty data, optional ZVOL quota relaxation through `zvol_enforce_quotas`, and retry behavior when pending frees may resolve pressure.

Rename validation checks destination existence, pool match, parent type, descendant name lengths and nesting, filesystem/snapshot limits, available space, encryption compatibility, and no move into descendant. Sync-time rename updates child ZAPs, parent object, parent-held references, count accounting, space accounting, ZFS mount names, ZVOL minors, and property-change notifications.

Livelist removal coordinates with the pool livelist-condense zthr. If the livelist currently being removed is queued for condensation, the code marks it cancelled and waits for the condense cycle before closing and optionally freeing the on-disk deadlist object.

`dsl_dir_wait()` currently handles `ZFS_WAIT_DELETEQ`. In kernel builds it checks the mounted ZPL objset's unlinked set, readonly state, and pool writability; in libzpool builds it reports no delete-queue wait.

## State and Synchronization
The file relies on `dp_config_rwlock` for dataset tree stability, `dd_lock` for in-memory directory fields and accounting arrays, `dd_activity_lock`/CV for waiters, and txg lists for dirty dir writeout. Sync-time functions assert `dmu_tx_is_syncing(tx)` where they mutate on-disk metadata.

Parent holds are reference-counted through `dsl_dir_hold_obj()` and released through `dsl_dir_rele()` or `dsl_dir_async_rele()`. Eviction validates no dirty-list membership and no temporary reservations before tearing down properties, locks, activity CVs, livelists, and SPA refs.

Space updates intentionally use iterative loops in hot paths such as temp reservation and `dsl_dir_willuse_space()` to reduce stack growth from deep dataset trees. Some sync-time propagation remains recursive.

## Dependencies
Depends on DMU buffers, txg dirty lists, ZAP objects, DSL datasets, DSL properties, sync tasks, SPA feature flags, ARC temporary reservations, metaslab deferred-space accounting through `dsl_pool`, ZFS policy/delegation checks, ZPL unlinked-set state, ZVOL rename/minor helpers, livelist/deadlist helpers, and kernel credential/zone checks.

## Risks
Accounting invariants are high-risk: `dd_used_bytes`, `dd_reserved`, used-breakdown buckets, temp reservations, estimated writes, and parent rollups must remain consistent across create, destroy, rename, snapshot, reservation changes, and sync cancellation.

`dsl_dir_set_reservation_sync_impl()` deliberately updates parent accounting while holding the child `dd_lock` so dataset and dir accounting remain atomically visible to quota checks. Lock-order changes here can introduce deadlocks or inconsistent quota decisions.

`dsl_dir_rename_check()` performs count initialization from a check function during syncing context. This is intentional but unusual; callers must preserve the sync-task assumptions.

The path parser treats `/` and `@` specially and returns snapshot tails. Misusing `tailp` can turn a partial lookup into a false success or `ENOENT`.

Callback and waiter lifetimes cross subsystem boundaries: `dsl_prop_notify_all()`, ZFS mount rename callbacks, ZVOL minor renames, livelist condense cancellation, and delete-queue waits all rely on external objects remaining valid under the expected pool/config locks.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_pool.c -->
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
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_pool.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_prop.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dsl_prop.c

## Summary
Implements OpenZFS DSL property lookup, inheritance, received-property handling, set/inherit sync tasks, property-change callbacks, all-property enumeration, and helpers for building property nvlists. Properties are stored in DSL dir or snapshot ZAP objects, with suffix keys for inherited, received, and newer index values.

## Main Responsibilities
- Resolves effective property values from snapshot props, local dir props, received props, inherited parent props, or defaults.
- Supports callback registration and notification for integer property changes.
- Predicts effective quota/reservation-style values before setting them.
- Sets, clears, inherits, and receives individual or batched properties through sync tasks.
- Stores special ignore-unknown-value entries for newer indexed property values while preserving compatibility with older ZFS versions.
- Enumerates local, received, inherited, and snapshot-valid properties into nvlists.
- Tracks whether a dataset has received properties using `ZPROP_HAS_RECVD`.

## Key APIs
- Lookup: `dsl_prop_get_dd()`, `dsl_prop_get_ds()`, `dsl_prop_get()`, `dsl_prop_get_integer()`, `dsl_prop_get_int_ds()`, `dsl_prop_get_all()`, `dsl_prop_get_received()`.
- Mutation: `dsl_prop_set_int()`, `dsl_prop_set_string()`, `dsl_prop_inherit()`, `dsl_props_set()`, `dsl_props_set_check()`, `dsl_props_set_sync()`, `dsl_props_set_sync_impl()`, `dsl_prop_set_sync_impl()`.
- Prediction and received tracking: `dsl_prop_predict()`, `dsl_prop_get_hasrecvd()`, `dsl_prop_set_hasrecvd()`, `dsl_prop_unset_hasrecvd()`.
- Callback lifecycle: `dsl_prop_init()`, `dsl_prop_fini()`, `dsl_prop_register()`, `dsl_prop_unregister()`, `dsl_prop_unregister_all()`, `dsl_prop_hascb()`, `dsl_prop_notify_all()`.
- Nvlist helpers: `dsl_prop_nvlist_add_uint64()`, `dsl_prop_nvlist_add_string()`.

## Important Behavior
Property keys use suffixes: `$inherit` for explicit inheritance, `$recvd` for received values, and `$iuv` for newer indexed values older implementations should ignore. `dsl_prop_get_dd()` checks `$iuv`, local, explicit inherit, received, parents, and finally default values.

`dsl_prop_get_ds()` handles snapshot property ZAPs first, then delegates to the containing dir. Snapshot properties require the snapshot props feature on old-version checks, and non-snapshot datasets use the dir's `dd_props_zapobj`.

`dodefault()` returns defaults for normal mutable properties and set-once properties, but not ordinary readonly properties. This lets initial values be supplied without treating readonly runtime stats as settable defaults.

`dsl_prop_predict()` is intentionally narrow and only predicts quota, reservation, refquota, and refreservation effective values. It models interactions between local and received values, plus pre-`SPA_VERSION_RECVD_PROPS` source translation.

Callbacks are stored per dir in `dsl_prop_record_t` lists and per dataset in `ds_prop_cbs`. Registration immediately invokes the callback with the current integer value. Notification walks inheritance descendants unless a local property blocks propagation.

Callback records do not hold datasets. Recursive notification paths use `dsl_dataset_try_add_ref()` before invoking callbacks for datasets that could have been evicted, especially snapshot callback records encountered while walking head datasets.

`dsl_prop_set_sync_impl()` creates snapshot props ZAPs lazily, applies source-specific ZAP changes, removes empty snapshot prop ZAPs, computes the new effective value, notifies callbacks for integer properties, and logs history. Source combinations cover clearing local, clearing received, clearing both, setting local, setting received, and explicit inheritance.

`dsl_prop_set_iuv()` stores new indexed values for `redundant_metadata=some/none` and `snapdir=disabled` in `$iuv` while writing the default numeric value to the base key for older-version compatibility.

`dsl_prop_get_all_impl()` iterates property ZAPs, filters suffix keys, suppresses overridden received values, skips incompatible inherited or snapshot properties, resolves strings by lookup when needed, and records each property as an nvlist with `ZPROP_VALUE` and `ZPROP_SOURCE`.

`dsl_prop_get_received()` returns true received properties only after `ZPROP_HAS_RECVD` exists; before that it treats local properties as the received set for compatibility with older pools.

## State and Synchronization
Callers must hold the DSL pool config lock for low-level lookup and callback operations. Callback list manipulation uses the containing dir's `dd_lock`. Sync-time mutation runs through `dsl_sync_task()` and uses MOS ZAP updates under assigned DMU transactions.

Snapshot property ZAPs are optional and destroyed when empty. Dir property ZAPs are permanent fields of `dsl_dir_phys_t`. Set operations estimate required blocks as two blocks per property unless only removing entries.

## Dependencies
Depends on DSL dirs and datasets, DMU transactions, ZAP cursors/lookups/updates, sync tasks, SPA version/feature behavior, ZFS property metadata from `zfs_prop.h`, nvlists, pool config locking, dataset eviction reference helpers, and spa history logging.

## Risks
Property source precedence is subtle. Incorrect handling of `$inherit`, `$recvd`, `$iuv`, snapshot props, or parent traversal can expose wrong effective values or wrong `setpoint` strings.

Callback notification is lifetime-sensitive because callback records intentionally avoid dataset holds. Missing `dsl_dataset_try_add_ref()` in recursive paths would risk use-after-free during eviction.

`dsl_prop_set_sync_impl()` must preserve compatibility with old pool versions and received-property semantics. Source bitmask mistakes can silently clear the wrong ZAP key or fail to restore local/received precedence.

All-property enumeration must avoid duplicate keys and skip compatibility helper keys. Returning `$iuv` or overridden `$recvd` values as ordinary properties would confuse `zfs get` and receive rollback paths.

String length and ZAP name/value limits are enforced in `dsl_props_set_check()`. New callers that bypass batched property setting need equivalent validation.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_prop.c -->