# sources/distributed-fs/ceph-client/fs/gfs2/sys.h

## Purpose
`sys.h` declares the small public surface for GFS2 sysfs integration and journal recovery triggering.

## Important APIs
`gfs2_sys_fs_add` and `gfs2_sys_fs_del` attach and detach per-mount sysfs kobjects. `gfs2_sys_init` and `gfs2_sys_uninit` create and destroy the global `gfs2` kset under `fs_kobj`. `gfs2_recover_set` starts recovery for a requested journal id.

## Control Flow And State
Module initialization calls `gfs2_sys_init`; each mount calls `gfs2_sys_fs_add` after enough superblock state exists for sysfs exposure; unmount calls `gfs2_sys_fs_del`; module exit calls `gfs2_sys_uninit`. Recovery callers can use `gfs2_recover_set` without knowing the sysfs parser details.

## Dependencies And Integration Points
The header forward-declares `struct gfs2_sbd` and includes spinlock support because the implementation coordinates with superblock and lockstruct state. It is consumed by mount, superblock teardown, and sysfs-related recovery code.

## Risks And Test Signals
Risks are mostly lifecycle ordering errors, such as deleting a sysfs object before attributes are removed or exposing sysfs before required superblock fields are initialized. Signals are clean mount/unmount cycles, sysfs file presence, recovery trigger behavior, and absence of kobject reference warnings.
