# File Research: sources/cow-pools/bcachefs-tools/include/linux/blkdev.h

Purpose: userspace block-device shim exposing common Linux block-device and filesystem helper APIs.

Key contents:
- Defines file size, bio vector limits, major/minor device helpers, sector constants, page-sector helpers, and discard/nonrot stubs.
- Defines minimal `struct file`, `struct super_block`, `struct dir_context`, and `struct file_operations`.
- Declares block I/O submission, discard, zeroout, block-device open/lookup, capacity, logical block size, status conversion, and init helpers.
- Provides stubs for plugs, inode eviction, filesystem sync, char device registration, invalidate bdev, and `capable()`.
- Implements `file_inode()`, `file_bdev()`, `bdevname()`, `op_is_write()`, `bio_data_dir()`, `dir_emit()`, and `dir_emit_dots()`.

Important interactions:
- Provides much of the block/VFS compatibility base for bcachefs-tools.
- Some kernel security/scheduling concepts are deliberately simplified, e.g. `capable(cap)` always returns true in this shim.
