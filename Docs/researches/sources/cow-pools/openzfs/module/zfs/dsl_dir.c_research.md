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
