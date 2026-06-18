# Group Research: parted resizable FAT/HFS sources

Scope checked: `Docs/research_subset_a.md` includes `sources/block-storage/parted`, so all listed files are in subset A.

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/calc.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/calc.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/calc.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/fat/calc.h

Declares the FAT sizing and address-conversion interface implemented by `calc.c`.

Exports:
- Cluster size/count bound helpers.
- Reserved-sector count helper.
- General creation sizing and resize sizing calculators.
- Resize geometry viability check.
- Alignment calculation between old/new filesystems.
- Sector/fragment/cluster conversion helpers.

Role:
- Shared header for FAT create/open/check/resize code.
- Depends on FAT core types from `fat.h` inclusion ordering.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/calc.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/clstdup.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/clstdup.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/clstdup.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/fat/clstdup.h

Small public header for FAT cluster duplication.

Exports:
- `fat_duplicate_clusters(FatOpContext* ctx, PedTimer* timer)`.

Role:
- Included by `fat.h`.
- Exposes the main data-moving step used by `resize.c`.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/clstdup.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/context.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/context.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/context.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/fat/context.h

Defines FAT resize operation state.

Important types:
- `FatDirection`: forward/backward cluster-start movement.
- `FatOpContext`: old/new filesystem pointers, fragment geometry, movement delta, buffered relocation map, remap table, duplicated-fragment counter, and FAT32 root-directory allocation list.

Exports:
- Context creation/destruction.
- Static and final fragment/cluster mapping helpers.
- Initial destination FAT creation.

Role:
- Central shared state between `resize.c`, `clstdup.c`, and FAT reconstruction code.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/context.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/count.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/count.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/count.h -->
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
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/count.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/fat.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/fat/fat.c

Core FAT filesystem lifecycle and libparted operations: allocate, open, create, close, check, copy, and resize/create constraints.

Key behavior:
- `fat_alloc()` creates `PedFileSystem`, `FatSpecific`, and duplicate geometry.
- `fat_alloc_buffers()` allocates the shared 512 KiB sector buffer and one-byte-per-cluster info table.
- `fat_open()` reads/analyzes boot sector, opens FAT32 info sector, reads FAT table, allocates buffers, and collects cluster info.
- `fat_create()` computes FAT sizing, initializes geometry fields, creates FAT16 or FAT32 metadata, writes boot/info sectors and FAT tables, and clears root directory for FAT16.
- `fat_check()` recomputes expected sizes, compares duplicate FATs, checks FAT32 free-cluster info-sector value, and marks the filesystem checked.
- `fat_get_copy_constraint()` and resize/create constraints derive minimum sizes from used clusters plus directory relocation needs.
- `fat_copy()` is implemented as open then resize into the target geometry.

Important dependencies:
- Boot sector and info-sector helpers from other FAT files.
- Size math from `calc.c`.
- Table operations from `table.c`.
- Cluster classification from `count.c`.

Notable constraints:
- Only FAT16 and FAT32 are created through public helpers here.
- Resize minimum is found by binary search because FAT sizing is not directly invertible.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/fat.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/fat.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/fat/fat.h

Umbrella header for the FAT implementation.

Defines:
- Core FAT scalar types: `FatCluster`, `FatFragment`, `FatType`.
- Packed on-disk `FatDirEntry`.
- `FatSpecific`, the per-filesystem state containing boot/info sectors, geometry, FAT type, offsets, table, cluster info, and shared buffers.
- FAT constants for attributes, root directory size, and max cluster counts.

Includes:
- `table.h`, `bootsector.h`, `context.h`, `fatio.h`, `traverse.h`, `calc.h`, `count.h`, `clstdup.h`.

Exports:
- FAT filesystem types.
- Allocation/free/buffer functions.
- `fat_resize()`.
- Fragment-size setter.

Role:
- Central compile-time coupling point for the FAT resizer.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/fat.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/fatio.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/fat/fatio.c

