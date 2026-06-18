<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/self.c -->
## sources/distributed-fs/ceph-client/fs/proc/self.c

Purpose: implements the persistent `/proc/self` symlink, resolving at read time to the caller's thread-group ID in the proc mount's PID namespace.

Important APIs and functions: `proc_self_get_link`, `proc_setup_self`, and `proc_self_init`; global `self_inum` stores the allocated inode number.

Control flow: init allocates a stable proc inode number. Superblock fill calls `proc_setup_self`, which creates a persistent root dentry named `self`, allocates a symlink inode with `proc_self_inode_operations`, and attaches it with `d_make_persistent`. Link resolution computes `task_tgid_nr_ns(current, proc_pid_ns(inode->i_sb))`, allocates a decimal string, and frees it through delayed-call cleanup.

State and persistence behavior: each proc mount has a persistent dentry/inode for `self`, but the symlink target is dynamic per calling task and pid namespace. `self_inum` is initialized once and reused across mounts.

Dependencies and integration points: depends on proc superblock PID namespace state, scheduler task IDs, VFS delayed symlink cleanup, and proc root setup.

Risks: link resolution can fail with `-ENOENT` when current has no TGID in the mount namespace, and RCU-walk context requires atomic allocation or `-ECHILD`. The target format is ABI-stable.

Test signals: readlink `/proc/self` from init and nested PID namespaces; RCU path-walk behavior; persistent dentry creation failure during proc mount; compare target with `getpid()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/self.c -->
