# sources/distributed-fs/ceph-client/fs/fsopen.c

## Purpose
`fsopen.c` implements the fd-based mount API entry points `fsopen(2)`, `fspick(2)`, and `fsconfig(2)`. It creates filesystem contexts, exposes their logs through anonymous fds, applies parameters, and transitions contexts through create/reconfigure phases.

## Important APIs, Types, and Functions
- `fscontext_fops` exposes `.read` for context log messages and `.release` for `put_fs_context()`.
- `fsopen()` creates a mount `fs_context` by filesystem type.
- `fspick()` creates a reconfiguration `fs_context` for an existing mount root.
- `fsconfig()` submits flags, strings, binary blobs, paths, fds, and create/reconfigure commands.
- `vfs_cmd_create()`, `vfs_cmd_reconfigure()`, and `vfs_fsconfig_locked()` enforce the context state machine.

## Control Flow
`fsopen()` validates mount permission and flags, resolves the filesystem type, allocates a mount context, puts it in `FS_CONTEXT_CREATE_PARAMS`, attaches a log, and returns an anonymous fd. `fspick()` performs a pathname lookup, requires the target dentry to be the mount root, builds a reconfigure context, and returns an fd. `fsconfig()` validates command-specific user arguments, copies the key/value into a `struct fs_parameter`, locks `fc->uapi_mutex`, and either parses the parameter or runs create/reconfigure. Create calls `vfs_get_tree()`, checks LSM mount permission, drops `s_umount`, and moves to `FS_CONTEXT_AWAITING_MOUNT`. Reconfigure checks `CAP_SYS_ADMIN` in the superblock user namespace, locks `s_umount`, calls `reconfigure_super()`, and cleans the context.

## State and Persistence
State is in `struct fs_context`: phase, log ring, root, fs type, uapi mutex, and parsed parameters. The anonymous fd owns a reference to the context. User-provided strings, blobs, filenames, and files are freed after parsing unless stolen by the filesystem or LSM.

## Dependencies and Integration Points
This code integrates with `fs_context` helpers, `anon_inode_getfd`, `vfs_get_tree`, `reconfigure_super`, LSM hooks, path lookup, mount capabilities, and the parameter parser in `fs_parser.c`. It is the main syscall bridge into filesystem-specific `init_fs_context` and `parse_param`.

## Risks
The main risks are state-machine bypass, user pointer copy limits, stolen-parameter ownership, and superblock lock handling. `fsconfig()` caps binary parameters at 1 MiB and strings/keys at 256 bytes, so compatibility depends on callers respecting those limits. Create paths must drop `s_umount` exactly once after `vfs_get_tree()` succeeds. Reconfiguration permission is checked in the target superblock user namespace, not only the caller namespace.

## Test Signals
Exercise fsopen/fspick/fsconfig success and failure phases, invalid command/value combinations, oversized strings/blobs, path-empty behavior, fd parameters, LSM denials, create-excl behavior, reconfigure permission failures, context log reads, and release cleanup after partial configuration.
