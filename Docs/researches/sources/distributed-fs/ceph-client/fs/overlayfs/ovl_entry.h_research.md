# sources/distributed-fs/ceph-client/fs/overlayfs/ovl_entry.h

## Purpose
`ovl_entry.h` defines the core in-memory objects that represent an OverlayFS mount, layer, path, dentry entry, and inode. These are the private data structures used across superblock setup, lookup, readdir, copy-up, xattrs, and inode operations.

## Important APIs, types, and functions
`struct ovl_config` stores resolved mount options: upper/work/lower path strings, permission mode, redirect/verity/uuid/xino/fsync modes, and feature booleans such as `index`, `nfs_export`, `metacopy`, and `userxattr`. `struct ovl_sb` tracks each unique underlying superblock, its pseudo device, UUID conflict status, and whether it is used as a lower. `struct ovl_layer` maps a layer to a cloned mount, trap inode, fs entry, layer index, fsid, and xwhiteout state. `struct ovl_path` pairs a layer with a real dentry.

`struct ovl_entry` is a flex-array object holding a lower stack for an overlay inode/dentry. `struct ovl_fs` is the mount-private superblock state: layer arrays, work/index directories, namelen, config, creator credentials, capability probe results, in-use locks, trap inodes, xino mode, whiteout cache, volatile error sequence, and casefold state. `struct ovl_inode` embeds `struct inode` and stores per-inode cache/redirect data, version, flags, upper dentry, lower entry, and a mutex.

Inline accessors include `OVL_FS()`, `ovl_numlowerlayer()`, `ovl_upper_mnt()`, `ovl_upper_mnt_idmap()`, `ovl_numlower()`, `ovl_lowerstack()`, `ovl_lowerdata()`, `ovl_lowerdata_dentry()`, `OVL_E_FLAGS()`, `OVL_I()`, `OVL_I_E()`, `OVL_E()`, and `ovl_upperdentry_dereference()`.

## Control flow
These structures are allocated during mount (`ovl_fs`, layers, root `ovl_entry`) and lookup (`ovl_entry`, `ovl_inode`). Runtime helpers select upper/lower/data paths by reading these objects. Lookup may populate lowerdata lazily, while copy-up updates the upper dentry and flags under `ovl_inode.lock`.

## State and persistence
The file itself contains no on-disk format, but its fields mirror persistent OverlayFS concepts: lower/upper/work paths, stable fsid/xino policy, index/work directories, origin/lowerdata references, and volatile mount error tracking. References are owned carefully: layer mounts are unmounted by `ovl_free_fs()`, lower dentries are refcounted in `ovl_entry`, upper dentries are held by `ovl_inode`, and trap inodes prevent overlap cycles.

## Dependencies and integration points
The header is included by `overlayfs.h`, making these definitions globally available to the OverlayFS implementation. It assumes VFS objects such as `super_block`, `vfsmount`, `dentry`, `inode`, credentials, mutexes, and atomics.

## Risks
The first member of `struct ovl_layer` must remain `mnt` because `ovl_free_fs()` reuses layout assumptions while unmounting. Flexible-array sizing and reference ownership are safety-sensitive. Memory ordering around `__upperdentry` and lowerdata requires the accessors in `util.c` to be used consistently.

## Test signals
Tests should stress mount/unmount cleanup, copy-up races, lazy lowerdata lookup, multiple lower/data layers, overlapping-layer rejection, xino/fsid behavior, and directory cache lifetime. Debug builds should watch for `WARN_ON_ONCE()` checks in `OVL_FS()` and lowerdata accessors.
