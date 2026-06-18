# File Research: sources/block-storage/parted/libparted/fs/r/fat/context.c

Builds and manages `FatOpContext`, the resize/copy state that relates an old FAT filesystem to a new one.

Key behavior:
- Chooses fragment size as the smaller old/new cluster size and applies it to both filesystems.
- Computes start movement direction and fragment delta from old/new absolute cluster starts.
- Allocates `buffer_map` for buffered relocation and `remap` for old-fragment to new-fragment mapping.
- Maps static fragments/clusters when old and new filesystems are on the same device and aligned.
- `fat_op_context_create_initial_fat()` creates a provisional destination FAT that reserves statically-mapped used/bad clusters and old metadata sectors overlapping the new data area.

Important dependencies:
- `fat_set_frag_sectors()` from `fat.c`.
- `fat_get_fragment_flag()` from `count.c`.
- `fat_table_new()`, `fat_table_set_cluster_count()`, `fat_table_set_bad()`, `fat_table_set_eof()`.
- `ped_geometry_map()` for metadata-sector overlap.

Notable constraints:
- Cross-device copy disables static mapping and forces duplication.
- The initial FAT is intentionally only an allocation guard, not the final FAT chain layout.
