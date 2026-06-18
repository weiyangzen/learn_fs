# File Research: sources/block-storage/util-linux/libmount/src/hook_mount.c

This conditional hook implements mounting through the newer Linux mount fd API: `fsopen()`, `fsconfig()`, `fsmount()`, `open_tree()`, `mount_setattr()`, and `move_mount()`.

Supported operation model:

- New mount: `fsopen` during prepare or mount stage, `fsconfig(source/options)`, `FSCONFIG_CMD_CREATE`, `fsmount`, optional detached subdir open, VFS attributes, then `move_mount`.
- Remount: `open_tree`, `fspick`, `fsconfig` reconfiguration, and `mount_setattr`.
- Propagation-only: `open_tree` and post-stage `mount_setattr` propagation.
- Move/bind: `open_tree`, optional VFS attributes, and post-stage `move_mount`.

Key components:

- `struct libmnt_sysapi` hookset data stores `fd_fs`, `fd_tree`, `is_new_fs`, and optional `subdir`.
- `configure_superblock()` sends superblock and filesystem-specific options through `fsconfig()`, ignoring VFS/userspace/external options.
- `hook_create_mount()` creates a new detached mount and records mount ID through `statx(STATX_MNT_ID)` when available.
- `hook_reconfigure_mount()` uses `fspick()` then `FSCONFIG_CMD_RECONFIGURE`.
- `hook_set_vfsflags()` translates option-list mount attributes into `mount_setattr()` normal and recursive calls.
- `hook_set_propagation()` applies propagation options through post-attach `mount_setattr()`.
- `hook_attach_target()` moves the detached tree to the target, with optional `MOVE_MOUNT_BENEATH`, and marks attached/moved status.
- `hook_prepare()` decides whether to use the new API or recover to legacy.

Important behavior:

- `LIBMOUNT_FORCE_MOUNT2=always|never` can force or disable the classic mount path.
- The new API is skipped for btrfs mounts with SELinux options because of noted fsconfig limitations.
- Helpers use the new API only for propagation setting; helper execution itself remains external.
- ENOSYS or unsupported new API paths return positive `1` from prepare after clearing syscall status, allowing `hook_mount_legacy.c` to continue.
- Kernel versions before 5.14 are rejected for remount `mount_setattr()` use.
- For Linux >= 6.15, `hook_subdir.c` can set `api->subdir`, and this file opens the subdirectory from a detached tree before final attachment.

Dependencies and interactions:

- Active under `USE_LIBMOUNT_MOUNTFD_SUPPORT`.
- Coordinates with `hook_subdir.c`, `hook_idmap.c`, option-list attribute extraction, syscall-message collection, Linux version checks, and context syscall status.

Risk notes:

- The file intentionally has several recovery paths into legacy mount behavior; callers must not treat positive prepare return as fatal.
- File descriptor ownership is central. `close_sysapi_fds()` is used on failure/deinit; other hooks may reuse `fd_tree`.
- Some classic `MS_*` flags are interpreted as superblock options for backward compatibility, so option map correctness is critical.
