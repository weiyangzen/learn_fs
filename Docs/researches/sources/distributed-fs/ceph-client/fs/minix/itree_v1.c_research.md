<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/itree_v1.c -->
# sources/distributed-fs/ceph-client/fs/minix/itree_v1.c

## Purpose
`itree_v1.c` specializes the generic Minix indirect-tree implementation for original Minix V1 filesystems. V1 uses 16-bit block pointers, seven direct zones, one single-indirect slot, and one double-indirect slot.

## Important APIs, Types, and Functions
The file defines `DEPTH = 3`, `DIRECT = 7`, and `typedef u16 block_t`. `i_data()` maps the generic tree code onto `minix_i(inode)->u.i1_data`. `block_to_path()` converts a logical file block into offsets for direct, single-indirect, or double-indirect lookup. Public wrappers `V1_minix_get_block()`, `V1_minix_truncate()`, and `V1_minix_blocks()` expose the generic `get_block()`, `truncate()`, and `nblocks()` to the rest of Minix.

## Control Flow
For logical blocks 0 through 6, `block_to_path()` returns a one-element direct offset. Blocks 7 through 518 use inode slot 7 and an offset in the 512-entry indirect block. Larger valid blocks use inode slot 8, a first-level offset `block >> 9`, and a second-level offset `block & 511`. Negative blocks and blocks whose byte offset exceeds `s_maxbytes` return depth 0, causing the generic mapper to fail without mapping.

## State and Persistence Behavior
All block numbers are kept in host order and returned unchanged by `block_to_cpu()` and `cpu_to_block()`. Persistent pointers live in the V1 raw inode's 16-bit zone fields and in 16-bit indirect blocks. The included common code handles dirtying inode/metadata buffers and block freeing.

## Dependencies and Integration Points
This wrapper is built by textual inclusion of `itree_common.c`, so the macros and helpers it defines are compile-time parameters to the common implementation. It is called by `minix_get_block()`, `minix_truncate()`, and `minix_getattr()` when `INODE_VERSION(inode) == MINIX_V1`.

## Risks
The fixed `512` indirect fanout is tied to 1 KiB `BLOCK_SIZE` and 16-bit pointers; V1 mount validation must keep `s_maxbytes` within the representable mapping limit. Overflow or incorrect bounds here would map logical blocks to the wrong indirect slot. Because V1 block numbers are 16-bit, large devices/images cannot be represented safely.

## Test Signals
Use V1 images to test writes at block 0, block 6/7, block 518/519, maximum-size rejection, double-indirect truncation, sparse holes, and `stat->blocks` accounting through `V1_minix_blocks()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/itree_v1.c -->
