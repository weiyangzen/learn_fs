# Group Research: group_1453_openzfs_sources_cow_pools_openzfs_module_zfs_zfs_ioctl_c_sources_co_5d3bae7be9f8

Scope checked against `Docs/research_subset_a.md`: `sources/cow-pools/openzfs` is included in subset A. All three listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_ioctl.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_ioctl.c

## Role

`zfs_ioctl.c` is the central `/dev/zfs` ioctl implementation for OpenZFS. It is the kernel-facing control plane used by `zfs`, `zpool`, and `libzfs_core` to create and destroy pools, manipulate datasets and snapshots, manage vdevs, send/receive streams, set properties, register event/on-exit state, and initialize/finalize the ZFS kernel module.

The file contains both legacy `zfs_cmd_t` ioctl handlers and newer nvlist-based handlers registered through `zfs_ioctl_register()`.

## Main Components

- `zfs_ioc_vec_t` and `zfs_ioc_vec[]`: dispatch metadata for every ioctl, including handler pointer, security policy, name validation mode, pool-state requirements, history logging behavior, and accepted nvlist schema.
- Security policy helpers: `zfs_secpolicy_*()` functions enforce global-zone/local-zone visibility, delegated ZFS permissions, pool config privilege, send/raw-send permission, receive/create/mount permission, property-specific restrictions, and fault-injection privileges.
- `zfsdev_ioctl_common()`: common ioctl entry point. It validates command availability, nvlist source size, input nvpairs, dataset/pool/entity names, pool read-only/suspended state, runs secpolicy, dispatches either legacy or nvlist handler, copies out output nvlists, and logs successful mutating operations to pool history.
- Pool operations: create/import/export/destroy, configs/stats/history, scrub/scan, freeze/upgrade/reguid/sync/reopen/checkpoint/discard checkpoint/prefetch/DDT prune.
- Vdev operations: add/remove/attach/detach/split/set state/set path/set FRU, initialize, trim, and vdev property get/set.
- Dataset operations: create/clone/destroy/rename/promote/rollback, list children/snapshots, get stats/ZPL props/received props, object lookup/path/stats, next object, diff, space accounting.
- Snapshot/bookmark operations: create/destroy snapshots, temporary snapshots, user holds/releases, bookmarks and bookmark property lookup.
- Property operations: `zfs_set_prop_nvlist()`, `zfs_check_settable()`, `zfs_prop_set_special()`, received/local/inherited property handling, delayed receive properties, and namespace mount-cache refresh for mount-affecting properties.
- Send/receive operations: legacy and nvlist send/receive, stream size estimates, progress lookup, receive property rollback/restoration, resumable/raw/heal receive support, redaction handling.
- Encryption key operations: load/unload/change wrapping keys with hidden key material passed through nvlists.
- Device state: `/dev/zfs` minor allocation, per-open state, zevent/onexit state lookup, init, and teardown.
- Module lifecycle: `zfs_kmod_init()` initializes zvol, SPA, ZFS, ioctl tables, zoned UID callback, device state, TSD keys, and device attachment; `zfs_kmod_fini()` reverses this.

## Notable Local/Current Behavior

This copy includes explicit `zoned_uid` integration:

- `zfs_get_zoned_uid()` walks dataset ancestors, stripping snapshot suffixes, to find the delegation root where `zoned_uid` is set.
- Several permission paths call `zone_dataset_admin_check()` before normal `zoned` property logic.
- `zfs_secpolicy_zoned_uid_deleg()` uses DSL delegated permissions without requiring the traditional `zoned` property.
- Setting `ZFS_PROP_ZONED_UID` attaches/detaches kernel-side zone tracking.
- Destroy and rename preserve/clean up zone UID tracking via `zone_dataset_detach_uid()` and `zone_dataset_attach_uid()`.
- Module init/fini registers/unregisters `zfs_get_zoned_uid` with SPL zone support.

This is a significant authorization and namespace overlay on top of upstream-style ZFS delegation.

## Important Control Flow

1. Userland issues ioctl with `zfs_cmd_t`.
2. Platform wrapper maps request to vector index and calls `zfsdev_ioctl_common()`.
3. The common path optionally copies in and unpacks the input nvlist.
4. Dataset/pool/entity name is validated according to the registered ioctl.
5. Pool state is checked for suspended/read-only restrictions.
6. Nvlist keys are checked against the registered schema for non-legacy handlers.
7. Security policy runs before the handler.
8. Handler performs pool/dataset/vdev/ZIL/DMU/DSL operation.
9. Output nvlist is packed back to userland, optionally “smushed” for error-list style results.
10. Mutating/loggable ioctls record pool history and set TSD state for a follow-up `log_history`.

