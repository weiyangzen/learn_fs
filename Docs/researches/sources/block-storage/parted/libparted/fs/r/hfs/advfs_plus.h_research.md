# File Research: sources/block-storage/parted/libparted/fs/r/hfs/advfs_plus.h

Declares advanced HFS+ helpers.

Exports:
- HFS+ extents B-tree search.
- Bad-block list free/load/query.
- Empty-tail and minimum-size calculation.
- Start block calculation for packing free space.

Role:
- Used by HFS+ open, resize, file extent lookup, and wrapper handling.
