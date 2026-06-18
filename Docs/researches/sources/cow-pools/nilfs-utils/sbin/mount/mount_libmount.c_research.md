# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_libmount.c

## Scope

Libmount-based implementation of `mount.nilfs2`, replacing legacy table/option code with `struct libmnt_context` while preserving NILFS cleaner daemon coordination and single read-write mount policy.

## APIs And Behavior

- Initializes a libmount context, sets filesystem type to `nilfs2`, disables helper recursion, parses mount options, and splits NILFS attributes from kernel/libmount options.
- Supports fake, verbose, no-mtab, type, options, read-only/read-write, and version options.
- `nilfs_prepare_mount()` calls `mnt_context_prepare_mount()`, retrieves mount flags and mtab, checks writable-device accessibility, detects whether the target is already mounted, and finds any existing read-write NILFS mount for the same source.
- Enforces no overlapping read-write mounts. For rw-to-ro or rw-to-rw remounts, it parses old stored attributes, verifies the mountpoint, and shuts down the old cleaner daemon if recorded.
- `nilfs_do_mount_one()` calls `mnt_context_do_mount()` and reports syscall/library errors; if remount fails after stopping cleanerd, it tries to restart cleanerd and finalize mount attributes.
- `nilfs_mnt_context_complete_root()` copies mount root from an existing mtab entry for remount/fake cases to avoid incomplete utab attributes.
- `nilfs_update_mount_state()` launches cleanerd for read-write non-bind mounts unless `nogc`, updates stored attributes, and finalizes the mount.

## State And Dependencies

`struct nilfs_mount_info` carries libmount context, resolved mount flags, mount type, mounted state, and old/new NILFS attributes. Dependencies include libmount, `BLKROGET`, cleaner execution APIs, and `mount_attrs.c`.

## Risks And Invariants

The stored libmount attributes are the control channel for later umount/remount cleaner operations. `mnt_context_do_mount()` returns positive errno for syscall failures and negative library errors; callers normalize this for diagnostics. If cleanerd launch fails after a successful writable mount, the mount still succeeds but GC is not running.
