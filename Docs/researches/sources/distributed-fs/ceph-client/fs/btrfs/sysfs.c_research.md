# sources/distributed-fs/ceph-client/fs/btrfs/sysfs.c

## Purpose

`sysfs.c` is the Btrfs sysfs surface. It creates the global `/sys/fs/btrfs` kset, publishes kernel-supported feature files, and adds per-filesystem, per-device, per-allocation, discard, and qgroup kobjects under `/sys/fs/btrfs/<uuid>`. It is runtime integration code rather than an algorithm module: it turns `btrfs_fs_info`, `btrfs_fs_devices`, `btrfs_device`, `btrfs_space_info`, block group profile, and qgroup state into sysfs attributes and accepts a small set of privileged tunables.

## Important APIs, Types, And Functions

- `struct btrfs_feature_attr` wraps `struct kobj_attribute` with a feature set and bit. `BTRFS_FEAT_ATTR_*` instantiate known feature files.
- `struct raid_kobject` stores a RAID profile flag plus a `kobject` for `/allocation/<space>/<profile>`.
- Attribute macros `BTRFS_ATTR`, `BTRFS_ATTR_RW`, `BTRFS_ATTR_W`, and `BTRFS_ATTR_PTR` centralize kobj attribute creation.
- Feature helpers: `get_features()`, `set_features()`, `can_modify_feature()`, `btrfs_feature_attr_show()`, `btrfs_feature_attr_store()`, `btrfs_feature_visible()`, `init_feature_attrs()`, `addrm_unknown_feature_attrs()`, `btrfs_printable_features()`, and `btrfs_feature_set_name()`.
- Lifecycle APIs exported through `sysfs.h`: `btrfs_init_sysfs()`, `btrfs_exit_sysfs()`, `btrfs_sysfs_add_fsid()`, `btrfs_sysfs_remove_fsid()`, `btrfs_sysfs_add_mounted()`, `btrfs_sysfs_remove_mounted()`, `btrfs_sysfs_add_device()`, `btrfs_sysfs_remove_device()`, `btrfs_sysfs_add_space_info_type()`, `btrfs_sysfs_remove_space_info()`, `btrfs_sysfs_add_block_group_type()`, qgroup add/remove helpers, and rename/update helpers for fsid/devid.
- Tunable show/store handlers cover filesystem label, feature bits, discard limits, space-info chunk size and reclaim thresholds, global read policy, quota override, commit stats reset, device scrub speed limit, and qgroup subtree drop threshold.

## Control Flow

Module initialization calls `btrfs_init_sysfs()`, creates the `btrfs` kset under `fs_kobj`, initializes printable/unknown feature metadata, creates the dynamic feature group, merges static feature files, and optionally creates a debug group. Shutdown reverses those groups and unregisters the kset.

Device discovery can call `btrfs_sysfs_add_fsid()` before mount. It initializes the fsid kobject named by UUID and creates child `devices` and `devinfo` directories. Mount completion calls `btrfs_sysfs_add_mounted()`, which adds device links and devinfo entries, per-fs attributes, feature group, optional debug directory, discard directory, unknown feature files, the `bdi` link, and the top-level `allocation` directory.

Space information is added after allocation state exists. `btrfs_sysfs_add_space_info_type()` creates `/allocation/<type>` from `alloc_name()`. `btrfs_sysfs_add_block_group_type()` creates one child kobject per RAID profile under a space-info kobject, using `memalloc_nofs_save()` to avoid reclaim recursion during transaction or lock contexts. Removal walks RAID profile kobjects and then drops the space-info kobject.

Unmount uses `btrfs_sysfs_remove_mounted()` to remove links, files, child kobjects, unknown feature attributes, feature group, mounted attributes, and all device entries. `btrfs_sysfs_remove_fsid()` removes the base fsid tree for one filesystem or all known fsids.

Qgroup sysfs integration is lazy around qgroup initialization. `btrfs_sysfs_add_qgroups()` creates `/qgroups`, then adds one kobject per qgroup from `fs_info->qgroup_tree`; deletion walks the tree and drops children before the parent.

## State And Persistence Behavior

Sysfs files mostly reflect in-memory kernel state. Some store paths mutate persistent filesystem-superblock-related state indirectly:

- Feature bit and label changes update `fs_info->super_copy` under `super_lock`, set `BTRFS_FS_NEED_TRANS_COMMIT`, and wake `transaction_kthread`; the sysfs write itself does not commit a transaction.
- Read policy and discard limits update live `fs_devices` or `discard_ctl` fields with `READ_ONCE`/`WRITE_ONCE`; discard writes may reschedule discard work.
- Chunk size and reclaim thresholds update live `btrfs_space_info`/`fs_info` policy fields.
- Qgroup show/store handlers read or update qgroup flags/thresholds under `qgroup_lock`.
- Kobject state is embedded in long-lived Btrfs structures. Release callbacks zero embedded kobject storage and complete unregister completions so callers can wait for sysfs teardown.

## Dependencies And Integration Points

This file depends heavily on Linux kobject/sysfs APIs, Btrfs feature flag accessors, the transaction subsystem, discard work scheduling, space-info/block-group state, device-volume structures, qgroups, and superblock accessors. It is called from mount, unmount, device discovery, device add/remove/replace, chunk allocation, qgroup initialization, and module init/exit paths.

External observability is the sysfs ABI under `/sys/fs/btrfs`. It also sends block device uevents through `btrfs_kobject_uevent()` and maintains user-visible links to block devices and BDI state.

## Risks

The highest risk is lifetime ordering: sysfs kobjects expose embedded structures while mount/unmount, device removal, qgroup deletion, and seed-device teardown are possible. The code mitigates this with `state_initialized`, release callbacks, completions, and paired `kobject_del()`/`kobject_put()`, but double-add/double-remove and missing parent kobjects would still be dangerous.

Store methods need privilege and input validation discipline. Some paths require `CAP_SYS_ADMIN` or `CAP_SYS_RESOURCE`, reject read-only filesystems, parse with `kstrto*()` or `memparse()`, and bound values such as chunk size, thresholds, and read-policy parameters. Any new tunable should follow the same pattern and consider whether it can safely run in sysfs context.

Feature writes are intentionally limited to safe set/clear masks. Unknown feature files are dynamically added for unsupported bits so users can observe them but not mutate them. This avoids hiding important compatibility state.

## Test Signals

There is no direct unit test in this subset for sysfs. Test signals are integration-style: mount/unmount should create and remove the expected sysfs tree; feature visibility should match superblock flags; store handlers should reject invalid input, readonly filesystems, and missing capabilities; qgroup and device directories should appear and disappear with qgroup/device lifecycle. The selftests in this subset exercise many underlying data structures but not kobject/sysfs behavior directly.
