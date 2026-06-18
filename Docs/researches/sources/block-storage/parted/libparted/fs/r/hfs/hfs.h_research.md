# File Research: sources/block-storage/parted/libparted/fs/r/hfs/hfs.h

Central HFS/HFS+ definitions header.

Defines:
- Allocation bitmap macros.
- Buffer limits and Apple implementation codes.
- HFS/HFS+/HFSX signatures, versions, attribute bits, B-tree node types, fork types, catalog record types, file IDs, journal constants, and extent counts.
- Packed classic HFS structures: extent descriptors, MDB, B-tree node/header, catalog/extents keys, catalog records.
- Packed HFS+ structures: permissions, extents, fork data, Unicode names, volume header, B-tree records, catalog records, attributes, extents keys.
- Journal info/header/block-list structures.
- Private runtime structures for opened HFS/HFS+ files, bad-block lists, per-filesystem private data, generic B-tree keys, and B-tree leaf references.
- Global block buffers/counts used by HFS/HFS+ modules.

Role:
- Single shared type source for HFS, HFS+, journal, file, cache, and advanced helper modules.
