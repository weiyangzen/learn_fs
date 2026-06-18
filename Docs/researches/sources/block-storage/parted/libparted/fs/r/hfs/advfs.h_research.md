# File Research: sources/block-storage/parted/libparted/fs/r/hfs/advfs.h

Declares advanced classic HFS helpers.

Exports:
- Extents B-tree search.
- Bad-block list free/load/query.
- Empty-tail sector calculation.
- Start block calculation for packing free space.

Role:
- Used by HFS open/resize and HFS file extent lookup.
