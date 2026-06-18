<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/internal.h -->
# sources/distributed-fs/ceph-client/fs/internal.h

## Purpose

`sources/distributed-fs/ceph-client/fs/internal.h` is the private cross-file header for VFS implementation code under `fs/`. It declares internal helpers that are shared among VFS source files but are not public kernel APIs, and it defines small internal structures and inline helpers for mount, file, inode, namespace, xattr, attr, and path handling.

## Important APIs, Types, and Functions

The header declares initialization hooks such as `bdev_cache_init()`, `chrdev_init()`, `filename_init()`, and `mnt_init()`. Namei and namespace internals include `filename_lookup()`, `filename_mkdirat()`, `filename_mknodat()`, `filename_symlinkat()`, `filename_linkat()`, `filename_unlinkat()`, `filename_rmdir()`, `filename_renameat2()`, `path_mount()`, `path_umount()`, `path_pivot_root()`, `lookup_mnt()`, `finish_automount()`, `may_mount()`, and remount helpers.

File and open internals include `alloc_empty_file*()`, `do_file_open()`, `do_file_open_root()`, `build_open_how()`, `build_open_flags()`, `file_close_fd_locked()`, `do_ftruncate()`, `chmod_common()`, `chown_common()`, `fput_close*()`, and inline helpers `file_put_write_access()` and `put_file_access()`.

Inode, dcache, pipe, namespace, stat, splice, xattr, ACL, attr, and anon-inode declarations cover `prune_icache_sb()`, `dentry_needs_remove_privs()`, `in_group_or_capable()`, `prune_dcache_sb()`, `shrink_dcache_for_umount()`, `pipefifo_fops`, `open_namespace_file()`, `do_statx*()`, `splice_file_to_pipe()`, `kernel_xattr_ctx`, xattr copy/set/get helpers, ACL helpers, `alloc_mnt_idmap()`, stashed dentry helpers, `path_mounted()`, file-owner release, statmount idmap reporting, and namespace root getters.

## Control Flow

This header has no runtime control flow by itself. It enables control flow between VFS implementation files by exposing internal functions that would otherwise require public declarations. Several inline helpers do encode behavior: `file_put_write_access()` releases inode and mount write references, including backing-file user mount references; `put_file_access()` releases read or writer accounting based on file mode; `sb_start_ro_state_change()` and `sb_end_ro_state_change()` provide memory-barrier ordering for superblock read-only transitions; `path_mounted()` checks whether a path is a mount root.

## State and Persistence Behavior

The header owns no storage. It describes and coordinates state owned by other VFS components: mount write counts, superblock readonly-transition flags, inode cache and dcache shrink state, file descriptor tables, xattr copy buffers, idmapped mount references, stashed dentries, and namespace roots.

The readonly-transition helpers are stateful in callers because they write `sb->s_readonly_remount` with memory barriers so mount readers observe either a pending transition or completed flag changes consistently.

## Dependencies and Integration Points

`internal.h` is a dense integration point across VFS compilation units. It depends on core kernel types such as `struct super_block`, `struct file`, `struct path`, `struct mount`, `struct fs_context`, `struct inode`, `struct dentry`, `struct seq_file`, `struct iov_iter`, `struct mnt_idmap`, and `struct ns_common`.

It is used by files such as `fs/init.c`, `fs/inode.c`, `fs/ioctl.c`, open/namei/namespace/stat/xattr/attr implementations, and filesystem helpers that need private VFS contracts. The block-device init declaration is compiled away to an inline no-op when `CONFIG_BLOCK` is disabled.

## Risks and Edge Cases

Because this is an internal header, changes have broad blast radius but limited external ABI review. Function signatures must stay synchronized with implementation files. Inline reference-release helpers are particularly sensitive: mismatched `put_write_access()` and mount write accounting can leak or prematurely drop write permissions, especially for backing files.

The readonly-transition barriers are subtle; weakening them can let `mnt_is_readonly()` observers see inconsistent superblock flag state. Xattr and ACL helpers carry user-pointer and kernel-buffer contracts that must remain clear to avoid user-copy bugs.

## Test Signals

Test signals are indirect. Full VFS build coverage across `CONFIG_BLOCK`, `CONFIG_FS_POSIX_ACL`, namespace, xattr, statmount, and backing-file configurations catches missing declarations. Runtime coverage should exercise mount/remount readonly transitions, file open/close accounting, early init wrappers, xattr get/set paths, ACL enabled and disabled builds, namespace file opens, dcache/inode shrinkers, and backing-file write-access release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/internal.h -->