Thin I/O adapter over `PedGeometry` for FAT fragments and clusters.

Key behavior:
- Converts fragment or cluster numbers to filesystem-relative sectors.
- Reads/writes one or more fragments.
- Reads/writes one or more clusters.
- Provides sync-write variants that call `ped_geometry_sync()` after the write.

Important dependencies:
- Mapping helpers from `calc.c`.
- FAT geometry fields from `FatSpecific`.

Constraints:
- Asserts fragment/cluster ranges before I/O.
- All sector math assumes the FAT implementation’s 512-byte sector model.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/fatio.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/fatio.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/fat/fatio.h

Declares FAT fragment and cluster I/O functions.

Exports:
- Multi-fragment read/write/sync-write.
- Single-fragment wrappers.
- Multi-cluster read/write/sync-write.
- Single-cluster wrappers.

Role:
- Shared I/O interface for traversal, resize relocation, and FAT32 root creation.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/fatio.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/resize.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/resize.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/table.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/table.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/table.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/fat/table.h

Declares the FAT table abstraction.

Defines:
- `FatTable`: raw table buffer, logical/raw size, type, cluster/free/bad counts, and allocation cursor.

Exports:
- Allocation, duplication, destruction, clearing.
- Read/write/write-all/compare/stat-counting.
- Entry get/set.
- Cluster allocation with optional read-check.
- Cluster state predicates and setters.
- Entry-size helper.

Role:
- Shared metadata layer for FAT open/check/create/resize.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/table.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/traverse.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/traverse.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/traverse.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/fat/traverse.h

Declares FAT directory traversal state and directory-entry helper functions.

Defines:
- `FatTraverseInfo`: filesystem pointer, directory name, legacy-root flag, dirty/eof flags, current buffer, next buffer, and entry buffer.

Exports:
- Traversal begin/complete/child traversal.
- Dirty marking and next-entry iteration.
- Directory-entry first-cluster get/set.
- Length, name, active/file/system/directory/null/first-cluster predicates.

Role:
- Used by cluster counting and resize directory reconstruction.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/fat/traverse.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/filesys.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/filesys.c

Generic libparted filesystem operation dispatch for the resizable filesystem subset.

Key behavior:
- Maps probed type names to open/close/resize/constraint functions for HFS, HFS+, HFSX, and FAT.
- `ped_file_system_open()` opens the device, probes the filesystem, validates probed geometry against the supplied geometry, dispatches to type-specific open, and attaches type.
- `ped_file_system_close()` dispatches close and closes the device.
- `ped_file_system_resize()` clobbers signatures in the target geometry outside the existing filesystem, then dispatches type-specific resize.
- `ped_file_system_get_resize_constraint()` dispatches type-specific constraint calculation.
- Static clobber helpers clear filesystem signatures at start/end while respecting an exclude geometry.

Important dependencies:
- FAT/HFS/HFS+ exported open/close/resize/constraint functions.
- `pt-tools.h` sector clearing.
- libparted probing and geometry APIs.

Notable constraints:
- Only the explicitly mapped filesystem families are supported by this resize frontend.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/filesys.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/advfs.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/advfs.c

Advanced classic HFS helpers for extents B-tree lookup, bad-block tracking, and shrink boundary calculation.

Key behavior:
- Compares HFS extent keys by file ID, fork type, and start block without unsafe subtraction on 32-bit file IDs.
- `hfs_btree_search()` walks the extents B-tree from header/root through index nodes to a leaf record at or below the search key.
- Loads bad-block extents from the extents overflow file into a linked list.
- Frees and queries the bad-block extent list.
- `hfs_get_empty_end()` finds the first sector of the free tail region after considering the last bad block and allocation bitmap.
- `hfs_find_start_pack()` finds where relocation must begin to free a requested number of blocks at the end.

Important dependencies:
- HFS on-disk structures from `hfs.h`.
- HFS file reads from `file.c`.
- Allocation bitmap macros.

