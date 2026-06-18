<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/namespaces.c -->
## sources/distributed-fs/ceph-client/fs/proc/namespaces.c

Purpose: implements `/proc/<pid>/ns`, exposing namespace membership as symlinks and directory entries for configured namespace types.

Important APIs and functions: the `ns_entries` table selects enabled `proc_ns_operations`. Core functions are `proc_ns_get_link`, `proc_ns_readlink`, `proc_ns_instantiate`, `proc_ns_dir_readdir`, and `proc_ns_dir_lookup`. Exports `proc_ns_dir_operations` and `proc_ns_dir_inode_operations`.

Control flow: readdir obtains the task from the proc inode, emits dots, and emits one entry per enabled namespace operation using `proc_fill_cache`. Lookup scans `ns_entries` by name and instantiates a symlink inode bound to that namespace operation. Symlink traversal enforces `ptrace_may_access(PTRACE_MODE_READ_FSCREDS)`, obtains the namespace path via `ns_get_path`, and jumps to the nsfs dentry; readlink formats the namespace name via `ns_get_name`.

State and persistence behavior: namespace link inodes carry `PROC_I(inode)->ns_ops` and task PID state inherited from `proc_pid_make_inode`. Dentries use PID dentry operations so they revalidate against task lifetime. No namespace reference persists in the proc inode beyond operation metadata; the target path is obtained at access time.

Dependencies and integration points: integrates proc pid lookup, nsfs operations, ptrace access checks, pid/user/net/uts/ipc/mnt/cgroup/time namespace implementations, and VFS symlink/readlink handling.

Risks: namespace symlinks are security-sensitive because they reveal and can open namespace file descriptors; ptrace-mode checks must be preserved. Task exit can race lookup/readlink. Config-dependent table order is user-visible in directory listings.

Test signals: list and read `/proc/<pid>/ns` across namespace configs; permission denial under ptrace restrictions; task exit during readdir/readlink; `setns` users opening namespace symlinks; nested pid/user namespace behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/namespaces.c -->
