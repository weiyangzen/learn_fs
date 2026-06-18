# File Research: sources/block-storage/parted/libparted/fs/r/hfs/advfs_plus.c

HFS+ counterpart to `advfs.c`, adapted for HFS+ extent key formats, larger node sizes, 32-bit allocation block numbers, and wrapper-aware minimum sizing.

Key behavior:
- Compares HFS+ extent keys by file ID, fork type, and 32-bit start block.
- `hfsplus_btree_search()` reads the HFS+ extents B-tree header, allocates node-sized buffers, walks index nodes, and returns matching leaf data/reference.
- Loads HFS+ bad-block extents into a linked list.
- Queries whether an allocation block lies in a bad-block extent.
- `hfsplus_get_empty_end()` computes free tail boundary after bad blocks.
- `hfsplus_get_min_size()` adjusts minimum shrink size when the HFS+ volume is embedded in an HFS wrapper.
- `hfsplus_find_start_pack()` finds a block from which relocation should pack data forward.

Important dependencies:
- HFS+ file reads from `file_plus.c`.
- Classic HFS helper `hfs_get_empty_end()` for wrapper calculations.
- HFS/HFS+ structures in `hfs.h`.

Notable issue:
- In `hfsplus_btree_search()`, the path after allocating `node` and failing the first `hfsplus_file_read()` returns without freeing `node`.
