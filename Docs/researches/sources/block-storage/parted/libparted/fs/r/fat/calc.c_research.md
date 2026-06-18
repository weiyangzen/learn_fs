# File Research: sources/block-storage/parted/libparted/fs/r/fat/calc.c

Implements FAT sizing, resize-fit checks, alignment math, and conversions between FAT clusters/fragments/sectors. All operational code is excluded under `DISCOVER_ONLY`.

Key behavior:
- Defines minimum/recommended/maximum cluster sizes and cluster-count limits for FAT12/FAT16/FAT32.
- `fat_calc_sizes()` searches for a compatible cluster size and FAT table size using Parted’s empirical Windows-compatible sizing algorithm.
- `fat_calc_resize_sizes()` is resize-specific and only searches current-or-smaller cluster sizes because the resizer cannot increase cluster size.
- `fat_check_resize_geometry()` compares old free space with the amount required for shrink plus directory relocation overhead.
- `fat_calc_align_sectors()` preserves old/new data-cluster alignment while greedily consuming spare metadata padding.
- Provides pure mapping helpers: cluster to fragment, fragment to cluster, fragment to sector, sector to fragment, cluster to sector, sector to cluster.

Important dependencies:
- Uses `FatSpecific`, `FatTable`, and geometry state from `fat.h`.
- Uses `ped_div_round_up`, `PED_MAX`, `PED_ASSERT`, and `ped_exception_throw`.

Notable constraints:
- FAT12 constants exist, but most resize code is practically FAT16/FAT32 oriented.
- The sizing algorithm is intentionally non-obvious and explicitly treated as compatibility-sensitive.
