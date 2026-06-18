# sources/distributed-fs/ceph-client/fs/minix/bitmap.c

## Purpose

`sources/distributed-fs/ceph-client/fs/minix/bitmap.c` manages Minix block and inode allocation bitmaps and raw on-disk inode access for Minix v1/v2 layouts. It allocates/frees blocks and inodes, counts free resources, clears deleted inode records, and initializes new VFS inodes. The source was read as a complete 269-line file for this report.

## Important APIs, Types, and Functions

Important state is `bitmap_lock`, shared by inode and zone bitmap mutations. Public functions include `minix_free_block`, `minix_new_block`, `minix_count_free_blocks`, `minix_V1_raw_inode`, `minix_V2_raw_inode`, `minix_free_inode`, `minix_new_inode`, and `minix_count_free_inodes`. Internal helpers are `count_free` and `minix_clear_inode`.

## Control Flow

Block allocation scans zone bitmap buffers for the first zero bit, sets it under `bitmap_lock`, marks the bitmap buffer dirty, translates the bitmap bit to an on-disk data zone, and validates the range. Freeing a block validates the data-zone range, clears the corresponding bit, and marks the buffer dirty. Inode allocation obtains a fresh VFS inode, scans and sets an inode bitmap bit, validates the inode number, initializes owner/timestamps/private Minix fields, inserts into the inode hash, and marks it dirty. Inode freeing clears the on-disk mode/link count before clearing the bitmap bit.

## State and Persistence Behavior

Persistent state is the on-disk inode and zone bitmaps plus raw inode table blocks, updated through buffer heads and marked dirty for writeback. In-memory state includes the new VFS inode and Minix private inode data. Free counts are computed by scanning bitmap buffers rather than maintaining counters here.

## Dependencies and Integration Points

It depends on `minix.h` for superblock layout, bitmap endian helpers, inode-private data, and version constants; buffer-head IO through `sb_bread`, `mark_buffer_dirty`, and `brelse`; VFS inode allocation and ownership helpers; and Minix inode tree/truncate code through shared inode structures.

## Risks and Edge Cases

Range checks protect against freeing blocks outside the data zone and inode numbers outside the inode table. Bitmap bit indexes include reserved inode/zone offsets and are easy to miscompute. `count_free` deliberately treats bitmap words endian-insensitively for zero-bit counting. Allocation can find a bit that maps outside valid zones or inode range and returns corruption/errors. On-disk inode clearing must match v1 versus v2 inode formats.

## Test Signals

Create/delete files until ENOSPC, verify free block/inode counts, run fsck after allocation/free cycles, test v1 and v2 images, inject out-of-range inode/block numbers, run concurrent creates/unlinks to stress `bitmap_lock`, and verify dirty bitmap/inode-table buffers are written after sync.
