# sources/distributed-fs/ceph-client/fs/autofs/root.c

Purpose: implements autofs root/directory file operations, dentry automount management, lookup behavior, daemon-controlled creation/removal of mount triggers, and root ioctls for daemon coordination.

Important APIs/types/functions: exports `autofs_root_operations`, `autofs_dir_operations`, `autofs_dir_inode_operations`, and `autofs_dentry_operations`. Key routines are `autofs_d_automount`, `autofs_d_manage`, `autofs_lookup`, `autofs_lookup_active`, `autofs_lookup_expiring`, `autofs_mount_wait`, `do_expire_wait`, `autofs_mountpoint_changed`, directory create/remove helpers, timeout/protocol ioctls, `is_autofs_dentry`, and `autofs_root_ioctl_unlocked`.

Control flow: path walks call `.d_manage` to decide whether to stop at a managed dentry, wait for pending expire/mount work, or return `-EISDIR` to suppress automount. `.d_automount` rejects daemon-triggered mounts, enforces namespace/private propagation checks, waits for expires, marks dentries pending, notifies the daemon via `autofs_wait()`, and rechecks whether userspace replaced the dentry. Lookup reuses active unhashed dentries or creates a negative dentry with attached `autofs_info` and managed flags when it is a root trigger.

State and persistence: maintains in-memory active and expiring lists under `lookup_lock`, per-dentry child counts, pending/expiring flags under `fs_lock`, and mtime/ctime/nlink transitions for synthetic directories and symlinks. Removal uses `d_drop()` and expiring lists rather than normal negative-dentry invalidation so racing path walks can wait on expire completion.

Dependencies and integration: depends on `waitq.c` for mount/expire daemon waits, `expire.c` for expiration helpers, VFS dentry management flags, mount namespace propagation checks, capability checks, and autofs UAPI ioctls (`READY`, `FAIL`, `CATATONIC`, `EXPIRE`, `EXPIRE_MULTI`, timeout, protocol queries).

Risks: dentry lifetime and lock ordering are delicate because active/expiring lists race with RCU path walk, expire, daemon mutations, and dentry release. Incorrect managed-flag handling can cause spurious `ELOOP`, missed automounts, or repeated daemon callbacks. The ioctl path must restrict non-daemon callers unless privileged.

Test signals: concurrent lookup/open/stat during mount and expire; daemon `READY`/`FAIL` ioctl behavior; v4 pseudo-direct leaf automount flag transitions; namespace/private propagation denial; compat timeout ioctl; KCSAN/lockdep around active and expiring list churn.
