# sources/distributed-fs/ceph-client/fs/romfs/storage.c

## Purpose
`storage.c` provides ROMFS backing-store access helpers. It abstracts reads, bounded string length scans, and name comparisons over MTD-backed and block-backed ROMFS images while enforcing image-size limits.

## Important APIs, Types, And Functions
Public helpers are `romfs_dev_read()`, `romfs_dev_strnlen()`, and `romfs_dev_strcmp()`. MTD-specific implementations are `romfs_mtd_read()`, `romfs_mtd_strnlen()`, and `romfs_mtd_strcmp()`, built under `CONFIG_ROMFS_ON_MTD` and using `mtd_read()`. Block-specific implementations are `romfs_blk_read()`, `romfs_blk_strnlen()`, and `romfs_blk_strcmp()`, built under `CONFIG_ROMFS_ON_BLOCK` and using `sb_bread()`, `buffer_head`, `memcpy()`, `memchr()`, and `memcmp()`.

## Control Flow
All public helpers first check `romfs_maxsize(sb)` bounds. `romfs_dev_read()` rejects reads starting beyond the image or extending past the limit, then dispatches to MTD if `sb->s_mtd` is present, else block if `sb->s_bdev` is present. `romfs_dev_strnlen()` clamps `maxlen` to the image limit and dispatches similarly. `romfs_dev_strcmp()` rejects out-of-image positions, names longer than `ROMFS_MAXFN`, and comparisons without space for the trailing NUL.

MTD reads request exact byte counts and treat short reads as `-EIO`. MTD string operations scan up to 16 bytes at a time; compare reads up to 17 bytes to include the trailing NUL. Block reads split by `ROMBSIZE` block boundaries, reading each buffer head, copying or scanning the segment, and releasing the buffer. Block compare checks a terminator either inside the final block or at the first byte of the next block.

## State And Persistence
The file owns no mutable state. It reads from persistent ROMFS images through MTD or block devices and uses transient stack buffers or buffer heads. Superblock fields `s_mtd`, `s_bdev`, and `s_fs_info` determine the active backend and bounds.

## Dependencies And Integration Points
It depends on `internal.h`, `linux/mtd/super.h`, `linux/buffer_head.h`, ROMFS constants `ROMBSIZE`, `ROMBSBITS`, and `ROMFS_MAXFN`, plus mount code that initializes `s_mtd`, `s_bdev`, and max size. `super.c` uses these helpers to parse metadata, names, and file data from the image.

## Risks
Boundary checks are the primary correctness and security defense. Off-by-one errors around trailing NUL checks could accept prefix names or read past image end. MTD short reads and block read failures must become `-EIO`. Block compare uses `BUG_ON()` for an invariant that the terminator check at the next block only happens on a block boundary, so logic changes around segment sizing need care.

## Test Signals
Tests should cover reads spanning block boundaries, strings with terminator inside a block and at the next block, missing terminators, oversized names, image-end boundary reads, MTD short-read/error injection, block `sb_bread()` failure, and both backing-store configurations. Mount tests with malformed ROMFS metadata should confirm errors are returned rather than out-of-bounds access.
