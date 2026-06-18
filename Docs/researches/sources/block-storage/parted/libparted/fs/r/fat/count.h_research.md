# File Research: sources/block-storage/parted/libparted/fs/r/fat/count.h

Declares cluster/fragment classification data and accessors.

Defines:
- `FatClusterFlag`: free, file, directory, bad.
- Packed `FatClusterInfo`: 6-bit used fraction and 2-bit flag.

Exports:
- `fat_collect_cluster_info()`.
- Cluster flag/usage lookup.
- Fragment flag lookup.
- Active-fragment predicate.

Role:
- Provides the semantic occupancy map consumed by FAT resize relocation and size checks.
