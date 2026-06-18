# File Research: sources/block-storage/thin-provisioning-tools/src/ioctl/tests.rs

This file validates ioctl request-code macro output against known block-device ioctl constants.

Test coverage:
- `request_code_none!(0x12, 119)` equals expected `BLKDISCARD`.
- `request_code_read!(0x12, 114, usize)` equals expected `BLKGETSIZE64`.
- `request_code_write!(0x12, 113, usize)` equals expected `BLKBSZSET`.

The expected constants vary by:
- MIPS/PowerPC/SPARC style direction encoding versus common architectures.
- 32-bit versus 64-bit pointer width.

Integration points:
- Protects `ioctl.rs` ABI compatibility for `file_utils` block-device operations.
