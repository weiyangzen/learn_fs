# sources/distributed-fs/ceph-client/fs/gfs2/super.h

## Purpose
`super.h` is the public header for GFS2 superblock helpers and VFS operation tables. It defines supported on-disk filesystem format bounds and exposes lifecycle, journal, statfs, freeze, and teardown functions to the rest of GFS2.

## Important APIs, Types, And Functions
`GFS2_FS_FORMAT_MIN` and `GFS2_FS_FORMAT_MAX` gate on-disk format compatibility. `gfs2_jindex_size` reads `sd_journals` under `sd_jindex_spin`. Other declarations cover journal descriptor lookup/check/free, master-directory lookup, read-write/read-only transitions, online uevents, thread teardown, statfs conversion and sync, freeze work, local statfs inode lookup/free, and `free_sbd`.

The header exports `gfs2_fs_type`, `gfs2meta_fs_type`, `gfs2_export_ops`, `gfs2_super_ops`, `gfs2_dops`, and xattr handler arrays for minimum and maximum format variants.

## Control Flow And State
Callers use these functions during mount, remount, unmount, statfs, journal recovery, and VFS operation dispatch. State protected through these APIs includes journal lists, statfs deltas, per-node local statfs inodes, the live journal bit, and superblock-private lifecycle resources.

## Dependencies And Integration Points
The header includes Linux VFS/dcache types and GFS2 `incore.h`. It is included by mount code, xattr handling, sysfs, rgrp, util, and other filesystem subsystems needing superblock-level operations.

## Risks And Test Signals
The main risk is contract drift between prototypes and `super.c` or callers, especially around statfs and format-dependent xattr handlers. Build coverage, mount/remount tests, statfs tests, and xattr tests across minimum and maximum GFS2 formats are the relevant signals.
