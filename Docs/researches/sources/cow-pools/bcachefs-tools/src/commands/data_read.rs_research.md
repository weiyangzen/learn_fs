# File Research: sources/cow-pools/bcachefs-tools/src/commands/data_read.rs

This file implements `data-read`, a low-level read command with extended bcachefs error reporting.

Behavior:
- Opens the target file with `O_DIRECT`.
- Requires offset and length to be 512-byte sector aligned.
- Allocates a 512-byte-aligned buffer manually.
- Calls the raw pread ioctl `_IOWR(0xbc, 67, struct bch_ioctl_pread_raw)`.
- Supports `--no-poison-check` to read data from poisoned extents.
- Reports error bitmask categories:
  - checksum
  - IO
  - decompression
  - erasure-code reconstruction
- Prints kernel-provided error text when available.
- Writes raw output to a file if `--output` is set, otherwise prints a hex dump.

Important note:
- If the ioctl returns an error, the command still dumps whatever data was returned, then exits with code 1.
