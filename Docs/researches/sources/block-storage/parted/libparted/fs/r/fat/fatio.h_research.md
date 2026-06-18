# File Research: sources/block-storage/parted/libparted/fs/r/fat/fatio.h

Declares FAT fragment and cluster I/O functions.

Exports:
- Multi-fragment read/write/sync-write.
- Single-fragment wrappers.
- Multi-cluster read/write/sync-write.
- Single-cluster wrappers.

Role:
- Shared I/O interface for traversal, resize relocation, and FAT32 root creation.
