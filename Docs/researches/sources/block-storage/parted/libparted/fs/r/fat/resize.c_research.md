# File Research: sources/block-storage/parted/libparted/fs/r/fat/resize.c

Main FAT resize orchestration, including FAT16/FAT32 conversion, data relocation, directory reconstruction, and metadata rewrite.

Key behavior:
- Builds rewritten directory trees by remapping each directory entry’s first cluster.
- Handles FAT16 fixed root directory duplication, FAT32 root directory construction, and FAT16/FAT32 conversion cases.
- Allocates FAT32 root directory clusters before final FAT reconstruction when converting FAT16 to FAT32.
- Frees duplicated FAT32 root clusters after final FAT reconstruction when converting FAT32 to FAT16.
- `fat_construct_new_fat()` clears the provisional FAT and rebuilds final chains from old active fragments through the remap table.
- `get_fat_type()` tests FAT16/FAT32 feasibility and uses libparted exceptions to ask/confirm conversion choices.
- `create_resize_context()` builds a new `PedFileSystem` with preserved boot/info-sector data, new FAT geometry, aligned offsets, initial FAT, and buffers.
- `fat_resize()` performs: context creation, cluster duplication, optional root allocation/free, final FAT build, directory tree build, FAT write, hidden-sector copy, boot/info-sector regeneration, and context assimilation.

Important dependencies:
- `FatOpContext` and duplication from `context.c`/`clstdup.c`.
- Directory traversal from `traverse.c`.
- FAT table operations from `table.c`.
- Sizing/alignment from `calc.c`.

Notable constraints:
- Supports shrinking and FAT16/FAT32 conversion, not arbitrary growth/move semantics.
- Hidden-sector copy is specific to FAT32 boot-loader compatibility.
