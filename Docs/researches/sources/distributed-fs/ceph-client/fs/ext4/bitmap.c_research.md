# sources/distributed-fs/ceph-client/fs/ext4/bitmap.c

## Purpose

`fs/ext4/bitmap.c` provides small helpers for counting free bits and verifying/updating inode and block bitmap checksums. These functions are used by allocation, inode allocation, group descriptor maintenance, and mount/debug accounting.

## Important APIs, types, and functions

- `ext4_count_free()` returns free bits in a bitmap buffer as total bits minus `memweight()`.
- `ext4_inode_bitmap_csum_verify()` and `ext4_inode_bitmap_csum_set()` verify or store inode bitmap checksums in group descriptor low/high fields.
- `ext4_block_bitmap_csum_verify()` and `ext4_block_bitmap_csum_set()` do the same for block bitmap checksums.

## Control flow

Checksum helpers no-op successfully when metadata checksums are not enabled. Otherwise they compute the checksum over the bitmap's active byte range using `s_csum_seed`, compare it with low 16-bit descriptor fields and optional high 16-bit fields when the descriptor size includes them, or write those fields during update.

## State and persistence behavior

The bitmap bytes are persistent metadata blocks. The checksum fields are persistent group descriptor fields. In-memory state is limited to `struct buffer_head` contents and ext4 superblock checksum seed/descriptor size. Setting a checksum mutates the group descriptor in memory; callers are responsible for journaling/dirtying descriptor metadata.

## Dependencies and integration points

The file depends on ext4 feature checks, group descriptor layout, `EXT4_INODES_PER_GROUP()`, `EXT4_CLUSTERS_PER_GROUP()`, `ext4_chksum()`, and `memweight()`. `balloc.c` uses block bitmap verification before trusting allocation maps; inode allocation code uses the inode bitmap counterparts.

## Risks and edge cases

The checksum byte length must match only valid bitmap bits, not necessarily the full block. Descriptor-size checks determine whether high checksum fields are meaningful; older descriptors compare only 16 bits. Bigalloc affects block bitmap length through clusters per group. Callers must pair checksum updates with descriptor journaling.

## Test signals

Verify checksum pass/fail with metadata_csum enabled and disabled, descriptor sizes with and without high fields, corrupted bitmap bytes, corrupted descriptor checksum fields, bigalloc cluster counts, and free-bit counts for all-zero, all-one, and mixed bitmaps.
