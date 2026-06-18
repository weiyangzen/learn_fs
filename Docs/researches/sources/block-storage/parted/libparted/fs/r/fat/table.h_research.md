# File Research: sources/block-storage/parted/libparted/fs/r/fat/table.h

Declares the FAT table abstraction.

Defines:
- `FatTable`: raw table buffer, logical/raw size, type, cluster/free/bad counts, and allocation cursor.

Exports:
- Allocation, duplication, destruction, clearing.
- Read/write/write-all/compare/stat-counting.
- Entry get/set.
- Cluster allocation with optional read-check.
- Cluster state predicates and setters.
- Entry-size helper.

Role:
- Shared metadata layer for FAT open/check/create/resize.
