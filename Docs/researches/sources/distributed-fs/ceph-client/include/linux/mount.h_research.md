<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mount.h -->
# sources/distributed-fs/ceph-client/include/linux/mount.h

## Purpose
`mount.h` declares the core VFS mount object, mount flags, write access helpers, mount creation/destruction APIs, expiry helpers, mountpoint checks, and kernel mount helpers.

## Important APIs, Types, and Functions
It defines `enum mount_flags`, including user-settable flags (`MNT_NOSUID`, `MNT_NODEV`, `MNT_NOEXEC`, atime flags, `MNT_READONLY`, `MNT_NOSYMFOLLOW`), internal flags (`MNT_INTERNAL`, `MNT_DOOMED`, `MNT_SYNC_UMOUNT`, `MNT_LOCKED`), lock flags, and masks. `struct vfsmount` contains `mnt_root`, `mnt_sb`, `mnt_flags`, and `mnt_idmap`. `mnt_idmap()` reads the mount idmap with release/acquire pairing expectations.

Declared APIs include `mnt_want_write()`, `mnt_want_write_file()`, `mnt_drop_write()`, `mnt_drop_write_file()`, `mntput()`, `mntget()`, `mnt_make_shortterm()`, `mnt_clone_internal()`, `__mnt_is_readonly()`, `mnt_may_suid()`, `clone_private_mount()`, `mnt_get_write_access()`, `mnt_put_write_access()`, `fc_mount()`, `fc_mount_longterm()`, `vfs_create_mount()`, `vfs_kern_mount()`, expiry helpers, `path_is_mountpoint()`, `our_mnt()`, `kern_mount()`, `kern_unmount()`, `may_umount_tree()`, `may_umount()`, `do_mount()`, path collection helpers, `kern_unmount_array()`, and `cifs_root_data()`.

## Control Flow and State
Mount creation flows from filesystem context or filesystem type into a `vfsmount`. Write paths first acquire mount write access and drop it afterward. Unmount paths test whether trees can be unmounted, mark/expire mounts, and release references. Idmapped mounts read `mnt_idmap` through `mnt_idmap()`.

## State and Persistence Behavior
`vfsmount` is runtime VFS state. It references persistent superblocks/dentries but is itself namespace/mount-table state. Mount flags are user-visible through mount APIs and proc views; write access counters and internal flags are transient.

## Dependencies and Integration Points
It integrates with superblocks, dentries, paths, file descriptors, filesystem contexts, user namespaces, mount namespaces, idmapping, CIFS root parsing, and kernel-internal mounts.

## Risks
Incorrect write-access pairing can allow writes on read-only mounts or block unmount. Mount flag locking must prevent privilege changes. `mnt_idmap()` ordering matters for idmapped mount setup. Reference leaks in `mntget()`/`mntput()` keep mounts alive.

## Test Signals
Mount/umount stress, remount read-only/write tests, idmapped mounts, nosuid/nodev/noexec enforcement, mount expiry, kernel mount/unmount helpers, and CIFS root mount parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mount.h -->
