<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/init.c -->
# sources/distributed-fs/ceph-client/fs/init.c

## Purpose

`sources/distributed-fs/ceph-client/fs/init.c` provides early-init, kernel-internal wrappers that mimic selected filesystem syscalls without using userspace pointers or already-open file descriptors. It is intended for `init/` and related boot code that needs to mount roots, create device nodes, change directories, set permissions, and duplicate files before normal userspace execution.

## Important APIs, Types, and Functions

The exported init helpers are `init_pivot_root()`, `init_mount()`, `init_umount()`, `init_chdir()`, `init_chroot()`, `init_chown()`, `init_chmod()`, `init_eaccess()`, `init_stat()`, `init_mknod()`, `init_link()`, `init_symlink()`, `init_unlink()`, `init_mkdir()`, `init_rmdir()`, `init_utimes()`, and `init_dup()`.

They use VFS helpers such as `kern_path()`, `path_mount()`, `path_umount()`, `path_pivot_root()`, `path_permission()`, `set_fs_pwd()`, `set_fs_root()`, `chown_common()`, `chmod_common()`, `vfs_getattr()`, `vfs_utimes()`, `get_unused_fd_flags()`, and `fd_install()`. Filename-taking operations use `CLASS(filename_kernel, ...)` wrappers to build kernel filename objects for lower-level `filename_*` helpers declared in `fs/internal.h`.

## Control Flow

Path-based operations first resolve a kernel string with `kern_path()` and appropriate lookup flags. `init_pivot_root()` resolves both new root and put-old directories and calls `path_pivot_root()`. `init_mount()` resolves the target and calls `path_mount()`. `init_umount()` resolves a mountpoint, optionally following symlinks unless `UMOUNT_NOFOLLOW` is set, and calls `path_umount()`.

Directory-context helpers resolve a directory and check execute/chdir permission before updating `current->fs`. `init_chroot()` additionally checks `CAP_SYS_CHROOT` in the current user namespace and calls `security_path_chroot()` before `set_fs_root()`.

Metadata changes resolve the target, acquire write access when needed, and call common VFS helpers. Object-creation and link/unlink operations wrap kernel string names in filename objects and delegate to the same `filename_*` implementations used by syscall paths. `init_dup()` obtains an unused fd and installs a reference to an existing file.

## State and Persistence Behavior

The helpers mutate normal VFS state on behalf of early kernel code: mount namespace state, the current task's root and cwd, inode ownership/mode/timestamps, directory entries, special files, hardlinks, symlinks, and fd tables. Persistence depends entirely on the backing filesystem and mount. The wrappers themselves hold no persistent state.

Resource cleanup is path-based: most functions `path_put()` resolved paths before returning, while scoped `CLASS(filename_kernel, ...)` objects manage filename lifetimes automatically.

## Dependencies and Integration Points

The file integrates early boot code with the normal VFS implementation while avoiding userspace address handling. It depends on mount/namei/open/stat/xattr internals exposed through `fs/internal.h`, LSM hooks for chroot, namespace capability checks, and the current task's `fs_struct` and file descriptor table.

Because many helpers are `__init`, they are intended to be discarded after boot; callers should not rely on them after init memory is freed.

## Risks and Edge Cases

These wrappers intentionally bypass syscall user-copy plumbing, so they must pass kernel filename wrappers to helpers that expect `struct filename` and must not pass raw kernel pointers into user-pointer syscall entry points. Lookup flags are security-sensitive: `AT_SYMLINK_NOFOLLOW` and `UMOUNT_NOFOLLOW` must be preserved exactly.

`init_chroot()` must keep capability and LSM checks aligned with normal chroot semantics. `init_chown()` needs `mnt_want_write()`/`mnt_drop_write()` pairing. `init_dup()` returns `0` after installing the fd rather than the fd number, matching the local init syscall contract but differing from `dup(2)` semantics; callers must understand that interface.

## Test Signals

Boot tests should verify initramfs/rootfs scripts using these helpers can mount, pivot root, chdir/chroot, create nodes/directories/links, set ownership/mode/timestamps, and unmount. Negative tests include missing paths, non-directories for chdir/chroot/pivot, permission failures, no `CAP_SYS_CHROOT`, readonly mounts for chown/chmod-like mutations, no free fds for `init_dup()`, and symlink-follow flag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/init.c -->
