# File Research: sources/block-storage/parted/libparted/fs/r/fat/traverse.c

Directory traversal and FAT directory-entry helpers.

Key behavior:
- `fat_traverse_begin()` opens either a FAT16 fixed root directory buffer or a cluster-chain directory buffer.
- `fat_traverse_next_dir_entry()` iterates entries, writing dirty buffers when moving across directory clusters.
- `fat_traverse_complete()` flushes dirty data and frees traversal state.
- `fat_traverse_directory()` constructs child path text and starts traversal at the child first cluster.
- Provides helpers for reading/writing first-cluster fields, including FAT32 high bits.
- Classifies active entries, files, system files, directories, null terminators, and entries with usable first clusters.
- Converts 8.3 names into printable `NAME.EXT` strings.

Important dependencies:
- FAT I/O from `fatio.c`.
- FAT table chain following.
- FAT constants and directory-entry structure from `fat.h`.

Notable constraints:
- Uses a static 4096-byte path buffer for child traversal names.
- VFAT long-name entries are skipped by file/directory classification.