Notable constraints:
- B-tree lookup is tailored to the extents B-tree only.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/advfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/advfs.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/advfs.h

Declares advanced classic HFS helpers.

Exports:
- Extents B-tree search.
- Bad-block list free/load/query.
- Empty-tail sector calculation.
- Start block calculation for packing free space.

Role:
- Used by HFS open/resize and HFS file extent lookup.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/advfs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/advfs_plus.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/advfs_plus.c

HFS+ counterpart to `advfs.c`, adapted for HFS+ extent key formats, larger node sizes, 32-bit allocation block numbers, and wrapper-aware minimum sizing.

Key behavior:
- Compares HFS+ extent keys by file ID, fork type, and 32-bit start block.
- `hfsplus_btree_search()` reads the HFS+ extents B-tree header, allocates node-sized buffers, walks index nodes, and returns matching leaf data/reference.
- Loads HFS+ bad-block extents into a linked list.
- Queries whether an allocation block lies in a bad-block extent.
- `hfsplus_get_empty_end()` computes free tail boundary after bad blocks.
- `hfsplus_get_min_size()` adjusts minimum shrink size when the HFS+ volume is embedded in an HFS wrapper.
- `hfsplus_find_start_pack()` finds a block from which relocation should pack data forward.

Important dependencies:
- HFS+ file reads from `file_plus.c`.
- Classic HFS helper `hfs_get_empty_end()` for wrapper calculations.
- HFS/HFS+ structures in `hfs.h`.

Notable issue:
- In `hfsplus_btree_search()`, the path after allocating `node` and failing the first `hfsplus_file_read()` returns without freeing `node`.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/advfs_plus.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/advfs_plus.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/advfs_plus.h

Declares advanced HFS+ helpers.

Exports:
- HFS+ extents B-tree search.
- Bad-block list free/load/query.
- Empty-tail and minimum-size calculation.
- Start block calculation for packing free space.

Role:
- Used by HFS+ open, resize, file extent lookup, and wrapper handling.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/advfs_plus.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/cache.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/cache.c

Custom extent cache for HFS/HFS+ relocation code.

Key behavior:
- `hfsc_new_cache()` creates an indexed linked-reference table plus one or more extent allocation tables.
- Avoids integer overflow when computing linked-reference table size.
- `hfsc_cache_add_extent()` rejects duplicate start blocks, appends storage tables as needed, records extent metadata, and updates required copy-buffer size.
- `hfsc_cache_search_extent()` looks up an extent by start block.
- `hfsc_cache_move_extent()` relocates a cached extent from one start block index to another and rejects duplicate destinations.
- `hfsc_delete_cache()` frees all table blocks and index references.

Important dependencies:
- Cache structures and constants from `cache.h`.
- Libparted exceptions for duplicate extent errors.

Role:
- Tracks extents by allocation-block start for relocation metadata updates.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/cache.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/cache.h

Defines the HFS common extent-cache structures and reference tags.

Key definitions:
- `CR_*` constants identify where an extent reference comes from, such as primary catalog/extents/allocation records, B-tree records, journal info block, or journal.
- Cache tuning constants control hash/index granularity and allocation table growth.
- `HfsCPrivateExtent` records extent start/length plus the metadata location that references it.
- `HfsCPrivateCacheTable` stores allocated extent records.
- `HfsCPrivateCache` owns the table list, linked-reference index, and required buffer size.

Exports:
- Cache create/delete.
- Add/search/move extent.
- Inline needed-buffer query.

Role:
- Support layer for HFS/HFS+ relocation modules outside this file group.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/cache.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/file.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/file.c

Classic HFS file-fork sector accessor.

Key behavior:
- `hfs_file_open()` stores filesystem, CNID, first three extents, sector count, and initializes extent cache state.
- `hfs_file_find_sector()` maps a logical file sector to an absolute filesystem sector via first extents, cached overflow extents, or a fresh extents B-tree lookup.
- `hfs_file_read_sector()` and `hfs_file_write_sector()` validate EOF bounds, map the sector, and dispatch geometry read/write.
- `hfs_get_extent_containing()` searches the HFS extents overflow file for the extent record covering a logical allocation block.

