# File Research: sources/block-storage/thin-provisioning-tools/src/io_engine/ramdisk.rs

This test-only file implements a mock direct-I/O ramdisk with error injection.

Important behavior:
- Stores data in an aligned shared `Buffer`.
- Tracks invalid pages in a shared `RoaringBitmap`.
- `invalidate(bytes)` marks all pages overlapping a byte range as faulty.
- `VectoredIo` read/write methods fail the entire vectored operation if any covered page is invalid.
- `FileExt` read/write methods fail when their range overlaps invalid pages.

Integration points:
- Used heavily by copier and IO utility tests.
- Simulates direct-I/O page-alignment and bad-sector behavior.

Risks and notes:
- Internally indexes sizes as `u32`, so it is for small test devices.
- Clones share both data and invalid-page state.