## Key Dependencies

- SPA/pool: `spa_*`, `vdev_*`, `spa_vdev_*`, `spa_checkpoint*`, `spa_wait*`
- DSL/DMU: `dsl_dataset_*`, `dsl_dir_*`, `dsl_prop_*`, `dmu_objset_*`, `dmu_recv_*`, `dmu_send_*`
- ZPL/ZFS mount layer: `zfsvfs_*`, `zfs_suspend_fs()`, `zfs_resume_fs()`, `zfs_set_version()`
- Zvol: `zvol_*`
- Delegation/security: `dsl_deleg_*`, `secpolicy_*`, `zone_dataset_*`
- Nvlists: `nvlist_*`, `fnvlist_*`
- On-exit/events: `zfs_onexit_*`, `zfs_zevent_*`

## Invariants And Safety Notes

- Ioctl numbers must remain stable across releases for user/kernel compatibility.
- Non-legacy ioctl schemas are enforced before handler execution, so handlers assume required keys exist and have expected types.
- `zfs_max_nvlist_src_size_os()` bounds user-provided source nvlist allocations to avoid kernel memory abuse.
- Pool write operations generally require both non-suspended and writeable pool checks.
- Several handlers perform best-effort rollback because operations like create-then-set-properties are not fully atomic.
- Receive property handling is especially delicate: it stashes original local/received props, delays props like `refquota` and `keylocation`, restores state on failure, and reports partial property errors.
- Some stats/object paths intentionally read from held but not fully owned objsets, with comments noting consistency limitations.
- On dataset rename/destroy, zoned UID side effects must stay synchronized with the DSL operation result.

## When Modifying

- New nvlist ioctls should be registered with `zfs_ioctl_register()` and a complete `zfs_ioc_key_t` schema.
- Add security policy before adding handler behavior; never rely on handler-side validation alone.
- For mutating operations, decide explicitly whether history logging and output nvlist smushing are appropriate.
- Any new dataset/pool name field outside `zc_name` needs explicit `*_namecheck()` validation.
- Be careful with local-zone and `zoned_uid` paths: a change in one secpolicy helper can alter delegation behavior across create, destroy, snapshot, rename, and setprop.
- For receive/send changes, verify legacy and nvlist entry points where both exist.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_log.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_log.c

## Role

`zfs_log.c` builds ZIL intent log records for ZFS filesystem operations. These routines are called inside DMU transactions and either create replayable in-memory `itx_t` records during normal operation or avoid/logically skip work while ZIL replay is already in progress.

## Main Components

- `zfs_log_create_txtype()`: maps create kind plus ACL/xvattr presence to the correct ZIL transaction type.
- `zfs_log_xvattr()`: serializes extended attribute masks and optional values into `lr_attr_t` trailing data.
- FUID helpers: `zfs_log_fuid_ids()` and `zfs_log_fuid_domains()` append FUID IDs and domain strings to log records.
- `zfs_xattr_owner_unlinked()`: suppresses logging for extended-attribute nodes whose owner is already unlinked.
- Namespace logging:
  - `zfs_log_create()`
  - `zfs_log_remove()`
  - `zfs_log_link()`
  - `zfs_log_symlink()`
  - `zfs_log_rename()`
  - `zfs_log_rename_exchange()`
  - `zfs_log_rename_whiteout()`
- Data and metadata logging:
  - `zfs_log_write()`
  - `zfs_log_truncate()`
  - `zfs_log_setattr()`
  - `zfs_log_setsaxattr()`
  - `zfs_log_acl()`
  - `zfs_log_clone_range()`

## Important Behavior

- Most functions return immediately when `zil_replaying(zilog, tx)` is true.
- Operations on unlinked znodes are generally not logged.
- Create logging encodes object IDs, dnode slot count, mode, UID/GID or FUID owner/group, generation, create time, rdev, optional xvattrs, optional ACLs, FUID metadata, and name.
- Remove logging calls `zil_remove_async()` for unlinked removed objects to prevent stale async write records from leaking into a reused object ID.
- Write logging chooses `WR_COPIED`, `WR_NEED_COPY`, or `WR_INDIRECT` through `zil_write_state()`, may inline data for copied writes, splits indirect writes on block boundaries, and accounts write-log bytes through `dsl_pool_wrlog_count()`.
- Clone-range logging splits block pointer arrays so each intent record stays within `zil_max_log_data()`.

