# sources/distributed-fs/ceph-client/fs/proc/fd.c

Purpose: Implements `/proc/<pid>/fd` symlinks and `/proc/<pid>/fdinfo` files for per-task file descriptors.

Important APIs and types: Exports `proc_fd_operations`, `proc_fd_inode_operations`, `proc_fdinfo_operations`, `proc_fdinfo_inode_operations`, and `proc_fd_permission()`. It uses `struct fd_data`, `proc_fd(inode)`, `fget_task()`, `fget_task_next()`, `files_lookup_fd_locked()`, `show_fd_locks()`, `file->f_op->show_fdinfo`, `proc_pid_link_inode_operations`, and dentry revalidation through `tid_fd_dentry_operations`.

Control flow: Lookup parses a numeric fd name, verifies that the target task still has the fd, captures mode, and instantiates either a symlink inode for `/fd/N` or a regular file for `/fdinfo/N`. Readdir emits numeric fd names by iterating open descriptors with `fget_task_next()` and filling proc cache entries. `/fd/N` symlink resolution gets the target file path and jumps to it. `/fdinfo/N` opens a single seq file that snapshots position, flags including close-on-exec, mount ID, inode number, locks, and optional file-specific fdinfo.

State and persistence: It stores the descriptor number in `PROC_I(inode)->fd`; actual file state remains in the target task's `files_struct`. Dentries are revalidated by checking whether the fd still exists and updating inode ownership/mode from the current file mode. Directory getattr reports the current count of open fds.

Dependencies and integration points: Integrates with `base.c` pid inode helpers, task files locking, fd tables, ptrace permissions, path/mount reporting, file locks, security task-to-inode labeling, and the common proc symlink operations.

Risks: Permission rules are security-sensitive: `/fdinfo` requires ptrace read access, while `/fd` has a same-thread-group exception for `/proc/self/fd` after setuid. Revalidation must avoid RCU lookup when it cannot safely ref target files. Iteration races with close/open and should remain robust. In this snapshot, duplicated loop text in `proc_readfd_common()` should be checked before compiling.

Test signals: Open/close descriptors while reading directories, readlink regular files/sockets/pipes/deleted files, close-on-exec flag reporting, fdinfo for epoll/eventfd/timerfd where `show_fdinfo` exists, permission checks across users and same thread group after setuid, directory size count, and task exit during lookup/read.
