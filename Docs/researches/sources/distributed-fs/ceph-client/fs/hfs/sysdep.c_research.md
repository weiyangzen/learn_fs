# sources/distributed-fs/ceph-client/fs/hfs/sysdep.c

Purpose: provides HFS dentry operations and timezone revalidation behavior needed because classic HFS timestamps are stored relative to local-time conventions.

Important APIs and control flow: `hfs_revalidate_dentry()` rejects RCU lookup with `-ECHILD`, returns valid for negative dentries, and for positive dentries adjusts ctime/atime/mtime by the difference between current `sys_tz.tz_minuteswest` and the inode's stored `tz_secondswest`. `hfs_dentry_operations` wires this revalidator together with `hfs_hash_dentry()` and `hfs_compare_dentry()`.

State and persistence: only in-memory inode timestamps and `HFS_I(inode)->tz_secondswest` are adjusted during dentry revalidation. No disk write is performed directly, but adjusted times could later be written through inode writeback if the inode becomes dirty through other paths.

Dependencies and integration: depends on Linux namei/dcache APIs and `hfs_fs.h`. `super.c` installs `hfs_dentry_operations` as default dentry operations after mounting the root.

Risks and test signals: global timezone changes can shift visible timestamps during lookup, and RCU walk fallback is required. Tests should simulate timezone changes, verify repeated revalidation does not double-adjust, and cover hash/compare consistency under dcache lookup.
