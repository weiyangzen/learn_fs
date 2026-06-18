# File Research: sources/block-storage/parted/libparted/fs/r/fat/clstdup.h

Small public header for FAT cluster duplication.

Exports:
- `fat_duplicate_clusters(FatOpContext* ctx, PedTimer* timer)`.

Role:
- Included by `fat.h`.
- Exposes the main data-moving step used by `resize.c`.
