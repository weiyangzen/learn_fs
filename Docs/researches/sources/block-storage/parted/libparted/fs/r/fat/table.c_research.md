# File Research: sources/block-storage/parted/libparted/fs/r/fat/table.c

Implements in-memory FAT table allocation, reading/writing, comparison, entry access, status predicates, and cluster allocation.

Key behavior:
- `fat_table_new()` allocates a sector-rounded raw FAT buffer and initializes reserved entries.
- Maintains `cluster_count`, free count, bad count, and last allocation hint.
- Reads a selected FAT copy from disk and checks first media byte against the boot sector.
- Writes one or all FAT copies synchronously.
- Compares FAT copies entry-by-entry.
- `fat_table_get()`/`fat_table_set()` handle FAT16 and FAT32 little-endian entries; FAT12 paths are mostly assertions/stubs.
- Provides predicates for bad, EOF, available, empty, and active clusters.
- Allocates clusters by scanning from `last_alloc`; `fat_table_alloc_check_cluster()` probes readability before accepting a cluster.

Important dependencies:
- `FatSpecific` geometry and boot sector media byte.
- `ped_geometry_read/write/sync`.
- Endian helpers.

Notable constraints:
- FAT12 entry size returns 2 as a FIXME, while FAT12 get/set are not implemented.