## Dependencies

- ZIL internals: `zil_itx_create()`, `zil_itx_assign()`, `zil_write_state()`, `zil_max_copied_data()`, `zil_max_log_data()`
- Znode/SA accessors: `sa_lookup()`, `ZTOZSB()`, `ZTOUID()`, `ZTOGID()`
- DMU/dbuf for copied write data: `sa_get_db()`, `dmu_read_by_dnode()`
- FUID and ACL support: `zfs_fuid_info_t`, `vsecattr_t`, ACE/FUID record layout macros

## Invariants And Safety Notes

- These functions must be called within a DMU transaction.
- Record sizes are computed before allocation; trailing record payloads are packed manually, so size arithmetic must match replay-side decoding exactly.
- Replay compatibility depends on stable ZIL record layouts and transaction type choices.
- `zfs_log_write()` attaches the stable-storage callback only to the last generated write intent record for a logical write.
- Extended attribute owner checks differ slightly on FreeBSD because vnode lock semantics prevent the ordinary `zrele()` pattern.

## When Modifying

- Any record layout change must be mirrored in ZIL replay code and remain compatible with existing on-disk log records.
- Be conservative with new fields in packed trailing data; update size calculations first.
- Preserve replay and unlinked-object guards unless there is a precise replay-side reason to change them.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_log.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_onexit.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_onexit.c

## Role

`zfs_onexit.c` manages per-`/dev/zfs` file descriptor cleanup callbacks. It lets kernel ZFS operations accumulate state across multiple ioctls and guarantees cleanup when the associated process closes the cleanup fd or exits.

## Main Components

- `zfs_onexit_init()`: allocates a `zfs_onexit_t`, initializes its mutex, and creates the action list.
- `zfs_onexit_destroy()`: drains the action list, invoking every registered callback with its stored data, then destroys list/mutex state and frees the container.
- `zfs_onexit_fd_hold()`: validates a user-provided fd, gets the corresponding `/dev/zfs` minor through `zfsdev_getminor()`, verifies it has on-exit state, and returns a held `zfs_file_t`.
- `zfs_onexit_fd_rele()`: releases the held file reference.
- `zfs_onexit_minor_to_state()`: maps a minor to `ZST_ONEXIT` state.
- `zfs_onexit_add_cb()`: registers a callback/data pair and optionally returns the action handle, implemented as the address of the action node.

## Important Behavior

- The cleanup model is tied to `/dev/zfs` open-file private state and minor numbers owned in `zfs_ioctl.c`.
- Consumers are expected to call `zfs_onexit_fd_hold()` before doing work that will later add a callback, preventing the fd from disappearing between validation and registration.
- Destroy invokes callbacks outside the lock, then reacquires the lock before removing the next action. This avoids running arbitrary cleanup while holding the list mutex.
- Callback nodes are appended to the tail and executed in head-removal order during destroy.

## Dependencies

- `zfs_file_get()` / `zfs_file_put()` for fd lifetime.
- `zfsdev_getminor()` and `zfsdev_get_state()` from the ioctl/device layer.
- Kernel list/mutex/kmem primitives.
- Consumers include temporary snapshots and user holds in `zfs_ioctl.c`; comments also describe receive-side accumulated state.

## Invariants And Safety Notes

- `zfs_onexit_fd_hold()` returns `NULL` for invalid fd, invalid minor, or missing on-exit state.
- `zfs_onexit_add_cb()` requires a valid minor that maps to live on-exit state.
- The returned `action_handle` is a kernel pointer cast to `uintptr_t`; it is only meaningful to cooperating kernel paths that validate it against the minor-owned state.
- Callbacks must tolerate being invoked during fd close/process cleanup rather than during the original ioctl.

## When Modifying

- Preserve the hold/release protocol around fd-derived minor numbers.
- Do not run callbacks while holding `zo_lock`.
- Any new consumer should define clear ownership of callback data and ensure its callback fully frees or invalidates that state.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_onexit.c -->