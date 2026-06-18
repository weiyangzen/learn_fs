# sources/distributed-fs/ceph-client/fs/ufs/cylinder.c

## Purpose
`cylinder.c` caches and loads UFS cylinder group metadata. It provides an LRU-like cache of cylinder group private info and buffer-head arrays used by allocation and inode code.

## Important APIs, types, and functions
Public functions are `ufs_put_cylinder` and `ufs_load_cylinder`; `ufs_read_cylinder` is internal. State lives in `struct ufs_sb_info` arrays `s_ucg`, `s_ucpi`, `s_cgno`, and `s_cg_loaded`, and in `struct ufs_cg_private_info`.

## Control flow
Reading a cylinder group fills an already allocated `ufs_cg_private_info`, attaches the first preloaded cylinder-group buffer plus any additional fragments, caches offsets such as inode bitmap, free bitmap, cluster summary, and rotors, then records the cache slot's cylinder number. Loading first checks slot 0, then direct-index mode when total groups fit in cache, otherwise searches loaded slots, promotes hits to slot 0, or evicts the least-recent slot with `ufs_put_cylinder` before reading the requested group.

## State and persistence
Runtime cache state stores buffer heads and decoded offsets/rotors. `ufs_put_cylinder` writes rotor fields back into the cylinder group buffer and marks it dirty, so allocation search position can persist.

## Dependencies and integration points
It depends on UFS superblock-private geometry, `ubh` buffer abstractions, cylinder group magic validation by callers, and block I/O. `balloc.c` and `ialloc.c` are primary consumers.

## Risks and test signals
Risks include stale buffer-head pointers after eviction, wrong cache promotion with many cylinder groups, failure cleanup leaking buffer references, and rotor updates being persisted unexpectedly late. Test signals include filesystems with fewer and more than `UFS_MAX_GROUP_LOADED` groups, repeated allocation across many groups, forced read failures of later cylinder group fragments, and unmount dirty-buffer checks.