Important dependencies:
- `hfs_btree_search()` from `advfs.c`.
- Classic HFS volume allocation block size and start block from the MDB.
- Big-endian on-disk extents.

Constraints:
- Only data forks are supported by the extent lookup helper.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/file.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/file.h

Declares classic HFS private file accessors.

Exports:
- Open/close for an HFS file fork from CNID and initial extents.
- Single-sector read/write.

Role:
- Used to access HFS special files such as extents and catalog files.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/file.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/file_plus.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/file_plus.c

HFS+ file-fork accessor with multi-sector extent-aware I/O.

Key behavior:
- `hfsplus_file_open()` stores filesystem, CNID, first eight extents, sector count, and cache state.
- `hfsplus_file_find_extent()` maps a logical file sector range to the largest contiguous physical extent slice available from first extents, cached extents, or extents B-tree lookup.
- `hfsplus_file_read()` and `hfsplus_file_write()` validate overflow/EOF, then loop over physical extent slices until the requested range is complete.
- Uses `priv_data->plus_geom`, so it works for both bare HFS+ volumes and embedded HFS+ volumes inside HFS wrappers.

Important dependencies:
- `hfsplus_btree_search()` from `advfs_plus.c`.
- HFS+ volume header block size.
- HFS+ geometry state in `HfsPPrivateFSData`.

Constraints:
- The internal extent lookup is for data forks.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/file_plus.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/file_plus.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/file_plus.h

Declares HFS+ private file accessors.

Exports:
- Open/close for an HFS+ file fork from CNID and initial extents.
- Multi-sector read/write.
- Inline single-sector read/write wrappers.

Role:
- Used for HFS+ special files: allocation, extents, catalog, attributes, startup, and journal-related metadata.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/file_plus.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/hfs.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/hfs.c

Main classic HFS and HFS+ open/close/resize implementation.

Classic HFS behavior:
- `hfs_open()` validates 512-byte-sector geometry, reads the MDB, opens extents/catalog files, reads allocation bitmap, duplicates geometry, and sets checked state from the unmounted bit.
- `hfs_close()` frees opened files, bad-block list, MDB, private data, geometry, and filesystem object.
- `hfs_get_resize_constraint()` fixes start alignment and computes minimum size from `hfs_get_empty_end() + 2`.
- `hfs_resize()` supports same-start shrink only, clears unmounted bit, packs data away from the tail, verifies freed tail, marks out-of-volume blocks used, updates MDB block/free counts and geometry, then writes MDB.

HFS+ behavior:
- `hfsplus_open()` detects optional HFS wrapper, sets `plus_geom`, reads volume header, validates HFS+/HFSX signature/version, replays journal if needed, opens special files, loads allocation bitmap, and sets checked state from unmounted/inconsistent flags.
- `hfsplus_close()` frees bad-block list, allocation maps, special files, wrapper, geometry, volume header, and private state.
- `hfsplus_get_resize_constraint()` uses `hfsplus_get_min_size()`.
- `hfsplus_volume_resize()` supports shrink of the HFS+ volume: clears unmounted bit, sets implementation code, packs data, updates total/free blocks, marks out-of-volume and reserved tail blocks used, writes allocation bitmap, and updates volume header.
- `hfsplus_wrapper_update()` updates the HFS wrapper MDB, wrapper allocation bitmap, and bad-block extents record for embedded HFS+.
- `hfsplus_resize()` orchestrates bare or wrapped HFS+ shrink with nested timers.

Optional debug code:
- Under `HFS_EXTRACT_FS`, can extract low-level HFS/HFS+ metadata files for debugging rather than repair.

Important dependencies:
- Probe helpers, file accessors, advanced FS helpers, relocation modules, and journal replay.
- Packed on-disk structures from `hfs.h`.

