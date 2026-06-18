# File Research: sources/block-storage/parted/libparted/fs/r/hfs/file_plus.h

Declares HFS+ private file accessors.

Exports:
- Open/close for an HFS+ file fork from CNID and initial extents.
- Multi-sector read/write.
- Inline single-sector read/write wrappers.

Role:
- Used for HFS+ special files: allocation, extents, catalog, attributes, startup, and journal-related metadata.
