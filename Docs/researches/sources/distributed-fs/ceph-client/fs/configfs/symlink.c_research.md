# sources/distributed-fs/ceph-client/fs/configfs/symlink.c

Purpose: implements configfs symlink creation and removal. Configfs symlinks are resolved at creation time to a target config item and keep that target busy against removal.

Important APIs/functions: `configfs_symlink_mutex` serializes symlink attach against rmdir. Path helpers compute a relative symlink body from source item to target. `get_target()` resolves the user path with `kern_path()`, requires the same superblock, and takes a target config item reference. `configfs_symlink()` validates parent item operations, temporarily drops the parent inode lock to resolve the target, calls client `allow_link()`, and creates the link. `configfs_unlink()` drops the dirent, calls optional `drop_link()`, decrements the target link count, and releases references.

Control flow: user `symlink(2)` supplies a target path. The target is looked up before relocking the parent to avoid VFS deadlocks, then the code revalidates the destination dentry and permissions. Successful creation increments `target_sd->s_links`, stores a relative path body in the symlink inode, and pins target dirent references. Unlink removes the link before decrementing target link count.

State and persistence: symlink bodies are heap strings freed by `mount.c` inode free. Target dirents track `s_links`; rmdir rejects linked targets. Links are RAM-only configfs entries.

Dependencies/integration: depends on public configfs `allow_link`/`drop_link` callbacks, dentry/path lookup, `dir.c` link creation and rmdir checks, and `inode.c` setattr.

Risks: the ABI intentionally differs from normal symlink semantics by resolving and pinning the target at creation. Locking is delicate because target lookup cannot happen with the parent directory locked. `drop_link()` ordering before decrementing target links preserves client cleanup ordering.

Test signals: valid same-configfs links, cross-superblock target rejection, missing target, target in creating/dropping state, rmdir blocked by links, unlink callback ordering, long relative paths returning `-ENAMETOOLONG`, and races with rmdir/mkdir.
