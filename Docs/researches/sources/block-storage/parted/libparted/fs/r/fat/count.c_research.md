# File Research: sources/block-storage/parted/libparted/fs/r/fat/count.c

Traverses directory trees and FAT chains to classify clusters as free, file, directory, or bad, and records partial last-cluster usage.

Key behavior:
- `flag_traverse_fat()` validates a chain, detects unterminated chains, out-of-range clusters, and cross-linked clusters.
- Checks chain length against directory-entry file size and stores last-cluster usage in 1/64 cluster units.
- `flag_traverse_dir()` recursively walks directories using `traverse.c`, skipping `.`/`..`, and flags file/directory chains.
- FAT32 root directory is both traversed and explicitly flagged as directory.
- `_mark_bad_clusters()` imports bad-cluster markers from the FAT table.
- Provides cluster/fragment flag queries and active-fragment detection.

Important dependencies:
- Directory traversal helpers from `traverse.c`.
- FAT table accessors from `table.c`.
- `cluster_info` storage allocated in `fat_alloc_buffers()`.

Notable constraints:
- `cluster_info` uses one packed byte per FAT cluster.
- Long VFAT names are skipped at the directory-entry classification level.
