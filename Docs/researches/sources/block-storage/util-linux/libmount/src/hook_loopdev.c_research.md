# File Research: sources/block-storage/util-linux/libmount/src/hook_loopdev.c

This hook implements automatic and explicit loop device setup for regular-file mounts and cleanup after mount failure or success. It also exposes the current non-hook umount loop deletion helper.

Key entry points:

- `hook_prepare_loopdev()` runs at `MNT_STAGE_PREP_SOURCE` and decides whether a loop device is needed.
- `setup_loopdev()` parses loop options, reuses or creates a loop device, updates `cxt->fs` source to `/dev/loopN`, and keeps a read-only FD open across mount.
- `hook_cleanup_loopdev()` runs after mount and either detaches the loop device on failure or closes the held FD on success.
- `mnt_context_delete_loopdev()` is called from umount code.

Important behavior:

- Loop setup is skipped for bind, move, propagation-only, non-mount actions, missing sources, and `X-mount.noloop`.
- Explicit userspace flags `loop`, `offset`, or `sizelimit` force loop handling.
- Automatic loop handling is enabled for regular files larger than 1 KiB when the filesystem type is known or can be guessed, except for EROFS and unknown non-blkid filesystems.
- Existing overlapping loop devices are detected. Full matching devices can be reused; partial overlap fails with `MNT_ERR_LOOPOVERLAP`.
- Existing reused loop devices are checked for autoclear races, read-only conflicts, unsupported legacy encryption, and conflict with explicit `loop=<device>`.
- New loop devices get `LO_FLAGS_AUTOCLEAR` on Linux >= 2.6.37, and `LO_FLAGS_READ_ONLY` if the mount is read-only.
- The hook removes unnecessary `loop=` from utab when autoclear or reuse makes persistence unnecessary and appends `MS_RDONLY` if the loop device is read-only.

Dependencies and interactions:

- Uses `loopdev.c`/`loopdev.h`, libblkid filesystem recognition, option lists, mountinfo lookups, path cache resolution, and Linux version checks.
- Updates `cxt->fs->source`, so later mount hooks mount the loop block device rather than the original regular file.

Risk notes:

- The race between finding a loop device and setup is handled by retrying stolen devices and revalidating reused loop state.
- On setup error after partial creation, cleanup calls `delete_loopdev()`, which uses the current filesystem source.
- Automatic loop avoidance for EROFS relies on kernel support for file-backed EROFS; older kernels may still need loop devices.
