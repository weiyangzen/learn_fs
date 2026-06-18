## sources/distributed-fs/ceph-client/fs/orangefs/namei.c

### Purpose
This file implements OrangeFS namespace inode operations for directories: lookup, create, unlink/rmdir, symlink, mkdir, and rename.

### Important APIs, types, and functions
- `orangefs_create()` sends `ORANGEFS_VFS_OP_CREATE`, creates a VFS inode from the returned handle, instantiates the dentry, and updates parent times.
- `orangefs_lookup()` sends `ORANGEFS_VFS_OP_LOOKUP`, maps success to `orangefs_iget()`, maps `-ENOENT` to a negative dentry, and uses `d_splice_alias()`.
- `orangefs_unlink()` sends `ORANGEFS_VFS_OP_REMOVE`, drops link count, and updates parent times.
- `orangefs_symlink()` sends `ORANGEFS_VFS_OP_SYMLINK`, creates a symlink inode, fixes symlink size locally, and instantiates the dentry.
- `orangefs_mkdir()` sends `ORANGEFS_VFS_OP_MKDIR`, creates a directory inode, and keeps directory nlink effectively constant.
- `orangefs_rename()` sends `ORANGEFS_VFS_OP_RENAME` and updates directory/target ctime.
- `orangefs_dir_inode_operations` exports the directory inode operation vector.

### Control flow
All namespace mutations allocate an operation, fill parent refs, names, and default attrs, call `service_operation()`, then reconcile VFS state from returned OrangeFS handles. Successful create-like operations call `orangefs_new_inode()`, `d_instantiate_new()`, and `orangefs_set_timeout()`. Parent mtime/ctime updates are performed locally through `__orangefs_setattr()` after success. Lookup always queries the server even in create-intent paths to preserve `O_EXCL` semantics.

### State and persistence behavior
Namespace state persists on the OrangeFS server via userspace daemon operations. Local dentry timeouts are refreshed after successful lookup/create/mkdir/symlink. Parent timestamps are locally marked and synced through OrangeFS setattr machinery.

### Dependencies and integration points
Depends on operation service, inode allocation in `inode.c`, timeout helpers, default sys_attr macro, and VFS dentry/inode operation contracts. Directory operation vector is installed for directory inodes by `orangefs_init_iops()`.

### Risks
Most operations are multi-phase: server mutation can succeed while local inode instantiation or ACL setup fails. Rename rejects all flags, so newer VFS rename modes are unsupported. `orangefs_mkdir()` returns `ERR_PTR(ret)` even though modern mkdir inode op signatures normally return a dentry pointer in this tree, making signature compatibility important. Parent timestamp updates are best-effort relative to the server mutation.

### Test signals
Test create/open exclusive behavior, lookup negative caching, unlink/rmdir, symlink target length and size, mkdir ACL inheritance, rename overwrite and unsupported flags, cross-client namespace visibility, daemon failure after server success, and parent timestamp changes.
