# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_inode.c

## Purpose
Provides Linux inode operation callbacks for ZFS files, directories, symlinks, and special nodes. It adapts lookup, create, mkdir, mknod, tmpfile, unlink, rmdir, rename, symlink, hardlink, getattr, setattr, ACL, and listxattr callbacks to ZFS vnode operations.

## Main APIs and Data
- `zpl_inode_operations`, `zpl_dir_inode_operations`, `zpl_symlink_inode_operations`, and `zpl_special_inode_operations` are exported operation tables.
- `zpl_lookup()` handles name lookup, longname policy, and case-insensitive dentry insertion.
- `zpl_vap_init()` prepares ZFS `vattr_t` creation attributes with idmap-aware UID/GID mapping and setgid inheritance.
- Creation paths include `zpl_create()`, `zpl_mknod()`, `zpl_tmpfile()`, `zpl_mkdir()`, and `zpl_symlink()`.
- Namespace mutation paths include `zpl_unlink()`, `zpl_rmdir()`, `zpl_rename2()`, and `zpl_link()`.
- Attribute paths include `zpl_getattr_impl()` and `zpl_setattr()`.

## Control Flow
Lookup enforces current longname settings: it rejects too-long create/rename targets while allowing access to existing long names when feature state permits. Case-insensitive datasets request the real name from `zfs_lookup()` and use `d_add_ci()` when the returned spelling differs.

Creation callbacks allocate `vattr_t`, initialize owner/group/mode, call the relevant ZFS create operation, then initialize security xattrs and POSIX ACLs. If post-create initialization fails, they remove the object, remove it from inode hash, and drop the inode. Tmpfile uses `zfs_tmpfile()` and wires the result into Linux’s tmpfile machinery.

Unlink/rmdir call ZFS remove operations and invalidate dentries on case-insensitive datasets to avoid negative dentry poisoning. Rename supports `RENAME_WHITEOUT` by creating a whiteout `vattr_t` for ZFS. Symlink creation mirrors file creation but omits ACL initialization. Hardlink checks `ZFS_LINK_MAX`, bumps ctime, grabs an inode ref, calls `zfs_link()`, and instantiates the new dentry.

Getattr uses `zfs_getattr_fast()` and conditionally populates Linux statx fields for birth time, NFS change cookie, direct-I/O alignment, and immutable/append/nodump attributes. Setattr validates with kernel helpers, converts idmapped UID/GID values, updates atime early when requested, calls `zfs_setattr()`, and adjusts POSIX ACLs after chmod.

## Integration Points
This is the central Linux VFS-to-ZFS namespace adapter. It depends on `zfs_vnops`, `zfs_znode`, ZFS idmap helpers, ACL/xattr initialization from `zpl_xattr.c`, SPL fstrans markers, Linux statx support, and kernel signature compatibility macros.

## Invariants and Edge Cases
- Longname constraints use both old `ZAP_MAXNAMELEN` and new `ZAP_MAXNAMELEN_NEW`.
- Case-insensitive filesystems avoid negative dentries after failed lookups and invalidated deletes.
- Setgid directories propagate group and setgid bit to subdirectories.
- Post-create security/ACL failure attempts to cleanly remove partially created objects.
- Symlink read rejects RCU path-walk by returning `-ECHILD` when no dentry is available.
- Change cookie combines ctime seconds and znode sequence to satisfy NFS monotonicity expectations.

## Risks and Testing Signals
Test longname feature toggles, case-insensitive lookup/delete/create, idmapped mounts, tmpfile behavior, security xattr and ACL failure cleanup, whiteout renames, statx change-cookie behavior under NFS, symlink reads, chmod ACL updates, and hardlink limit handling.
