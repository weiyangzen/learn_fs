# File Research: sources/block-storage/parted/libparted/fs/r/hfs/reloc.c

Purpose: Implements classic HFS extent relocation for libparted resize/compaction support when `DISCOVER_ONLY` is not set. It moves allocation blocks, updates extent references in the MDB, catalog B-tree, and extents-overflow B-tree, and compacts used extents away from a requested free-space region.

Main interfaces: `hfs_update_mdb()` rewrites primary and alternate master directory blocks. `hfs_pack_free_space_from_block()` is the exported compaction entry point declared in `reloc.h`.

Control flow: `hfs_pack_free_space_from_block()` builds an in-memory extent cache from MDB/catalog/extent trees, sizes the shared copy buffer, loads bad-block metadata, scans allocation blocks from `fblock`, and uses `hfs_move_extent_starting_at()` for occupied non-bad extents. `hfs_effect_move_extent()` finds a non-overlapping destination before/in the gap/after source, copies chunks via `ped_geometry_read/write`, and updates the allocation bitmap. `hfs_do_move()` then rewrites the owning extent descriptor and moves the cache entry.

Dependencies: HFS private structs from `hfs.h`, file access from `file.h`, advanced HFS helpers from `advfs.h`, cache operations from `cache.h`, endian helpers, `PedGeometry`, `PedTimer`, and libparted exceptions.

Important details and risks: Relocation is not atomic: data, extent references, and allocation bitmap writes can be partially committed, though comments rely on the HFS unmounted bit for protection. Extents overflow self-extents can be cached as `CR_BTREE_EXT_EXT`, but `hfs_do_move()` has no explicit handler for that case after the warning path. Progress divisor depends on `to_free`; invalid caller inputs could make progress reporting misleading. Test coverage should include MDB-only extents, catalog file/data/resource extents, overflow extents, bad-block avoidance, two-pass relocation, and simulated write failures.
