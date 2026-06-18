## sources/distributed-fs/ceph-client/fs/open.c

### Purpose
This is the Linux VFS open and file metadata syscall implementation. It is not specific to Ceph or OrangeFS despite the source-tree prefix; it supplies the generic syscall and helper layer that filesystem implementations such as OrangeFS enter through file, inode, dentry, and address-space operations. It handles truncate/ftruncate, fallocate, access checks, cwd/root changes, chmod/chown, open/openat/openat2/creat, close, and generic open helpers.

### Important APIs, types, and functions
- `do_truncate()`, `vfs_truncate()`, `ksys_truncate()`, and `do_ftruncate()` build `struct iattr`, enforce object type, write permissions, leases, security hooks, and call `notify_change()`.
- `vfs_fallocate()` validates fallocate mode combinations, range overflow, append/immutable/swapfile restrictions, LSM and fsnotify write permissions, then calls `file->f_op->fallocate`.
- `do_faccessat()` implements `access`, `faccessat`, and `faccessat2`, optionally using temporary credentials from `access_override_creds()` for real-uid checks.
- `chmod_common()`, `vfs_fchmod()`, `do_fchmodat()`, `chown_common()`, `do_fchownat()`, and `vfs_fchown()` centralize ownership and mode updates through `notify_change()`.
- `do_dentry_open()`, `finish_open()`, `finish_no_open()`, `vfs_open()`, `dentry_open()`, `kernel_file_open()`, `file_open_name()`, `filp_open()`, and `file_open_root()` are the core open helpers.
- `build_open_how()` and `build_open_flags()` translate userspace flags and `openat2` resolve constraints into `struct open_flags`.
- `filp_close()`, `close`, `generic_file_open()`, `nonseekable_open()`, and `stream_open()` provide close and default open-mode behavior.

### Control flow
Truncate by path resolves a pathname, checks the inode type, acquires mount write access and inode write access, breaks leases, runs security hooks, then calls `do_truncate()` under the inode lock. Ftruncate starts from an already opened file and uses `super_write` scope before calling the same helper with `ATTR_FILE` and timestamp changes. Open syscalls normalize flags, copy `open_how` from userspace for `openat2`, resolve names through `do_file_open()`, allocate a `struct file`, and finish through `do_dentry_open()`. `do_dentry_open()` initializes path, inode, mapping, read/write accounting, write access, fsnotify and LSM checks, lease breaking, file operations, filesystem-specific `->open`, I/O capability bits, readahead state, and direct-I/O eligibility.

### State and persistence behavior
The file mutates VFS objects and per-file state rather than persisting its own data. Persistent effects are delegated through `notify_change()`, filesystem `->fallocate`, `->open`, `->flush`, and writeback paths. It manipulates mount write counts, inode write counts, file modes, fd table entries, working directory/root paths, and fsnotify/audit side effects.

### Dependencies and integration points
It depends on name lookup, mount idmapping, LSM hooks, fsnotify, leases, file locks, audit, fd tables, credentials, and filesystem operation vectors. OrangeFS integrates indirectly through `orangefs_file_operations`, `orangefs_dir_inode_operations`, `orangefs_setattr`, `orangefs_permission`, `orangefs_getattr`, and `orangefs_dentry_operations` when VFS helpers dispatch into filesystem callbacks.

### Risks
Flag normalization is security-sensitive, especially `O_PATH`, `O_TMPFILE`, `O_DIRECTORY|O_CREAT`, and `openat2` resolve constraints. Credential override for `access()` must stay synchronized between `access_need_override_creds()` and `access_override_creds()`. Truncate/chown/chmod paths depend on correct idmapping and delegation retry behavior. `do_dentry_open()` has many cleanup paths where path, fops, write access, and file state must remain balanced.

### Test signals
Relevant tests include LTP or xfstests coverage for open/openat2 flag validation, truncate and ftruncate permissions, fallocate modes, chmod/chown idmapped mounts, O_DIRECT capability, close flush error behavior, and filesystem-specific tests ensuring OrangeFS callbacks receive correct VFS preconditions.
