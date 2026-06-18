# sources/distributed-fs/ceph-client/fs/qnx4/bitmap.c

## Purpose
`bitmap.c` counts free blocks in the QNX4 allocation bitmap for `statfs`.

## Important APIs, types, and functions
The file provides `qnx4_count_free_blocks`, using `qnx4_sb(sb)->BitMap`, `sb_bread`, and `memweight`.

## Control flow
It reads bitmap blocks beginning at the bitmap inode's first extent, counts zero bits as free blocks across `di_size` bytes, and stops on I/O failure.

## State and persistence
It only reads on-disk bitmap data through buffer heads. No in-memory bitmap cache is maintained beyond the copied bitmap inode in superblock info.

## Dependencies and integration points
It depends on QNX4 superblock state, block-size constants, buffer heads, little-endian fields, and `qnx4_statfs`.

## Risks and test signals
Risks include trusting bitmap inode size/extent fields, partial counts after I/O errors, and mismatch between bits and real block count. Test signals include `statfs` on valid images, corrupt bitmap extent, short bitmap size, and I/O-error injection.
