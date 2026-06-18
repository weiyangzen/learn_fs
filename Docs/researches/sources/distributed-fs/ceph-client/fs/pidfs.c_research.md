# sources/distributed-fs/ceph-client/fs/pidfs.c

## Purpose
`pidfs.c` implements the pidfs pseudo filesystem backing pidfds. It gives pidfds real inodes, stable file handles, polling, fdinfo, namespace and info ioctls, optional autokill-on-close, trusted xattrs, and export/open-by-handle support while keeping dentries stashed on `struct pid`.

## Important APIs, types, and functions
Lifecycle APIs include `pidfs_prepare_pid()`, `pidfs_add_pid()`, `pidfs_remove_pid()`, `pidfs_free_pid()`, `pidfs_register_pid()`, `pidfs_alloc_file()`, `pidfs_get_root()`, and `pidfs_init()`. Exit/coredump hooks are `pidfs_exit()` and `pidfs_coredump()`. File operations include `pidfd_poll()`, `pidfd_ioctl()`, `pidfd_show_fdinfo()`, and `pidfs_file_release()`. Export helpers include `pidfs_encode_fh()`, `pidfs_fh_to_dentry()`, `pidfs_export_open()`, and `pidfs_export_permission()`.

`struct pidfs_attr` stores optional simple xattrs and anonymous pidfd attributes: exit cgroup/exit code and coredump mask/signal/code. A global rhashtable maps 64-bit pidfs inode numbers to `struct pid`.

## Control flow
At boot, `pidfs_init()` initializes the rhashtable, creates the attr cache, mounts the pseudo filesystem, and stores the root path. `pidfs_add_pid()` allocates a unique inode number and inserts the pid in the hash; removal deletes it. `pidfs_alloc_file()` creates or reuses a stashed dentry via `path_from_stashed()`, opens it with `O_RDWR`, and preserves internal pidfd flags stripped by `do_dentry_open()`.

Pidfd poll waits on `pid->wait_pidfd` and reports readable/hangup when the task exits without delayed group-leader ambiguity. `PIDFD_GET_INFO` copies requested exit/coredump information from `pidfs_attr`, then live task credentials, cgroup id, ppid/tgid/pid, and supported-mask data when permitted by pid namespace hierarchy. Namespace ioctls fetch task namespace references after ptrace filesystem-credential checks and return namespace fds. File-handle open reconstructs a live pid from inode number, rejects exited or out-of-namespace pids, recreates the stashed path, and opens a pidfd-like file.

## State and persistence
Pidfs is pseudo/in-memory. Persistent-for-lifetime state lives in `struct pid`: `ino`, `pidfs_hash`, `attr`, and stashed dentry. On 64-bit, inode numbers come from a cookie; on 32-bit, the lower 32 bits are `i_ino` and upper 32 bits become `i_generation`. Exit and coredump attributes use write barriers before setting mask bits so readers see all-or-nothing data. Xattrs are stored in `simple_xattrs` under trusted.* and freed synchronously or via llist work when needed.

## Dependencies and integration points
The file integrates with pid allocation/free and task exit, proc fdinfo, cgroups, namespace APIs, ptrace access control, exportfs, pseudo_fs/stashed dentry helpers, anon-inode getattr/setattr behavior, rhashtable, simple xattrs, and pidfd UAPI definitions.

## Risks
Concurrency is central: pid exit races with pidfs registration, file-handle lookup, poll, and info ioctl. Namespace checks must prevent leaking information across pid namespace branches. Exported handles must not resurrect exited tasks. Xattr lazy allocation requires inode locking. `PIDFD_AUTOKILL` release must avoid kthreads/user workers.

## Test signals
Test pidfd inode/generation uniqueness on 32- and 64-bit, poll readiness for thread-group leader cases, fdinfo across pid namespaces, `PIDFD_GET_INFO` before and after exit/coredump, namespace ioctls and ptrace denial, open-by-handle for live/exited/out-of-namespace pids, autokill-on-close, trusted xattr set/list/get/remove, and cleanup after task creation failure with no pidfd.
