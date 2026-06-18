# File Research: sources/block-storage/util-linux/libmount/src/hook_subdir.c

This hook implements `X-mount.subdir=`, allowing callers to mount only a subdirectory from a filesystem source. It adapts to classic mount, older fd-based mount APIs, and newer detached-tree subdirectory support.

Key behavior:

- `is_subdir_required()` accepts `X-mount.subdir` only for normal mount operations, rejecting bind, move, remount, and propagation-only cases.
- The hook stores the requested subdir and registers `hook_mount_pre()`.
- On Linux >= 6.15 with mount fd support and no helper, `hook_mount_pre()` passes the subdir to `hook_mount.c` via `api->subdir`; `hook_mount.c` opens the detached subdirectory directly.
- On older paths, it creates `/run/mount` temporary target state, unshares the mount namespace, makes the runtime directory or temp target private, changes the context target to `MNT_PATH_TMPTGT`, and registers `hook_mount_post()`.
- `hook_mount_post()` binds or moves the requested subdirectory from the temporary root to the original target, then unmounts the temporary root and switches back to the original namespace.

Dependencies and interactions:

- Requires namespace support for fallback paths.
- Coordinates with `hook_mount.c` through `libmnt_sysapi` when mount fd support is available.
- Uses target mutation on `cxt->fs` and global hookset data to preserve the original target.

Risk notes:

- Fallback paths depend on mount namespace manipulation and can fail if unshare/setns/mount-private operations are not permitted.
- Cleanup is essential: `free_hookset_data()` calls `tmptgt_cleanup()` if the namespace was created.
- A comment typo says "ateched"; behavior is still clear.
