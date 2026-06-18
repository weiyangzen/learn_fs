# File Research: sources/block-storage/util-linux/sys-utils/blkdiscard.c

## Scope

Implements the `blkdiscard` command, which discards, securely discards, or zero-fills ranges of a block device using Linux block ioctls.

## Public And Internal APIs Covered

- Main command-line entry point.
- Internal actions: discard, secure discard, zeroout.
- Optional signature probing via libblkid.
- Progress/stat reporting through `print_stats()`.

## Control Flow And Behavior

- Parses offset, length, step, force, quiet, secure, zeroout, and verbose options.
- Opens the device read/write, using `O_EXCL` unless `--force` is supplied.
- Verifies the target is a block device.
- Reads device size with `BLKGETSIZE64` and logical sector size with `BLKSSZGET`.
- Validates offset and length alignment to sector size and clamps length to device end.
- With libblkid and without force, probes existing filesystem/partition signatures and warns; on interactive stdin, an existing signature requires `--force`.
- Iterates over the requested range in optional `--step` chunks and calls one of:
  - `BLKDISCARD`
  - `BLKSECDISCARD`
  - `BLKZEROOUT`
- Verbose stepped mode reports progress at most once per second.

## Dependencies

- Linux block ioctls from `<linux/fs.h>`.
- Optional libblkid probing.
- util-linux helpers for size parsing, monotonic time, block device helpers, i18n, and exit codes.

## Risks And Invariants

- Offset and length must be sector-aligned.
- Range arithmetic guards overflow and clamps to block-device size.
- `--force` bypasses exclusive open and signature protection.
- Unsupported ioctls return `EXIT_NOTSUPP` when `errno == EOPNOTSUPP`.
