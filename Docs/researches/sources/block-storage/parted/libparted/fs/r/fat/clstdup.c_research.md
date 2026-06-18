# File Research: sources/block-storage/parted/libparted/fs/r/fat/clstdup.c

Duplicates old FAT data fragments that cannot remain statically mapped in the resized filesystem. This is the data-moving engine used before the new FAT and directory entries are rebuilt.

Key behavior:
- `needs_duplicating()` duplicates directories unconditionally, files only when they cannot map statically, and skips free/bad fragments.
- Reads marked fragments in buffered groups, falling back to one-fragment reads if a bulk read fails.
- Writes groups quickly by preserving “underlay” fragments in the destination buffer, then falls back to slow one-fragment writes on error.
- Slow path marks failed destination clusters bad and allocates replacement clusters.
- Maintains `ctx->remap` so later FAT-chain and directory reconstruction can map old fragments to new fragments.
- `fat_duplicate_clusters()` initializes remap, counts work, updates the timer, and iterates through all fragments needing duplication.

Important dependencies:
- `FatOpContext` from `context.h`.
- `fat_get_fragment_flag()` from `count.c`.
- `fat_table_alloc_cluster()`, `fat_table_set_bad()`, `fat_table_set_eof()`.
- Fragment I/O from `fatio.c`.

Risk/edge notes:
- Timer update divides by `total_frags_to_dup`; if no fragments need duplication, loop likely does not execute before final `1.0` update.
- Error recovery is local to write failures by allocating alternative clusters.
