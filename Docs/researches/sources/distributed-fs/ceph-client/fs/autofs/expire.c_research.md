# sources/distributed-fs/ceph-client/fs/autofs/expire.c

Purpose: Implements autofs expiry selection, busyness checks, daemon notifications, and waits for dentries or mount trees being expired.

Important APIs and functions: `autofs_expire_run()` supports the legacy expire packet ioctl. `autofs_do_expire_multi()` and `autofs_expire_multi()` drive modern repeated expiry. `autofs_expire_wait()` blocks lookups on entries being expired. Internal helpers check direct mounts, tree mounts, leaf expiry, mount busyness, positive dentry traversal, and candidate selection.

Control flow: Expiry starts with direct/trigger mounts through `autofs_expire_direct()` or indirect mounts through `autofs_expire_indirect()`. Candidate selection checks pending flags, mountpoints, symlinks, dentry reference counts, subtree busyness, forced/immediate flags, and per-dentry or superblock timeouts. A two-phase `WANT_EXPIRE` then `EXPIRING` transition uses `synchronize_rcu()` to block RCU-walk races before notifying the daemon through `autofs_wait()`.

State and persistence: Uses `autofs_info` flags, `last_used`, per-entry `exp_timeout`, and `expire_complete`. Busy checks refresh `last_used` to avoid rapid retries. Completion clears `EXPIRING` and `WANT_EXPIRE` and wakes waiters.

Dependencies and integration points: Depends on VFS dentry/mount traversal, `may_umount_tree()`, `path_has_submounts()` indirectly through ioctl flows, autofs wait queues, superblock type helpers, RCU, dentry locking, and daemon notification packet definitions.

Risks: Expiry correctness depends on dentry refcount heuristics and locking order around `lookup_lock`, `d_lock`, and `fs_lock`. Missing completion would hang waiters. Forced expiry intentionally delegates busy handling to userspace and changes safety assumptions.

Test signals: Direct trigger expiry, indirect mount expiry, tree versus leaf mode, forced/immediate flags, per-dentry timeout override including zero timeout, busy submounts updating `last_used`, RCU-walk returning `-ECHILD`, unhashed dentry returning `-EAGAIN`, and repeated expire until `-EAGAIN`.