Notable constraints:
- No grow or start-move support for HFS/HFS+ resize.
- HFS+ journal replay can require restarting Parted if the volume header or MDB changed.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/hfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/hfs.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/hfs.h

Central HFS/HFS+ definitions header.

Defines:
- Allocation bitmap macros.
- Buffer limits and Apple implementation codes.
- HFS/HFS+/HFSX signatures, versions, attribute bits, B-tree node types, fork types, catalog record types, file IDs, journal constants, and extent counts.
- Packed classic HFS structures: extent descriptors, MDB, B-tree node/header, catalog/extents keys, catalog records.
- Packed HFS+ structures: permissions, extents, fork data, Unicode names, volume header, B-tree records, catalog records, attributes, extents keys.
- Journal info/header/block-list structures.
- Private runtime structures for opened HFS/HFS+ files, bad-block lists, per-filesystem private data, generic B-tree keys, and B-tree leaf references.
- Global block buffers/counts used by HFS/HFS+ modules.

Role:
- Single shared type source for HFS, HFS+, journal, file, cache, and advanced helper modules.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/hfs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/journal.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/journal.c

HFS+ journal replay and journal-location update helpers.

Key behavior:
- Computes Apple-style journal checksums.
- `hfsj_update_jib()` updates the volume header’s journal info block pointer and writes the volume header.
- `hfsj_update_jl()` updates the journal info block’s journal offset.
- `hfsj_replay_journal()` reads the journal info block and journal header, validates in-volume journal placement, sector-size alignment, magic values, size consistency, header sizes, and checksum.
- Detects journal endianness and uses endian-conversion macros from `journal.h`.
- Prompts before replaying non-empty journals.
- `hfsj_replay_transaction()` walks journal block-list headers, validates checksums and block sizes, reads transaction blocks from the circular journal, writes them to target sectors, syncs, and advances journal start.
- Warns and aborts open if replay changed the volume header or wrapper MDB.

Important dependencies:
- HFS+ relocation header for `hfsplus_update_vh()`.
- HFS/HFS+ journal structures from `hfs.h`.
- Libparted geometry read/write/sync and exception APIs.

Notable constraints:
- Journals outside the volume are unsupported.
- Only 512-byte journal sectors are supported.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/journal.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/journal.h

Declares HFS+ journal helpers and endian conversion macros.

Exports:
- `hfsj_replay_journal()`.
- `hfsj_update_jib()`.
- `hfsj_update_jl()`.

Defines:
- `HFS_16_TO_CPU`, `HFS_32_TO_CPU`, `HFS_64_TO_CPU`.
- `HFS_CPU_TO_16`, `HFS_CPU_TO_32`, `HFS_CPU_TO_64`.

Role:
- Shared journal API for HFS+ open/relocation code.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/journal.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/probe.c -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/probe.c

HFS geometry validation and wrapper probing.

Key behavior:
- `hfsc_can_use_geom()` rejects devices whose sector size is not 512 bytes.
- `hfs_and_wrapper_probe()` reads the classic HFS MDB at sector 2, validates HFS signature, computes the expected end of the HFS allocation area, and searches one allocation block past it for an alternate MDB signature.
- Returns a geometry covering the HFS or HFS wrapper length when detected.

Important dependencies:
- HFS MDB structure from `hfs.h`.
- Libparted geometry and exception APIs.

Role:
- Used by HFS/HFS+ open and probing to detect HFS wrappers around embedded HFS+ volumes.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/probe.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/probe.h -->
# File Research: sources/block-storage/parted/libparted/fs/r/hfs/probe.h

Declares HFS probe helpers.

Exports:
- `hfsc_can_use_geom(PedGeometry* geom)`.
- `hfs_and_wrapper_probe(PedGeometry* geom)`.

Role:
- Shared probe interface for HFS and HFS+ open paths.
<!-- END FILE RESEARCH: sources/block-storage/parted/libparted/fs/r/hfs/probe.h -->