# sources/distributed-fs/ceph-client/fs/jfs/ioctl.c

## Purpose
Implements JFS file attribute get/set support and FITRIM ioctl handling.

## Important APIs, types, and functions
`jfs_map_ext2()` maps JFS `mode2` flags to generic `FS_*_FL`. `jfs_fileattr_get()` and `jfs_fileattr_set()` expose file attributes. `jfs_ioctl()` handles `FITRIM`.

## Control flow
Fileattr get/set reject special files; set rejects fsx attributes, filters unsupported bits, blocks quota files, updates `mode2`, refreshes inode flags, updates ctime, and marks dirty. FITRIM requires `CAP_SYS_ADMIN`, checks device discard support, copies/clamps `fstrim_range`, calls `jfs_ioc_trim()`, and copies results back.

## State and persistence behavior
File flags persist in `mode2` after inode commit. FITRIM preserves logical allocation state while discard code trims free ranges and reports bytes discarded.

## Dependencies and integration points
Depends on Linux fileattr/ioctl/capability APIs, block-device discard limits, userspace copy helpers, JFS inode flags, dmap, and discard code.

## Risks and test signals
Test chattr/lsattr mappings, special files, quota files, directory-only dirsync, unknown ioctls, FITRIM privilege/device checks, and range/minlen clamping.
