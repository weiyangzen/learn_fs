<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/itree_v2.c -->
# sources/distributed-fs/ceph-client/fs/minix/itree_v2.c

## Purpose
`itree_v2.c` specializes the generic Minix indirect-tree implementation for Minix V2 and V3 inode block mapping. V2/V3 use 32-bit block pointers, seven direct zones, and single, double, and triple indirect slots.

## Important APIs, Types, and Functions
The file defines `DIRECT = 7`, `DEPTH = 4`, and `typedef u32 block_t`. `DIRCOUNT` and `INDIRCOUNT(sb)` describe direct count and per-indirect-block fanout based on filesystem block size. `i_data()` maps the generic implementation onto `minix_i(inode)->u.i2_data`. `block_to_path()` produces up to four offsets. Public wrappers are `V2_minix_get_block()`, `V2_minix_truncate()`, and `V2_minix_blocks()`.

## Control Flow
`block_to_path()` rejects negative logical blocks and byte offsets beyond `s_maxbytes`. It returns a direct offset for the first seven blocks, slot 7 plus one indirect offset for the next `INDIRCOUNT(sb)` blocks, slot 8 plus two offsets for the double-indirect range, and slot 9 plus three offsets for the triple-indirect range. The included common code then uses those offsets for lookup, allocation, and truncation.

## State and Persistence Behavior
Block pointers are 32-bit host-order values in memory and on supported Minix images as used by this code. Indirect fanout scales with `sb->s_blocksize`, unlike V1's hard-coded 1 KiB geometry. Persistent metadata updates and frees are delegated to `itree_common.c`.

## Dependencies and Integration Points
This file is used for both `MINIX_V2` and `MINIX_V3` in `inode.c`. It relies on the V2 raw inode layout, V3 superblock block-size setup, the generic Minix allocator/free routines, and the VFS block mapping callbacks.

## Risks
The triple-indirect arithmetic uses products of `INDIRCOUNT(sb)` and logical block values; bounds must be constrained by `s_maxbytes` to prevent nonsensical paths. V3 block-size changes directly affect indirect fanout, so mount-time block-size setup must happen before inode block mapping. Tests should watch for off-by-one errors at direct/single/double/triple boundaries.

## Test Signals
Use V2/V3 images with different supported block sizes; write and read across single-, double-, and triple-indirect boundaries; truncate from triple-indirect back to smaller sizes; verify `V2_minix_blocks()` metadata accounting; and inject ENOSPC during each indirect allocation depth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/itree_v2.c -->
