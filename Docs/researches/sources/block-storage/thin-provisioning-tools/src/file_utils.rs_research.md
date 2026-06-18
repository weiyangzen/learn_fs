# File Research: sources/block-storage/thin-provisioning-tools/src/file_utils.rs

This file provides filesystem and block-device utility functions.

Important behavior:
- Uses `libc::stat64` to classify regular files and block devices.
- `is_file_or_blk()` returns true for regular files or block devices.
- `is_file()` checks only regular files.
- `device_size()` issues `BLKGETSIZE64` through the crate ioctl macros.
- `file_size()` returns regular-file byte size or block-device capacity.
- `create_sized_file()` creates/truncates a file and sizes it by seeking to `nr_bytes - 1` and writing one zero byte.

Integration points:
- Used by IO engines and packer code to compute block counts.
- Depends on `ioctl.rs` request code generation.

Risks and notes:
- `create_sized_file()` creates sparse files for large sizes.
- `file_size()` rejects paths that are neither regular files nor block devices.
