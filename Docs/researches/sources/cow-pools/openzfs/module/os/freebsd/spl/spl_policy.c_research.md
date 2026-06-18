# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_policy.c

FreeBSD implementation of Solaris-style security policy checks used by ZFS.

Key behavior:
- Maps ZFS/NFS/mount/inject/SMB and vnode operations to FreeBSD `priv_check_cred()` privileges.
- `secpolicy_fs_owner()` grants dataset super-owner behavior when `zfs_super_owner` is enabled and the mount credential matches uid and jail.
- Vnode access helpers check read/write/exec/lookup/admin privileges and owner fallbacks.
- `secpolicy_vnode_setattr()` enforces permissions for size, mode, owner/group, and timestamp changes, including setuid/setgid clearing.
- `secpolicy_setid_clear()` and `secpolicy_setid_setsticky_clear()` handle FreeBSD setid/sticky privilege rules.
- `secpolicy_fs_mount_clearopts()` forces nosuid/user mount flags when caller lacks non-user mount privilege.
- `secpolicy_xvattr()` gates system flags.

This file is central to matching Solaris policy call sites to FreeBSD credential and jail semantics.
