# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vfsops.c

## Purpose
Solaris VFS/module glue for the OpenAFS filesystem, syscall/ioctl hooks, root vnode acquisition, VFS operation registration, UFS/NFS translator symbol lookup, and module lifecycle.

## Important APIs, Types, and Functions
Defines `afs_mount`, `afs_unmount`, `gafs_freevfs`, `afs_root`, `afs_statvfs`, `afs_sync`, `afs_vget`, `afs_mountroot`, `afs_swapvp`, `afsinit`, `_init`, `_info`, `_fini`, and operation tables/templates. Tracks syscall originals and UFS/NFS function pointers.

## Control Flow
Mount checks privileges, rejects remount, initializes `afs_globalVFS`, fsid, block size, and dev. Unmount checks privilege, rejects forced unmount, enforces VFS/root vnode refcount constraints, marks VFS unmounted, and releases root. Root fetches or refreshes `afs_globalVp`, carefully drops covered-vnode lock if an RPC may occur, holds the root vnode, and sets `VROOT`. `afsinit` hooks setgroups/ioctl syscalls, registers VFS/vnode ops, looks up NFS translator and UFS symbols, and marks initialized. `_init` verifies required modules, initializes locks, installs module linkage, and restores hooks on failure.

## State and Persistence
Global state includes `afs_globalVFS`, `afs_globalVp`, `afsfstype`, syscall hook originals, UFS function pointers, NFS translator pointers, module init flag, and VFS/vnode op registrations.

## Dependencies and Integration Points
Depends on Solaris module subsystem, VFS op registration (`vfs_setfsops`, `vn_make_ops`), syscall tables, `modlookup`, UFS, optional `nfssrv`, `osi_ioctl.c` for Solaris 11 `/dev/afs`, and common AFS init/shutdown.

## Risks
Syscall table patching and restoration are high risk, especially 32-bit table variants. Module loading depends on UFS and optional NFS modules being present. Root acquisition includes lock dropping to avoid deadlocks. Unmount depends on exact refcounts.

## Test Signals
Module load/unload success/failure paths, missing UFS/NFS modules, mount permission checks, duplicate mount rejection, root vnode retrieval, statvfs values, busy unmount, syscall hook restoration, and Solaris 10/11 op registration.
