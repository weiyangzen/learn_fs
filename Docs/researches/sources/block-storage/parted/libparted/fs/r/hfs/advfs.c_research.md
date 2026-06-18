# File Research: sources/block-storage/parted/libparted/fs/r/hfs/advfs.c

Advanced classic HFS helpers for extents B-tree lookup, bad-block tracking, and shrink boundary calculation.

Key behavior:
- Compares HFS extent keys by file ID, fork type, and start block without unsafe subtraction on 32-bit file IDs.
- `hfs_btree_search()` walks the extents B-tree from header/root through index nodes to a leaf record at or below the search key.
- Loads bad-block extents from the extents overflow file into a linked list.
- Frees and queries the bad-block extent list.
- `hfs_get_empty_end()` finds the first sector of the free tail region after considering the last bad block and allocation bitmap.
- `hfs_find_start_pack()` finds where relocation must begin to free a requested number of blocks at the end.

Important dependencies:
- HFS on-disk structures from `hfs.h`.
- HFS file reads from `file.c`.
- Allocation bitmap macros.

Notable constraints:
- B-tree lookup is tailored to the extents B-tree only.
