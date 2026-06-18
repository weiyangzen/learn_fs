# File Research: sources/block-storage/parted/libparted/fs/r/hfs/reloc_plus.c

Purpose: Implements HFS+ extent relocation and free-space packing for resize/compaction when `DISCOVER_ONLY` is disabled. It is the HFS+ analog of `reloc.c`, extended for 32-bit allocation blocks, HFS+ volume-header fork records, attributes B-tree, and journal metadata.

Main interfaces: `hfsplus_update_vh()` rewrites primary and alternate HFS+ volume headers. `hfsplus_pack_free_space_from_block()` is the exported compaction entry point declared in `reloc_plus.h`.

Control flow: `hfsplus_pack_free_space_from_block()` caches extents from the volume header, catalog B-tree, extents overflow B-tree, and attributes B-tree. It then scans occupied allocation blocks and calls `hfsplus_move_extent_starting_at()`, which may do a second relocation pass if a temporary post-source destination was used. `hfsplus_do_move()` updates the relevant volume-header fork, B-tree node, opened file cache, and journal info block/location when the moved extent is journal-related.

Dependencies: HFS+ private structures from `hfs.h`, I/O helpers from `file_plus.h`, bad-block helpers from `advfs_plus.h`, relocation cache from `cache.h`, journal helpers from `journal.h`, libparted geometry/timer/exception APIs, and endian helpers.

Important details and risks: Allocation bitmap persistence is tracked with `dirty_alloc_map` and flushed by sector through the allocation file. B-tree node sizes are read dynamically and allocated with `ped_malloc`; malformed record offsets are checked before use. Extents-overflow self-extents can be cached as `CR_BTREE_EXT_EXT` after a warning, but `hfsplus_do_move()` has no explicit case for moving that reference. Relocation is multi-write and not crash atomic. Tests should cover catalog data/resource forks, attributes fork records, startup/allocation/catalog/extents VH forks, journal info blocks, dirty allocation bitmap flushing, two-pass moves, and failure injection in B-tree rewrites.
