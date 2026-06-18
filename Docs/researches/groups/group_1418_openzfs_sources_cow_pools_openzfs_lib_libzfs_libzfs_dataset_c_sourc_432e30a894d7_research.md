# Group Research: group_1418_openzfs_sources_cow_pools_openzfs_lib_libzfs_libzfs_dataset_c_sourc_432e30a894d7

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/cow-pools/openzfs`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_dataset.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_dataset.c

## Scope

Core libzfs dataset implementation. It validates dataset/snapshot/bookmark names, opens and duplicates dataset handles, loads objset/property state, validates and sets properties, creates/destroys/clones/promotes/snapshots/rolls back/renames datasets, manages holds and delegated permissions, handles user/group/project quota properties, and computes zvol reservation sizing.

## APIs And Behavior

- `zfs_validate_name()`, `zfs_name_valid()`, and helpers enforce ZFS dataset, snapshot, bookmark, and pool naming rules with specific libzfs auxiliary errors.
- `make_dataset_handle()`, `make_dataset_handle_zc()`, `make_dataset_simple_handle_zc()`, `make_bookmark_handle()`, `zfs_open()`, `zfs_handle_dup()`, and `zfs_close()` construct and manage `zfs_handle_t` objects backed by `ZFS_IOC_OBJSET_STATS`, `ZFS_IOC_OBJSET_RECVD_PROPS`, bookmark enumeration, and cached zpool handles.
- Property validation is centralized in `zfs_valid_proplist()`, including user properties, user/group/project quotas, readonly/set-once checks, type applicability, mount/share zoning restrictions, encryption key properties, record/vol block sizes, volume sizing, UTF-8/normalization coupling, and `refreservation=auto`.
- `zfs_prop_set_list_flags()` gathers changelists for mount/share-sensitive properties, applies `ZFS_IOC_SET_PROP`, reports per-property failures, refreshes stats, and calls `zfs_mount_setattr()` for namespace properties such as atime, devices, exec, readonly, setuid, xattr, and nbmand.
- `zfs_prop_inherit()` handles both user-property inheritance and native property inheritance, using changelists and remount updates where needed.
- `zfs_prop_get()`, `zfs_prop_get_int()`, `zfs_prop_get_numeric()`, and `zfs_prop_get_recvd()` translate raw nvlists and objset stats into display values, including temporary mount-option overrides from `/proc/self/mounts`, clone/redaction snapshot formatting, GUID/txg literal handling, mountpoint inheritance plus altroot handling, and received-property mode.
- `zfs_create()`, `zfs_clone()`, `zfs_snapshot()`, `zfs_snapshot_nvl()`, `zfs_destroy()`, `zfs_destroy_snaps()`, `zfs_destroy_snaps_nvl()`, `zfs_promote()`, `zfs_rollback()`, and `zfs_rename()` wrap libzfs_core/kernel operations with parent checks, type checks, crypto checks, recursive behavior, changelists, and user-facing error translation.
- `zfs_hold()`, `zfs_hold_nvl()`, `zfs_release()`, `zfs_get_holds()`, `zfs_get_fsacl()`, and `zfs_set_fsacl()` implement snapshot holds and delegated ACL access.
- `zfs_userspace()` and `zfs_prop_get_userquota*()` query user/group/project usage and quota values through userspace accounting ioctls.
- `zvol_volsize_to_reservation()` models zvol reservation requirements, including RAIDZ/dRAID allocation overhead, metadata blocks, and copies.

## State And Dependencies

The file depends on `libzfs_impl.h`, `libzfs_core`, ZFS ioctls, nvlists, ZFS property metadata, zpool handles, changelists, mount/share helpers, crypto helpers, zone checks, user/group lookup, optional idmap/MLS label support, and kernel objset stats.

## Risks And Invariants

Dataset handles cache property nvlists and mount options, so callers must refresh when they need current kernel state. Changelist prefix/postfix ordering is essential around property changes, rename, rollback, and unmount/remount behavior. Volume reservation logic must stay synchronized with kernel/vdev accounting and the referenced test-suite shell implementation. Userquota property decoding depends on local passwd/group/idmap resolution and zone rules, so the same property string can fail or encode differently across environments.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_dataset.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_diff.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_diff.c

## Scope

Implements `zfs diff` support by comparing snapshots, consuming kernel diff records, resolving object IDs to paths/stats, and printing added/removed/modified/renamed file entries.

## APIs And Behavior

- `zfs_show_diffs()` is the public entry point. It sets up snapshot names, mountpoints, a pipe, a worker thread, and invokes `ZFS_IOC_DIFF`.
- Snapshot parsing supports `fromsnap`, abbreviated `@snap`, `tosnap`, live dataset targets, clone-origin comparisons, and just-in-time temporary snapshots via `ZFS_IOC_TMP_SNAPSHOT`.
- `differ()` reads fixed-size `dmu_diff_record_t` records from the pipe and dispatches `DDR_FREE` and `DDR_INUSE` ranges.
- Object resolution uses `ZFS_IOC_OBJ_TO_STATS`; free-object traversal uses `ZFS_IOC_NEXT_OBJ`.
- Output helpers print type markers `+`, `-`, `M`, and `R`, optional timestamps, optional file-type classifiers, parseable separators, color for TTY output, and escaped path bytes unless no-mangle mode is set.
- Rename detection compares object generation, mode, ctime, link counts, and old/new paths.

## State And Dependencies

`differ_info_t` carries dataset/snapshot names, mountpoints, flags, pipe fds, cleanup fd, shares object, and deferred error state. The file depends on snapshot mountpoints under `/.zfs/snapshot/`, mnttab mount discovery, pthreads, pipe2, ZFS diff ioctls, and `find_shares_object()`.

## Risks And Invariants

The worker expects complete fixed-size records; short or malformed records become `EPIPE`/diff-data errors. Path discovery requires permissions and loaded encryption keys. Temporary snapshots depend on a cleanup fd. The implementation intentionally ignores non-ZPL objects and the shares object.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_diff.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_impl.h -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_impl.h

## Scope

Private libzfs implementation header shared by the library source files.

## API Surface

Defines internal `libzfs_handle`, `zfs_handle`, and `zpool_handle` layouts; error buffer size; mount namespace property flags; `ZFS_IS_VOLUME`; URI handler structs; changelist flags; and `differ_info_t`.

It declares internal allocation/error helpers, zcmd nvlist helpers, dataset-handle constructors, property parser/list expansion helpers, changelist APIs, namespace/mount helpers, zpool open/name validation helpers, mnttab-related integration points, module loading, disk relabeling, and `find_shares_object()`.

## State And Dependencies

The header ties together libzfs public headers, libzfs_core, nvpair, DMU/ZFS ioctl structures, mutexes, regex, AVL-backed namespace/mnttab state, and libshare integration.

## Risks And Invariants

This is private ABI: struct fields are directly shared across libzfs translation units and must stay consistent with all users. The cached zpool handle list, mnttab AVL, namespace AVL, and zcmd nvlist helpers form library-global state behind a single `libzfs_handle_t`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_import.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_import.c

## Scope

Provides libzfs import-support callbacks, label clearing, and device-in-use detection for pool/vdev labels.

## APIs And Behavior

- `libzfs_config_ops` supplies `refresh_config_libzfs()` and `pool_active_libzfs()` to the shared import logic.
- `refresh_config()` sends a trial config through `ZFS_IOC_POOL_TRYIMPORT`, growing the destination nvlist on `ENOMEM`.
- `pool_active()` opens a pool silently and compares the active pool GUID against the label/config GUID.
- `zpool_clear_label()` scans all vdev labels, validates GUID and pool state, zeros the label nvlist/uberblock area while leaving leading pad space intact, and also clears an L2ARC header when the label indicates an L2 cache device.
- `zpool_in_use()` reads a vdev label and decides whether the device is active, exported, potentially active, spare, L2ARC, or unused. It checks active configs by GUID, searches aux spares/cache devices across imported pools, and returns the pool name/state when in use.

## State And Dependencies

The file depends on vdev labels, pool config nvlists, import ioctls, zpool iteration/open helpers, `zpool_read_label()`, `fstat64_blk()`, and libzutil label/config constants.

## Risks And Invariants

Device in-use results are conservative around active/exported labels and shared spares. Label clearing only succeeds if at least one valid label was overwritten and, for L2ARC labels, the header was also cleared. Active-pool checks rely on matching GUIDs rather than names alone.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_import.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_iter.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_iter.c

## Scope

Implements libzfs dataset iteration for child filesystems, snapshots, bookmarks, clones, dependents, snapshot specs, sorted snapshots, and mounted child datasets.

## APIs And Behavior

- `zfs_iter_filesystems_v2()` and `zfs_iter_snapshots_v2()` use list-next ioctls with expandable nvlists and optional simple handles.
- `zfs_iter_bookmarks_v2()` requests bookmark-valid properties through `lzc_get_bookmarks()` and creates bookmark handles.
- `zfs_iter_snapshots_sorted_v2()` collects snapshots in an AVL tree sorted by `createtxg`.
- `zfs_iter_snapspec_v2()` parses comma-separated snapshot specs, including ranges with `%`, validates endpoints, and iterates matching snapshots.
- `zfs_iter_children_v2()` visits snapshots before child filesystems.
- `zfs_iter_dependents_v2()` recursively walks clone dependencies, child filesystems, and snapshots while detecting dependency cycles unless recursion is allowed.
- `zfs_iter_mounted()` walks `MNTTAB`, filters mounted ZFS child filesystems, skips snapshots and legacy mountpoints, and invokes the callback.

## State And Dependencies

Iteration builds handles from `zfs_cmd_t` responses using constructors from `libzfs_dataset.c`. It depends on ZFS dataset/snapshot list ioctls, libzfs_core bookmark APIs, clone property resolution, AVL trees, and mnttab parsing.

## Risks And Invariants

Callbacks receive handles and are expected to close or retain them according to libzfs iteration conventions. List iteration treats `ESRCH` and `ENOENT` as normal completion/removal races. Dependent traversal guards against clone cycles by comparing dataset GUIDs on an explicit stack.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_iter.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_mnttab.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_mnttab.c

## Scope

Maintains an optional libzfs-side cache of mounted ZFS filesystems from `MNTTAB`.

## APIs And Behavior

- `libzfs_mnttab_init()` initializes a mutex and AVL tree keyed by `mnt_special`.
- `libzfs_mnttab_fini()` frees cached entries and destroys the AVL/mutex.
- `libzfs_mnttab_cache()` toggles cache retention.
- `libzfs_mnttab_find()` reloads from `MNTTAB` when caching is disabled or the cache is empty, then looks up a dataset by `mnt_special`.
- `libzfs_mnttab_add()` and `libzfs_mnttab_remove()` update the cache only when caching is enabled.
- Duplicate mount entries are ignored while loading.

## State And Dependencies

The cache lives in `libzfs_handle_t` as `zh_mnttab`, guarded by `zh_mnttab_lock`. Each node stores duplicated special, mountpoint, and options strings and a constant ZFS fstype string.

## Risks And Invariants

When caching is disabled, add/remove are no-ops and find drops/rebuilds the AVL. Returned `struct mnttab` fields point into cached nodes, so their lifetime is tied to the cache entry and lock-protected mutation discipline.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_mnttab.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_mount.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_mount.c

## Scope

Implements libzfs mount, unmount, share, unshare, pool-wide dataset enable/disable, mountpoint ordering, and namespace-property support.

## APIs And Behavior

- `zfs_is_namespace_prop()` and `zfs_namespace_prop_flag()` identify properties that require mount namespace updates.
- `is_mounted()` and `zfs_is_mounted()` query the libzfs mnttab cache.
- `zfs_is_mountable()` rejects non-filesystems, `mountpoint=none/legacy`, `canmount=off`, global-zone attempts for zoned datasets, and redacted datasets unless forced.
- `zfs_mount()` and `zfs_mount_at()` build mount options from properties, force readonly for readonly-imported pools, optionally load encryption keys, add `zfsutil`, create mountpoint directories, enforce overlay/empty-directory rules, call `do_mount()`, and update the mnttab cache.
- `zfs_unmount()` unshares first, unmounts with `do_unmount()`, updates the cache, optionally unloads encryption-root keys, and disables zvol OS state.
- `zfs_unmountall()` and `zfs_unshareall()` use changelists for recursive mount/share-sensitive teardown.
- `zfs_share()`, `zfs_is_shared()`, `zfs_unshare()`, `zfs_commit_shares()`, and `zfs_truncate_shares()` wrap libshare NFS/SMB protocol operations based on `sharenfs` and `sharesmb`.
- `remove_mountpoint()` removes default or inherited mountpoint directories after dataset destruction/disable.
- `zpool_enable_datasets()` gathers eligible filesystems, mounts them in mountpoint order with optional parallelism, then serially shares them.
- `zpool_disable_datasets()` walks current mnttab entries for a pool, sorts mountpoints deepest-first, unshares, unmounts, removes eligible directories, and calls OS-specific disable logic.
- `zfs_foreach_mountpoint()` sorts by mountpoint and zone state, then dispatches callbacks serially or through a taskq that preserves parent-before-child mount ordering.

## State And Dependencies

The file depends on mnttab cache helpers, libshare, zone APIs, crypto key helpers, zpool properties, OS-specific `do_mount()`/`do_unmount()`/zvol hooks, changelists, task queues, mount constants, and filesystem stat/readdir calls.

## Risks And Invariants

Parent mountpoints must be processed before descendants; the custom comparator and task dispatch logic enforce that. Libshare is treated as not thread-safe, so sharing is serialized even when mounting is parallel. Mount option synthesis deliberately avoids current mount-option overrides by reading raw property nvlists. Unmount failures attempt to restore sharing where possible.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_mount.c -->