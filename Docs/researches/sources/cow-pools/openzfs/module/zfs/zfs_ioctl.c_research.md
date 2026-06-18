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
