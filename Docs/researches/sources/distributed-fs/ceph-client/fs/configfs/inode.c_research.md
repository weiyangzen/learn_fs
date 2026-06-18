# sources/distributed-fs/ceph-client/fs/configfs/inode.c

Purpose: provides configfs inode creation, persistent attribute metadata handling, dentry dropping, and lockdep class assignment for default groups.

Important APIs/functions: `configfs_setattr()` stores changed uid/gid/mode/timestamps in `sd->s_iattr` after `simple_setattr()`. `configfs_new_inode()` allocates a new inode, assigns `ram_aops`, default inode operations, inode number, and either default or saved attributes. `configfs_create()` validates a negative dentry, creates an inode, updates parent mtime/ctime, and assigns lock classes for default groups. `configfs_get_name()` maps dirents to directory/link dentry names or attribute names. `configfs_drop_dentry()` unhashes and unlinks instantiated attribute/link dentries.

Control flow: dir/link/attribute creation first creates a dirent, then calls `configfs_create()` to allocate the inode. Later chmod/chown calls update both inode and dirent so attributes survive dentry eviction and recreation. Removal paths call `configfs_drop_dentry()` while holding the parent inode mutex.

State and persistence: configfs is RAM-only, but `s_iattr` persists metadata for each dirent while the config item exists. Inode numbers are generated with `get_next_ino()`.

Dependencies/integration: used by `dir.c`, `file.c`, `mount.c`, and `symlink.c`; depends on VFS simple inode helpers, ram address-space ops, capabilities, and lockdep when enabled.

Risks: `sd->s_iattr` allocation happens on first setattr and must be freed with the dirent. `ATTR_MODE` must clear `S_ISGID` correctly when callers lack permissions. Dentry dropping races are coordinated with parent inode locks and dentry locks.

Test signals: chmod/chown persistence after lookup eviction, directory/link/attribute inode modes, lockdep class behavior for nested default groups, dentry drop while file open, and setattr permission/capability cases.
