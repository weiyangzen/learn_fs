# File Research: sources/block-storage/parted/libparted/fs/hfs/hfs.h

Comprehensive HFS/HFS+/HFSX on-disk and private-state header. It defines allocation-bitmap macros, buffer limits, Apple creator codes, HFS/HFS+/HFSX signatures and versions, volume attribute bits, B-tree node kinds, catalog record kinds, well-known file IDs, journal constants, and HFSX compare modes.

The HFS section defines packed structures for extents, master directory block, B-tree node/header records, catalog and extent keys, directory/file records, and thread records. The HFS+ section defines permissions, extent descriptors, fork data, Unicode names, volume header, B-tree records, catalog records, extents keys, attributes, and journal info/header/block list structures.

The private section defines in-memory file handles, extent lists, filesystem data for HFS and HFS+, generic B-tree keys, and B-tree leaf record references. External globals `hfs_block`, `hfsp_block`, and counters support shared block buffers. This header is used beyond probing by resize/relocation code, so it is much broader than `probe.c` requires.
