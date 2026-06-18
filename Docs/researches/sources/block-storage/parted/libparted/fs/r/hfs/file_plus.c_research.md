# File Research: sources/block-storage/parted/libparted/fs/r/hfs/file_plus.c

HFS+ file-fork accessor with multi-sector extent-aware I/O.

Key behavior:
- `hfsplus_file_open()` stores filesystem, CNID, first eight extents, sector count, and cache state.
- `hfsplus_file_find_extent()` maps a logical file sector range to the largest contiguous physical extent slice available from first extents, cached extents, or extents B-tree lookup.
- `hfsplus_file_read()` and `hfsplus_file_write()` validate overflow/EOF, then loop over physical extent slices until the requested range is complete.
- Uses `priv_data->plus_geom`, so it works for both bare HFS+ volumes and embedded HFS+ volumes inside HFS wrappers.

Important dependencies:
- `hfsplus_btree_search()` from `advfs_plus.c`.
- HFS+ volume header block size.
- HFS+ geometry state in `HfsPPrivateFSData`.

Constraints:
- The internal extent lookup is for data forks.
