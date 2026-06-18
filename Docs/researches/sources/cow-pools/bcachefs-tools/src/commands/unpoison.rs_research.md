# File Research: sources/cow-pools/bcachefs-tools/src/commands/unpoison.rs

Implements `bcachefs unpoison`, a dangerous recovery command that clears poison flags on file extents through a manually encoded `_IOW(0xbc, 68, struct bch_ioctl_unpoison)` ioctl.

Behavior:
- Requires `--yes-i-understand`; otherwise prints a detailed warning and exits with status 1.
- Accepts file path, sector-aligned byte offset, and sector-aligned length.
- If length is zero, rounds the file size up to 512-byte sectors.
- Opens the file read/write and calls `libc::ioctl` with `BchIoctlUnpoison`.
- Reports the cleared range on success.

Important safety context:
- The file-level documentation and CLI help emphasize that unpoisoning can make corrupt data invisible once a valid checksum exists over corrupted bytes.
- The command recommends `bcachefs data-read --no-poison-check` before proceeding.

Potential concerns:
- Ioctl encoding is duplicated locally instead of using `wrappers::ioctl::bch_ioc_w`, though the formula matches.
- The command exits directly for missing confirmation rather than returning an error, which is consistent with command UX but less library-friendly.
