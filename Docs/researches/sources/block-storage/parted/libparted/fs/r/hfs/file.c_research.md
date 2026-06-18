# File Research: sources/block-storage/parted/libparted/fs/r/hfs/file.c

Classic HFS file-fork sector accessor.

Key behavior:
- `hfs_file_open()` stores filesystem, CNID, first three extents, sector count, and initializes extent cache state.
- `hfs_file_find_sector()` maps a logical file sector to an absolute filesystem sector via first extents, cached overflow extents, or a fresh extents B-tree lookup.
- `hfs_file_read_sector()` and `hfs_file_write_sector()` validate EOF bounds, map the sector, and dispatch geometry read/write.
- `hfs_get_extent_containing()` searches the HFS extents overflow file for the extent record covering a logical allocation block.

Important dependencies:
- `hfs_btree_search()` from `advfs.c`.
- Classic HFS volume allocation block size and start block from the MDB.
- Big-endian on-disk extents.

Constraints:
- Only data forks are supported by the extent lookup helper.
