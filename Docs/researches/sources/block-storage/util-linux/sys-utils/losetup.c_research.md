# File Research: sources/block-storage/util-linux/sys-utils/losetup.c

`losetup.c` implements `losetup(8)`, the CLI for creating, listing, modifying, detaching, and removing Linux loop devices.

Key behavior:
- Defines action modes for create, detach, detach-all, list, show-one, find-free, set-capacity, set-direct-io, set-blocksize, and remove.
- Uses `struct loopdev_cxt` from util-linux loopdev helpers for all kernel loop interactions.
- Provides legacy text output through `printf_loopdev()` and structured table/JSON/raw output through `libsmartcols`.
- Supports listing all loop devices or only those associated with a backing file and offset.
- Implements `--nooverlap` checks to prevent conflicting loop mappings and to reuse exact matching non-encrypted mappings where safe.
- Handles setup flags for read-only, partition scan, direct I/O, offset, size limit, logical sector size, and reference string.
- Retries loop setup on transient `EBUSY`/`EAGAIN` for automatically selected loop devices.
- Warns for backing files smaller than 512 bytes or not aligned to 512-byte sector boundaries.

Important dependencies:
- `loopdev.h` owns loop ioctl details, backing-file metadata, iteration, overlap detection, and status queries.
- `libsmartcols` owns column definitions, JSON typing, raw output, and no-heading output.
- util-linux parsing helpers enforce numeric sizes and exclusive option groups.

Risk notes:
- The command has many mutually exclusive modes; correctness depends on the `ul_excl_t` tables and later contextual validation.
- `--direct-io` and `--sector-size` can modify existing loop devices when no create action is selected.
- Non-root listing can lack backing inode/device data, so output falls back to partial information.
- Reuse under `--nooverlap` deliberately rejects read-only-to-read-write transitions and encrypted overlaps.
