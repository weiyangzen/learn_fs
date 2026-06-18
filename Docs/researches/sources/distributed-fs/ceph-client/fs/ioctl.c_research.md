<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/ioctl.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ioctl.c` implements the generic VFS `ioctl(2)` syscall dispatcher and common file ioctls that are shared across filesystems. It handles close-on-exec toggles, nonblocking and async flags, block mapping, fiemap, legacy preallocation ioctls, freeze/thaw, clone/dedupe, size queries, file attribute ioctls, filesystem UUID/sysfs path reporting, and compat ioctl translation.

## Important APIs, Types, and Functions

The syscall entry points are `SYSCALL_DEFINE3(ioctl)` and, under `CONFIG_COMPAT`, `COMPAT_SYSCALL_DEFINE3(ioctl)`. The generic fallback to filesystem-specific handlers is `vfs_ioctl()`. The core dispatcher is `do_vfs_ioctl()`.

Shared helper APIs include exported `fiemap_fill_next_extent()`, exported `fiemap_prep()`, and exported `compat_ptr_ioctl()`. Important local helpers are `ioctl_fibmap()`, `ioctl_fiemap()`, `ioctl_file_clone()`, `ioctl_file_clone_range()`, `ioctl_preallocate()`, `file_ioctl()`, `ioctl_fionbio()`, `ioctl_fioasync()`, `ioctl_fsfreeze()`, `ioctl_fsthaw()`, `ioctl_file_dedupe_range()`, `ioctl_getfsuuid()`, and `ioctl_get_fs_sysfs_path()`.

## Control Flow

Native `ioctl(2)` obtains the fd through the scoped fd helper, rejects bad fds, runs `security_file_ioctl()`, calls `do_vfs_ioctl()`, and if the command is not one of the generic VFS commands, falls back to `vfs_ioctl()` which calls `file_operations->unlocked_ioctl()` and translates `-ENOIOCTLCMD` to `-ENOTTY`.

`do_vfs_ioctl()` switches on command numbers. Simple commands update close-on-exec or file flags. `FIOQSIZE`, `FIONREAD`, and `FIGETBSZ` return sizes for supported object types. Freeze/thaw check `CAP_SYS_ADMIN` in the superblock user namespace and delegate to superblock freeze/thaw operations. Clone and dedupe copy user argument structures and call VFS range helpers. Attribute ioctls delegate to fileattr helpers. Regular-file-only legacy preallocation commands flow through `file_ioctl()`.

FIEMAP copies the user header, bounds extent count against `FIEMAP_MAX_EXTENTS`, initializes `struct fiemap_extent_info`, calls the inode's `->fiemap`, and copies back flags and mapped extent count. Filesystem `->fiemap` implementations call `fiemap_prep()` and `fiemap_fill_next_extent()` to validate flags, optionally sync dirty pages, and copy extent records to the user array.

Compat ioctl handling runs `security_file_ioctl_compat()`, special-cases integer `FICLONE`, x86_64 legacy preallocation structure alignment, and 32-bit flag command numbers, then reuses `do_vfs_ioctl()` with `compat_ptr()` for compatible pointer commands or falls back to filesystem `compat_ioctl`.

## State and Persistence Behavior

Most operations mutate file descriptor or filesystem state indirectly. `FIOCLEX`/`FIONCLEX` update fd table close-on-exec state. `FIONBIO` changes `file->f_flags` under `f_lock`; `FIOASYNC` delegates to `fasync()` and may alter async notification state. Preallocation, punch-hole, zero-range, clone, and dedupe can change file extents through VFS filesystem methods. Freeze/thaw changes superblock freeze state. Fileattr ioctls can update inode flags or project IDs through helpers in other files.

FIEMAP and FIBMAP report mapping state without changing layout, except `FIEMAP_FLAG_SYNC` can write and wait dirty pages. UUID and sysfs-path ioctls expose superblock fields only when populated.

## Dependencies and Integration Points

The file integrates syscall/fd handling, LSM ioctl hooks, file operations, inode operations, VFS clone/dedupe/fallocate, superblock freeze/thaw, buffer-head `bmap`, writeback sync, fscrypt/fileattr helpers, user-copy helpers, compat ABI, and architecture ioctl definitions.

Filesystem integration occurs through `file_operations->unlocked_ioctl`, `file_operations->compat_ioctl`, `inode_operations->fiemap`, superblock operations, and the common fileattr helpers included from `<linux/fileattr.h>`.

## Risks and Edge Cases

User ABI compatibility is the primary risk. Commands that pass integers must not be fed through `compat_ptr()`, and x86_64 legacy preallocation structures require special alignment handling. New generic ioctls must preserve compat semantics and go through LSM review because security modules may care about command behavior.

FIEMAP must avoid extent-count overflow on 32-bit systems and must propagate unsupported flags back through `fi_flags` with `-EBADR`. FIBMAP is privileged and warns if a block number would truncate into an `int`. Freeze/thaw permission checks depend on the superblock user namespace.

Size-reporting commands deliberately reject anonymous regular files in some cases. `ioctl_file_dedupe_range()` limits the copied request to one page. Clone must report an error if a length-limited clone completes only partially.

## Test Signals

Tests should cover native and compat ioctls for `FIONBIO`, `FIOASYNC`, `FIONREAD`, `FIOQSIZE`, `FIGETBSZ`, `FIBMAP` permission failure and success, FIEMAP count-only and bounded arrays, unsupported FIEMAP flags, freeze/thaw permission and unsupported filesystems, clone and clone-range partial behavior, dedupe range copyback, legacy preallocation whence handling, x86_64 compat preallocation structures, fileattr get/set, UUID/sysfs path absent and present cases, and fallback to filesystem-specific ioctl returning `-ENOTTY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ioctl.c -->
