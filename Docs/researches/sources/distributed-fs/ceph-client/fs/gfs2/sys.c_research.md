# sources/distributed-fs/ceph-client/fs/gfs2/sys.c

## Purpose
`sys.c` implements the `/sys/fs/gfs2/<locktable>/` interface and per-filesystem kobject lifecycle. It exposes read-only status, administrative controls, lock-module controls, recovery triggers, and tunables.

## Important APIs, Types, And Functions
`struct gfs2_attr` wraps a sysfs attribute with GFS2-specific show/store callbacks. The exported functions are `gfs2_sys_fs_add`, `gfs2_sys_fs_del`, `gfs2_sys_init`, `gfs2_sys_uninit`, and `gfs2_recover_set`.

Top-level attributes include `id`, `fsname`, `uuid`, `freeze`, `withdraw`, `statfs_sync`, `quota_sync`, quota refresh controls, `demote_rq`, and `status`. `lock_module` attributes expose protocol name, lock blocking, withdraw-helper status, journal id assignment, first-mount coordination, and recovery control. `tune` attributes update quota, statfs, readahead, warning, new-files-jdata, and withdraw-helper timeout fields.

## Control Flow
All sysfs reads and writes dispatch through `gfs2_attr_show` and `gfs2_attr_store`, converting the kobject back to `struct gfs2_sbd`. `gfs2_sys_fs_add` initializes the kobject, creates default, tune, and lock-module groups, links the block device, and emits `KOBJ_ADD` with readonly and spectator environment variables. Deletion removes the link/groups, drops the kobject, and waits for release completion.

Administrative store handlers parse simple numeric commands, require `CAP_SYS_ADMIN` for mutation where needed, and call into freeze/thaw, withdraw, statfs, quota, glock demotion, and recovery code. `gfs2_recover_set` waits for the local journal to be ready, rejects recovery of the active non-spectator journal, locates a target journal descriptor, and queues recovery.

## State And Persistence
Most state is in-memory mount state: `sd_flags`, lockstruct fields, tune fields, journal id, completion objects, and log counters. Store operations can cause persistent effects indirectly by freezing, syncing quota/statfs, recovering journals, or withdrawing the filesystem. Kobject state persists only for the lifetime of the mounted filesystem.

## Dependencies And Integration Points
The sysfs layer integrates GFS2 with udev, lock managers, quota, recovery, glocks, freeze/thaw, and withdrawal helpers. `gfs2_uevent` adds locktable, lockproto, journal id, and UUID variables to kobject events.

## Risks And Test Signals
Risks include incorrect capability checks, accepting invalid tunable values, racing journal id assignment with lock initialization, recovery attempts during shutdown, and kobject cleanup leaks on partial setup failure. Test signals include sysfs permission/parse tests, manual recovery trigger tests, freeze/withdraw sysfs tests, uevent content, and lock-module coordination in clustered mounts.
