# File Research: sources/cow-pools/bcachefs-tools/include/linux/blk_types.h

Purpose: defines block-layer data structures, request operations, request flags, bio structure, and status values for tools builds.

Key contents:
- Defines block open mode flags.
- Provides lightweight `struct inode`, `request_queue`, `gendisk`, `hd_struct`, and `block_device` shims.
- Defines `blk_status_t` values and `BIO_INLINE_VECS`.
- Defines `struct bio` layout including bdev, status, operation flags, iterator, refcounts, callbacks, vector table, and pool.
- Defines bio flag bits and bvec pool indexing.
- Defines request operation enum and request flag bits/macros.
- Provides `bio_op()` and `bio_set_op_attrs()`.
- Defines common read/write operation aliases.

Important interactions:
- Foundation for `bio.h` and `blkdev.h`.
- Used by bcachefs I/O code that expects Linux block-layer types while running in userspace tools context.
