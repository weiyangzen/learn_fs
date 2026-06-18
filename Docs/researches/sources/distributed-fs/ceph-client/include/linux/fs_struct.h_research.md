# sources/distributed-fs/ceph-client/include/linux/fs_struct.h

Purpose: defines `struct fs_struct`, the per-task/shared filesystem view containing root, current working directory, umask, and exec state. It is the kernel-side state behind `chroot`, `chdir`, `umask`, clone sharing of filesystem context, and task exit cleanup.

Important APIs and types: `struct fs_struct` stores a user count, seqlock, umask, `in_exec`, and `struct path` values for root and pwd. Public functions include `exit_fs()`, `set_fs_root()`, `set_fs_pwd()`, `copy_fs_struct()`, `free_fs_struct()`, `unshare_fs_struct()`, and `current_chrooted()`. `get_fs_root()` and `get_fs_pwd()` take the seqlock in exclusive-read style, copy the path, and take a path reference. `current_umask()` reads `current->fs->umask`.

Control flow: fork/clone either shares or copies `fs_struct`; path-changing syscalls update root/pwd with seqlock protection; users retrieve stable path references through the inline getters; `exit_fs()` drops the task's reference on exit.

State and persistence: this is process runtime state, not filesystem persistence. It controls pathname resolution and file creation permissions, making it security-sensitive despite being transient.

Dependencies and integration points: depends on scheduler task state, path references, spin/seqlock infrastructure, VFS path lookup, namespace/chroot handling, and exec code that tracks `in_exec`.

Risks and test signals: risks include path reference leaks, use-after-free if copied without `path_get`, races during chroot/chdir, and incorrect sharing after `unshare(CLONE_FS)`. Tests should cover multithreaded chdir/chroot, clone with and without `CLONE_FS`, umask inheritance, exec-time behavior, and namespace teardown.
