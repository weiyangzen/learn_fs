# Group Research: group_1886_xfsprogs_sources_local_fs_xfsprogs_repair_dinode_c_sources_local_fs_0913eac2383d

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/dinode.c -->
# File Research: sources/local-fs/xfsprogs/repair/dinode.c

## Role

`dinode.c` is the central inode verifier and repair engine for `xfs_repair`. It validates on-disk inode cores, data forks, attribute forks, block mappings, symlinks, directories, quota files, realtime metadata files, reflink metadata, and metadata-directory inodes. It is called by phase 3 for inode discovery and semantic checks, and by phase 4 for duplicate-block detection and final block-map accounting.

## Main Responsibilities

- Translate and validate bmbt extent records for data and attr forks.
- Maintain repair’s in-core block ownership map while scanning inode forks.
- Detect duplicate, metadata, free, CoW, and invalid block claims.
- Validate realtime extents and rtgroup-aware realtime block mappings.
- Validate special XFS metadata inodes: root, quota, realtime bitmap/summary, rtrmap, rtrefcount.
- Repair correctable inode-core fields and clear unrecoverably corrupt inodes.
- Attempt bmap rebuilds from rmap data before clearing bad data/attr forks.
- Validate symlink, quota, directory, and attribute contents through specialized helpers.
- Mark metadata-directory tree contents for later recreation.

## Key Types and State

- `enum xr_ino_type` classifies discovered inode intent: directory, realtime data, quota, regular data, symlink, device, fifo/socket, realtime bitmap/summary/rmap/refcount.
- Static translated strings cache fork and file type names to avoid gettext contention in parallel AG scans.
- `zap_metadata` marks metadata directory files whose contents should be discarded because phase 6 rebuilds the metadata directory tree.

## Inode Clearing

- `clear_dinode_attr` removes an attr fork by resetting attr extent counts, attr format, shortform attr header, and `di_forkoff`.
- `clear_dinode_core` zeros and reinitializes a dinode core with magic, version, generation, formats, v3 inode number, and UUID.
- `zero_dinode` clears core, unlinked pointer, and fork payload.
- `clear_dinode` additionally notifies realtime/rmap/refcount repair code when critical metadata inodes are cleared, so later checks avoid trusting now-invalid metadata.

## Extent and Block Mapping Validation

`process_bmbt_reclist_int` is the core extent scanner. For each extent record it:

- Decodes disk bmbt records to in-core `xfs_bmbt_irec`.
- Verifies file offset ordering.
- Rejects zero-length extents.
- Rejects unwritten extents in attr forks and non-regular files.
- Validates physical block ranges against data device, realtime device, or rtgroup geometry.
- Ensures file offsets do not exceed `XFS_MAX_FILEOFF`.
- Optionally populates a per-inode `blkmap` used later to read directories, symlinks, quotas, and metadata files.
- Checks repair’s global in-core block map for illegal ownership conflicts.
- Marks accepted blocks as `XR_E_INUSE`, `XR_E_METADATA`, or `XR_E_MULT`.
- Adds reverse-map records when rmap collection is active.

The public wrappers split behavior:

- `process_bmbt_reclist` validates and updates the block map.
- `scan_bmbt_reclist` validates against known duplicate extents without mutating the block map.

## Realtime Handling

Realtime support has two paths:

- Legacy realtime extents use the compact `rt_bmap` and `rt_lock`.
- Rtgroup-enabled filesystems use the same grouped bmap abstraction as data AGs, with `isrt=true`.

`process_rt_rec`, `check_rt_rec_state`, and `process_rt_rec_state` validate realtime block ranges, enforce realtime extent alignment semantics, detect duplicate realtime references, and account for reflink-capable realtime files.

## Metadata Btree Inodes

The file supports in-inode roots for realtime metadata btrees:

- `process_rtrmap` validates realtime reverse mapping btree metadata files.
- `process_rtrefc` validates realtime refcount btree metadata files.

Both require metadata inode flags, verify association with an rtgroup when applicable, validate root level and root size, check key ordering, and traverse child blocks through `scan_lbtree`. They deliberately skip duplicate-block reprocessing when the metadata btree will be rebuilt.

## Data Fork Processing

`process_inode_data_fork` validates the data fork according to `di_format`:

- `LOCAL`: checks fork-local size limits.
- `EXTENTS`: scans inline extents.
- `BTREE`: validates and traverses bmap btree roots and children.
- `META_BTREE`: dispatches to realtime rmap/refcount validators.
- `DEV`: accepted for device inodes.

If a data fork is corrupt and rmap data is usable, it attempts `rebuild_bmap`. If rebuild fails, it clears the whole inode unless running in no-modify mode.

## Attribute Fork Processing

`process_inode_attr_fork` validates attr format, attr extent count, attr btree/extents, and optional semantic attr contents via `process_attributes`. On corruption it attempts attr fork bmap rebuild, then clears only the attr fork if rebuild fails. This is intentionally less destructive than clearing the whole inode because the data fork may already have been accounted into the global block map.

## Core Inode Validation

`process_dinode_int` is the main state machine. It validates and repairs:

- CRC, magic, inode version, `di_next_unlinked`.
- v3 inode number and UUID.
- Negative sizes.
- Free/in-use consistency against the in-core inode map.
- Mode and fork format compatibility.
- `di_flags` and `di_flags2` feature constraints.
- Metadata-directory flags.
- Reflink, realtime, bigtime, nrext64, and CoW extent-size feature compatibility.
- Timestamp nanoseconds for legacy timestamps.
- Extent size and CoW extent size hints.
- Size rules for directories, symlinks, special files, quotas, and realtime metadata inodes.
- Attr fork offset constraints.
- Data and attr fork block/extent counts.
- Semantic contents for directories, symlinks, and quota files.

It returns whether the inode was corrupt, while separately reporting whether it should be considered used, whether it is a directory, and whether the disk buffer must be written.

## Semantic Content Checks

- Directories are delegated to `process_dir2`.
- Symlinks are checked for length, zero size, remote block readability, CRC/header validity, and embedded NUL characters.
- Quota files are scanned by dquot cluster, with CRC, UUID, type, and record verification; bad dquot records are repaired in place if modification is allowed.

## Public Entrypoints

- `process_dinode`: full processing and possible repair.
- `verify_dinode`: core-only verification, no modification.
- `verify_uncertain_dinode`: quiet verification for candidate inodes discovered through directory entries.
- `get_agino_buf`: reads an inode cluster buffer and returns a pointer to a specific dinode.

## Repair Model

This file is conservative: structural inconsistencies that could lead to unsafe interpretation normally clear the inode or fork. Recoverable counter/flag/timestamp errors are fixed in place. Bmap rebuild is attempted only when rmap information can plausibly reconstruct fork mappings.

## Interactions

- Calls `process_dir2` for directory data.
- Uses `blkmap` helpers from `bmap` to map inode file offsets to physical blocks.
- Updates `incore` block states and inode state bits.
- Calls rmap/refcount/realtime repair helpers when metadata is invalidated.
- Depends on `globals` for no-modify mode, quota inode state, root/metadir repair flags, and feature-upgrade state.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/dinode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/dinode.h -->
# File Research: sources/local-fs/xfsprogs/repair/dinode.h

## Role

`dinode.h` declares the inode and bmbt processing API used across xfs_repair phases.

## Exposed API

- `convert_extent`: converts a disk bmbt record into offset, start block, block count, and flags.
- `process_bmbt_reclist`: validates a bmbt record list and updates block accounting.
- `scan_bmbt_reclist`: validates a record list against duplicate extents without updating global ownership.
- `process_dinode`: full inode verification/repair entrypoint.
- `verify_dinode`: core validation for known inodes.
- `verify_uncertain_dinode`: quiet validation for candidate inodes.
- `process_uncertain_aginodes`, `process_aginodes`, `check_uncertain_aginodes`: AG-level inode scan workflow hooks.
- `get_agino_buf`: random-access inode cluster read helper.
- `dinode_bmbt_translation_init`, `get_forkname`: translation/string helpers for diagnostics.

## Interactions

This header binds phase drivers, directory repair, bmap scanning, and inode discovery to `dinode.c`. It intentionally exposes only high-level inode processing functions and keeps the detailed repair policy private to `dinode.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/dir2.c -->
# File Research: sources/local-fs/xfsprogs/repair/dir2.c

## Role

`dir2.c` validates and performs limited repair of XFS v2/v3 directory formats during inode processing. It supports shortform, block, leaf, and node directories. Its output feeds inode discovery, parent tracking, dot/dotdot repair decisions, and later directory rebuilding.

## Bad Directory Tracking

The file maintains a process-wide locked list of directory inode numbers whose leaf/node linkage is known bad. `dir2_is_badino` lets future passes avoid repeatedly traversing known-bad leaf/node btrees.

## Shortform Directories

`process_sf_dir2` validates inline directory data stored in the inode data fork. It checks and repairs:

- Entry count consistency.
- `i8count` consistency and conversion from 64-bit inode encoding back to compact encoding when possible.
- Directory size versus actual encoded entries.
- Entry offsets and regenerated legal offsets.
- Invalid, self-referential, special metadata, free, or nonexistent child inode references.
- Illegal names and zero-length names.
- Parent pointer validity.

During inode discovery it adds valid but unknown child inodes to the uncertain inode tree. Outside discovery, unknown or free entries are junked.

Special handling:

- Shortform directories do not store explicit `.` or `..` entries; the parent inode is in the header.
- Root `..` is corrected to self.
- Non-root self-parenting is cleared for later phase 6 reconstruction.
- Metadata directories are always rebuilt, so child inode state is not used to reject entries.

## Block Directories

`process_block_dir2` reads the single directory block via the inode `blkmap`, validates block magic, bounds the leaf array against the tail, processes the data area, and marks buffers dirty if fixups or checksum recomputation are needed.

## Directory Data Blocks

`process_dir2_data` is the common validator for longform directory data blocks. It:

- Verifies free-space entries, data-entry tags, alignment, and bestfree ordering.
- Rejects structurally corrupt blocks so later phases can rebuild or junk them.
- Validates child inode numbers.
- Marks bad entries by replacing the first name byte with `/`, which makes them recognizable for later cleanup.
- Preserves `.` and `..` long enough for special correction logic.
- Corrects bad `.` inode numbers.
- Detects and clears duplicate `.` or `..`.
- Rejects non-dot entries that point to the containing directory.
- Repairs bestfree tables with `libxfs_dir2_data_freescan`.

## Leaf and Node Directories

`process_leaf_block_dir2` validates leaf block entry count, stale count, and hash ordering.

`process_leaf_level_dir2` walks leaf blocks left to right, verifies sibling back pointers, validates parent btree paths with `verify_da_path`, and checks the final rightmost path with `verify_final_da_path`.

`process_node_dir2` traverses the directory btree to the leftmost leaf, then delegates leaf walking and parent path verification.

`process_leaf_node_dir2` scans all mapped data blocks below the leaf area and then, for node directories, verifies the leaf/node btree unless the directory is already known bad.

## Public Entrypoint

`process_dir2` chooses the processing path from inode format and final file block offset:

- Local format and size within inode fork: shortform.
- One directory block: block format.
- Blocks extending into leaf/node region: leaf/node format.
- Anything else: invalid size/format.

It reports missing `.` and `..` entries. Missing root or metadata-root `..` sets global repair flags so later phases can recreate them.

## Interactions

- Uses inode trees from `incore` to decide whether referenced inodes exist, are confirmed, or are free.
- Adds unknown directory references to uncertain inode lists during phase 3 discovery.
- Uses `blkmap` and `da_read_buf` to read directory blocks.
- Cooperates with phase 6 by marking bad entries and deferring graph-level dot/dotdot reconstruction.
- Checks global quota, realtime, rtrmap, rtrefcount, and metadata root inode identities so user directories cannot retain special metadata references.

## Repair Model

Directory repair here is intentionally local. It fixes obvious encoding and entry problems, but does not fully rebuild directory topology. Parent/child graph consistency and dot/dotdot reconstruction happen later when all inode references are known.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/dir2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/dir2.h -->
# File Research: sources/local-fs/xfsprogs/repair/dir2.h

## Role

`dir2.h` declares the directory v2 repair interface.

## Exposed API

- `process_dir2`: validates and locally repairs a directory inode’s contents.
- `process_sf_dir2_fixi8`: rewrites shortform directory entries when `i8count` drops to zero.
- `dir2_is_badino`: tests whether a directory is known to have corrupt leaf/node linkage.

## Interactions

This header connects `dinode.c` to directory semantic checking and lets other code query the bad-directory cache.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/dir2.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/err_protos.h -->
# File Research: sources/local-fs/xfsprogs/repair/err_protos.h

## Role

`err_protos.h` declares the shared diagnostic and fatal error functions used throughout repair code.

## API

- `do_abort`: fatal internal error, marked `noreturn` and printf-format checked.
- `do_error`: fatal system or repair error, marked `noreturn` and printf-format checked.
- `do_warn`: nonfatal warning.
- `do_log`: progress/log output.

## Importance

The printf format attributes give compile-time validation for the many translated diagnostic strings throughout repair. The distinction between abort/error/warn/log is central to xfs_repair’s behavior in no-modify versus modifying modes.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/err_protos.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/globals.c -->
# File Research: sources/local-fs/xfsprogs/repair/globals.c

## Role

`globals.c` defines global state shared by xfs_repair phases and helper modules.

## Major State Groups

- Command and device state: filesystem name, file descriptors, external log/realtime names, file/device mode.
- Behavior flags: verbose, no-modify, dangerous repair, zap log, core dump, geometry assumptions, feature additions.
- Runtime buffers and direct I/O sizing.
- Repair status: primary superblock modified, bad inode btree, dirty filesystem, copied stripe unit.
- Required reconstruction flags: root inode, root `..`, metadata root inode, metadata `..`, realtime bitmap/summary inode.
- Superblock counter accumulation: inode counts, free blocks, realtime extents.
- Geometry-derived globals: inodes per block, AG count, chunk sizing, max symlink blocks.
- Parallel/progress state: report interval, progress counters, AG stride, thread count.
- Low-space behavior: `need_packed_btrees`.

## Quota Inode State

The file stores user/group/project quota inode numbers and per-type state:

- Unknown.
- Have.
- Lost.

Helpers provide mutation and queries:

- `set_quota_inode`
- `lose_quota_inode`
- `clear_quota_inode`
- `get_quota_inode`
- `is_quota_inode`
- `is_any_quota_inode`
- `lost_quota_inode`
- `has_quota_inode`

## Notes

`quotino_off` maps quota type to array slot and asserts on invalid types. This keeps the quota inode state compact and uniform across all repair phases.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/globals.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/globals.h -->
# File Research: sources/local-fs/xfsprogs/repair/globals.h

## Role

`globals.h` declares shared constants, global variables, and quota inode helpers for xfs_repair.

## Constants

- `XR_*` superblock and geometry error codes.
- Legal filesystem block-size log bounds.
- `NUM_AGH_SECTS`, the expected number of AG header sectors.
- `ORPHANAGE`, the lost+found directory name.
- `rounddown` utility macro.

## Global Declarations

The header exposes all shared state defined in `globals.c`, plus:

- `rt_lock`, used for legacy realtime extent map protection.
- `struct libxfs_init x`, the global libxfs initialization descriptor.
- Feature-upgrade booleans such as `add_bigtime`, `add_nrext64`, and `add_exchrange`.

## Quota API

Declares helpers to set, clear, lose, read, and test quota inode numbers.

## Interactions

Almost every file in this group includes `globals.h` because repair phases are coordinated through shared mode flags, feature flags, counters, and reconstruction markers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/globals.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/incore.c -->
# File Research: sources/local-fs/xfsprogs/repair/incore.c

## Role

`incore.c` implements repair’s in-memory block state maps for data AGs and rtgroups, plus the legacy realtime extent bitmap.

## Group Block Maps

Each AG or rtgroup has a `struct bmap`:

- Cacheline-aligned mutex.
- Btree root keyed by block offset.
- Values are pointers to static state integers.

The btree records state transitions rather than one entry per block, making large runs compact.

## State Updates

`set_bmap_ext` changes the state of a block range. It handles all boundary cases:

- Updating an entire existing extent.
- Splitting a range inside a larger extent.
- Merging with previous or next extents when states match.
- Inserting new transition points at start/end boundaries.

`get_bmap_ext` returns the state at a block and optionally the length of the same-state run up to a caller-provided maximum.

## Realtime Bitmap

For non-rtgroup filesystems, realtime extents use `rt_bmap`, a packed 4-bit-per-extent array. Helpers:

- `get_rtbmap`
- `set_rtbmap`
- `reset_rt_bmap`
- `init_rt_bmap`
- `free_rt_bmap`

`rtsb_init` marks the first realtime extent in use if a realtime superblock exists.

## Initialization and Reset

`reset_ag_bmaps` initializes each AG:

- AG header blocks as `XR_E_INUSE_FS`.
- Valid AG body as `XR_E_UNKNOWN`.
- Beyond-AG region as `XR_E_BAD_STATE`.

`reset_rtg_bmaps` initializes rtgroups:

- Realtime superblock area as filesystem metadata where applicable.
- Remaining valid rtgroup blocks as free.
- End sentinel as bad state.

`reset_bmaps` also marks an internal log as filesystem metadata.

`init_bmaps` allocates AG bmaps, rtgroup bmaps or legacy rt bitmap, and resets them. `free_bmaps` releases them.

## Concurrency

`lock_group` and `unlock_group` serialize access to a single AG or rtgroup map. Higher-level inode scanning locks the group while checking/updating ranges.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/incore.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/incore.h -->
# File Research: sources/local-fs/xfsprogs/repair/incore.h

## Role

`incore.h` defines repair’s in-memory state structures for block ownership, free extents, duplicate extents, inode records, parent tracking, link counts, file types, and bmap cursors.

## Block State API

Declares:

- `init_bmaps`, `reset_bmaps`, `free_bmaps`.
- `lock_group`, `unlock_group`, plus AG wrappers.
- `set_bmap_ext`, `get_bmap_ext`.
- `set_rtbmap`, `get_rtbmap`.

## Block State Values

`XR_E_*` states encode repair’s view of each block:

- Unknown, free, in-use, filesystem metadata, inode block, space-map block.
- Single-source variants from btree/rmap scans.
- Duplicate/multiple-use state.
- Refcount and CoW states.
- Bad-state sentinel.

`XR_E_METADATA` is deliberately below `XR_E_INUSE` because metadata-directory files are rebuilt and their blocks must become free-space candidates later.

## Extent Trees

Defines:

- `extent_tree_node_t` for AG free/duplicate extents.
- `rt_extent_tree_node_t` for realtime duplicate extents.
- APIs for bno trees, bcnt trees, duplicate extent trees, realtime duplicate extent trees, and counts.

Bno trees are sorted by start block. Bcnt trees are sorted by length with linked-list chaining for equal-sized extents.

## Inode Records

`ino_tree_node_t` tracks a 64-inode chunk:

- Start inode.
- Free mask and sparse mask.
- Confirmed mask.
- Directory mask.
- Reflink old/new masks.
- Metadata inode mask.
- Disk nlink counters.
- Parent list or extended data.
- Optional directory filetype array.
- Per-record mutex.

`INOS_PER_IREC` and `IREC_MASK` define bit granularity.

## Inode Tree API

Declares functions to:

- Allocate and free inode records.
- Find records by AG/inode or range.
- Set inodes used/free, including allocation of new records.
- Manage uncertain inode trees.
- Add extended inode data for phases 6 and 7.
- Track parent inode numbers and link counts.
- Track directory file types.

## Inline State Helpers

The header provides inline helpers for:

- Confirmed inode state.
- Directory bit.
- Free/used bit.
- Sparse bit.
- Reflink was/is bits.
- Metadata bit.
- Reference-checked and reached bits.
- Filetype access.

Many setters take the per-record mutex because AG processing can be parallel.

## Bmap Cursor

Defines `bmap_cursor_t` and `bm_level_state_t` for validating bmap btree traversal state, including sibling pointers and first/last keys per level.

## Inobt Helpers

`inorec_get_freecount` and `inorec_set_freecount` abstract old and sparse inode btree record formats.

`xfs_rootrec_inodes_inuse` returns how many initial inodes mkfs assumes allocated, varying by metadir and rtgroup support.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/incore.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/incore_bmc.c -->
# File Research: sources/local-fs/xfsprogs/repair/incore_bmc.c

## Role

`incore_bmc.c` initializes bmap btree cursors used during inode bmap btree validation.

## Function

`init_bm_cursor`:

- Clears the cursor.
- Sets inode to `NULLFSINO`.
- Records number of levels.
- Initializes every level’s block and sibling pointers to `NULLFSBLOCK`.
- Initializes first/last keys to `NULLFILEOFF`.

## Interactions

The cursor is used by bmap btree scanning code to validate key ordering, sibling pointers, and parent/child key consistency while processing inode data or attr forks.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/incore_bmc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/incore_ext.c -->
# File Research: sources/local-fs/xfsprogs/repair/incore_ext.c

## Role

`incore_ext.c` implements AVL/btree-backed extent tracking for duplicate extents and rebuilt free-space trees.

## Extent Structure

The file manages four structures:

- Per-AG duplicate extent btrees.
- Per-AG free extent bno AVL trees.
- Per-AG free extent bcnt AVL trees.
- A realtime duplicate extent AVL64 tree.

## Duplicate Extents

`add_dup_extent` inserts a per-AG duplicate block range into a btree keyed by start block, storing end block as value.

`search_dup_extent` tests whether a requested AG block range overlaps any duplicate extent. It checks the found range and previous range.

`release_dup_extent_tree` clears a per-AG duplicate tree after phase 4 has processed that AG.

## Free Extent Trees

`add_bno_extent`, `findfirst_bno_extent`, `find_bno_extent`, and `get_bno_extent` manage free extents sorted by starting block.

`add_bcnt_extent`, `findfirst_bcnt_extent`, `findbiggest_bcnt_extent`, `findnext_bcnt_extent`, and `get_bcnt_extent` manage free extents sorted by block count. Equal-sized extents are stored in an ordered linked list anchored by the AVL node.

The bcnt code swaps node contents in a few cases to preserve AVL anchor identity while inserting/removing entries from equal-size lists.

## Realtime Duplicate Extents

Realtime duplicate extents use 64-bit AVL keys because realtime extent numbers can exceed AG block widths.

`add_rt_dup_extent` merges overlapping or adjacent realtime duplicate ranges before insertion.

`search_rt_dup_extent` tests whether a realtime extent is in the duplicate tree.

`free_rt_dup_extent_tree` releases the realtime duplicate tree descriptor.

## Initialization and Teardown

`incore_ext_init` allocates all per-AG descriptor tables, initializes btrees and AVL trees, initializes locks, and initializes the realtime duplicate tree.

`incore_ext_teardown` destroys per-AG duplicate trees and frees bno/bcnt descriptor arrays. Realtime duplicate teardown is separate.

## Count Helpers

- `count_bno_extents_blocks`: counts bno extents and total blocks in an AG.
- `count_bno_extents`: counts bno extents.
- `count_bcnt_extents`: counts bcnt extents.

## Interactions

Phase 4 builds duplicate extent lists from the global block map, then inode scans query those lists to decide which inodes must be cleared. Phase 5 uses bno/bcnt free extent trees to rebuild allocation btrees.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/incore_ext.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/incore_ino.c -->
# File Research: sources/local-fs/xfsprogs/repair/incore_ino.c

## Role

`incore_ino.c` implements repair’s in-memory inode trees and uncertain-inode trees.

## Inode Tree Model

Each `ino_tree_node_t` represents one 64-inode chunk. The main inode tree stores confirmed inode chunks. The uncertain tree stores candidate chunks discovered from directory references before repair has confirmed whether they exist.

## Link Count Storage

The file uses dynamically growing arrays for disk and counted nlinks:

- Start with `uint8_t`.
- Grow to `uint16_t` when values exceed 255.
- Grow to `uint32_t` when values exceed 65535.

This saves memory for large filesystems where most nlink counts are small.

Functions:

- `add_inode_ref`
- `drop_inode_ref`
- `num_inode_references`
- `set_inode_disk_nlinks`
- `get_inode_disk_nlinks`

## Inode Record Allocation

`alloc_ino_node` initializes a chunk as all free and unconfirmed, allocates disk nlink storage, optional filetype storage, clears metadata/reflink/dir masks, and initializes a mutex.

`free_ino_tree_node` releases nlink arrays, extended data, parent arrays, filetypes, mutex, and the record.

## Uncertain Inodes

`add_aginode_uncertain` rounds the inode down to a 64-inode chunk, uses a per-AG last-record cache, creates a record if needed, and marks the candidate free or used.

`add_inode_uncertain` converts fs inode number to AG/in-AG form.

`get_uncertain_inode_rec`, `findfirst_uncertain_inode_rec`, `find_uncertain_inode_rec`, and `clear_uncertain_ino_cache` support phase 3 processing of newly discovered candidate inodes.

## Confirmed Inode Trees

`add_inode` creates and inserts a confirmed inode record.

`set_inode_used_alloc` and `set_inode_free_alloc` add a new chunk and mark a specific inode used or free.

`get_inode_rec` removes a record from the main inode tree.

`find_inode_rec_range` finds inode records overlapping a range.

`print_inode_list` and `print_uncertain_inode_list` are debugging utilities.

## Parent Tracking

`set_inode_parent` stores parent inode numbers in a packed `parent_list_t` indexed by bit position. It supports both the early-phase parent-list union field and the later extended-data parent list.

`get_inode_parent` returns a stored parent or zero.

## Extended Phase Data

`alloc_ex_data` converts a record from early parent-only data to full extended data:

- Preserves existing parent list.
- Allocates counted nlink storage matching current nlink width.
- Initializes reached/processed masks to zero.

`add_ino_ex_data` applies this to every confirmed inode record and sets `full_ino_ex_data`.

## Initialization

`incore_ino_init` allocates per-AG main and uncertain AVL trees, initializes them with inode-range operations, allocates the uncertain last-record cache, and starts with compact inode data mode.

## Interactions

- Phase 2 creates or marks root and metadata inode chunks.
- Phase 3 adds uncertain inodes from directory entries and confirms them after validation.
- Phase 6/7 use extended data for reachability, parent, and nlink validation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/incore_ino.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/init.c -->
# File Research: sources/local-fs/xfsprogs/repair/init.c

## Role

`init.c` initializes libxfs and process-level repair prerequisites.

## Main Flow

`xfs_init`:

- Clears and fills a `libxfs_init` descriptor from global command options.
- Configures data, log, and realtime device names.
- Chooses libxfs access flags:
  - read-only/inactive for no-modify,
  - dangerous inactive mode when requested,
  - exclusive mode by default,
  - direct I/O always,
  - buffer locking when prefetch is enabled.
- Falls back to dangerous inactive initialization only to emit a targeted read-only mounted filesystem error.
- Creates thread-specific keys for data and attr block maps.
- Raises file-size rlimit to infinity.
- Initializes prefetch tracing.
- Runs CRC32C and directory/attribute hash self-tests before examining the filesystem.

## Support Helpers

- `ts_create`: creates pthread keys for per-thread block-map caching.
- `increase_rlimit`: ensures repair can write large outputs/metadata without `RLIMIT_FSIZE` interference.

## Interactions

This file must run before phase processing because later code assumes libxfs devices, buffer cache behavior, thread-local block maps, and hash/CRC primitives are ready.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/init.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase1.c -->
# File Research: sources/local-fs/xfsprogs/repair/phase1.c

## Role

`phase1.c` implements xfs_repair phase 1: find, verify, and possibly repair the primary superblock.

## Main Flow

`phase1`:

- Logs phase start.
- Resets global repair-needed flags for root, metadir, realtime metadata, and quotas.
- Reads the primary superblock into an aligned AG buffer.
- If the primary superblock is unreadable or invalid, searches for a valid secondary superblock.
- Verifies and sets primary superblock geometry.
- Repairs `features2` versus `bad_features2` mismatch.
- Applies lazy counter conversion requests.
- Clears nonzero `shared_vn`.
- Writes the modified primary superblock unless in no-modify mode.
- Resets accumulated superblock counters.

## Helpers

- `alloc_ag_buf`: aligned AG header buffer allocation.
- `no_sb`: fatal path when no valid secondary superblock can be found.

## Repair Model

Phase 1 only repairs the superblock enough to let later phases mount libxfs geometry and scan the filesystem. Feature conversions are applied after superblock verification so subsequent phases operate against the intended feature set.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase1.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase2.c -->
# File Research: sources/local-fs/xfsprogs/repair/phase2.c

## Role

`phase2.c` implements phase 2: set up libxfs buffer-cache use, handle the log, scan AG freespace and inode maps, ensure root/metadata inode chunks exist, discover metadata inodes, and apply requested feature upgrades.

## Log Handling

`zero_log` initializes log structures, finds log head/tail, and enforces safe behavior:

- If log head/tail cannot be found, repair exits unless no-modify or explicit log zap allows proceeding.
- If the log contains unreplayed metadata, repair requires mounting to replay it unless `-L` or no-modify is used.
- If `zap_log` is set and modification is allowed, clears the log.
- Seeds `libxfs_max_lsn` for v5 filesystems.

The dummy `xlog_recover_do_trans` disables transaction replay in repair context.

## Feature Upgrade Helpers

The file supports adding:

- Inode btree counts.
- Bigtime timestamps.
- Nrext64 extent counters.
- Exchange-range support.

Each helper validates prerequisite features and exits cleanly when the feature already exists or cannot be added.

`install_new_geometry` temporarily installs the upgraded superblock to validate minimum log size and root inode location, then restores and reinstalls state cleanly.

The free-space upgrade check scaffolding exists, but `need_check_fs_free_space` currently returns false.

`upgrade_filesystem` writes the upgraded primary superblock immediately when modifying, setting `features_changed`.

## Phase 2 Flow

`phase2`:

- Calls `set_mp` so buffer cache routines can operate.
- Logs whether the filesystem uses an internal or external log.
- Retains the primary superblock buffer if writeback hooks require it.
- Processes the log.
- Scans AG freespace and inode maps via `scan_ags`.
- Ensures the root inode chunk exists in the in-core inode tree.
- Marks root, metadir root, realtime bitmap, and realtime summary inodes used/metadata as appropriate.
- Marks corresponding inode blocks in the block map if the chunk had to be synthesized.
- Discovers rtgroup metadata inodes.
- Discovers quota inodes for metadir quota filesystems.
- Applies feature upgrades.

## Interactions

Phase 2 seeds the in-core inode map and block map that `dinode.c`, `dir2.c`, and phase 4 rely on. It is the point where superblock-level feature additions are made durable before later rebuild work.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase3.c -->
# File Research: sources/local-fs/xfsprogs/repair/phase3.c

## Role

`phase3.c` implements phase 3: clear unlinked inode lists, verify uncertain inodes, process known inodes, and perform inode discovery through directories.

## AGI Unlinked Cleanup

`process_agi_unlinked` reads each AGI and clears all `agi_unlinked` buckets when modifying. This is delayed until phase 3 because inode clearing must not lose information before unlinked lists are examined.

## Known Inode Processing

`process_ag_func` waits for inode prefetch, then calls:

`process_aginodes(..., check_dirs=1, check_dups=0, extra_attr_check=1)`

This means phase 3 performs directory processing, inode discovery, and attribute semantic checks, but does not run duplicate-block checking.

`process_ags` runs this through the inode prefetch framework.

## Uncertain Inode Processing

`do_uncertain_aginodes` processes one AG’s uncertain inode records and returns how many new uncertain inodes were found.

`phase3` loops over all AGs until no uncertain inodes remain. This handles directory entries that point to inodes not present in the initial inode btrees.

## Phase Flow

`phase3`:

- Logs phase start and whether unlinked lists will be cleared.
- Checks realtime superblock metadata when applicable.
- Clears AGI unlinked lists if modifying.
- Checks uncertain inode records found before phase 3.
- Processes all known inodes with directory discovery enabled.
- Repeatedly processes newly discovered inodes in parallel until the uncertain sets are empty.

## Interactions

Phase 3 is where `dir2.c` and `dinode.c` cooperate most directly: directory entries can add uncertain inodes, and those inodes are then validated by `process_uncertain_aginodes`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase3.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase4.c -->
# File Research: sources/local-fs/xfsprogs/repair/phase4.c

## Role

`phase4.c` implements phase 4: detect duplicate block claims, reprocess inodes against duplicate extent lists, collect rmap/refcount data, validate quota inode pointers, and check realtime metadata before rebuild.

## Duplicate Extent Setup

`process_dup_extents` walks the in-core block map for one AG or rtgroup and:

- Warns about free space seen by only one freespace btree in no-modify mode.
- Adds `XR_E_MULT` data-device ranges to the per-AG duplicate extent tree.
- Ignores duplicate rtgroup extents because no later search consumes them.
- Warns on unknown/bad block states.

`process_dup_rt_extents` scans the legacy realtime extent bitmap and builds merged duplicate realtime extent ranges.

## Inode Reprocessing

Phase 4 resets all bmaps, then calls inode processing with:

`process_aginodes(..., check_dirs=0, check_dups=1, extra_attr_check=0)`

This gives each inode a two-pass duplicate check:

- First pass checks whether the inode overlaps known duplicate extents.
- If corrupt, the inode/fork can be cleared.
- If clean, the second pass updates block ownership maps.

Directory and attr semantic checks are disabled because phase 3 already handled them.

## Root and Metadata Root Checks

Before duplicate processing, phase 4 checks whether the root inode and metadir root inode are free or not directories. If so, it sets global reconstruction flags and reports loss.

## Rmap and Refcount Processing

When rmap work is needed, `collect_rmaps` is enabled before inode reprocessing. `process_rmap_data` then:

- Adds fixed AG/rtgroup rmap records.
- Verifies rmap btrees.
- Computes data and realtime refcount records when reflink is enabled.
- Fixes inode reflink flags.
- Checks refcount btrees.

## Quota Superblock Validation

`quotino_check` verifies that remembered quota inode numbers are valid, present in the inode tree, and not free. Missing quota inodes are marked lost.

`quota_sb_check` reconciles quota feature state:

- For metadir filesystems, discovered quota inodes can preserve or enable quota feature state.
- For older layouts, losing all quota inodes downgrades quota state; valid quota inode triplets enable it.

## Realtime Metadata

If realtime blocks exist, phase 4 calls `check_rtmetadata` after duplicate processing to generate/check realtime summary and bitmap information before later rebuild phases.

## Memory Lifecycle

After inode duplicate processing, phase 4 frees realtime duplicate extent tracking and per-AG duplicate extent trees as AG work completes.

## Interactions

Phase 4 is the bridge between inode scans and allocation metadata rebuild. It converts block ownership conflicts into duplicate extent lists, lets inode repair remove bad claimants, and then produces a clean block state map for later freespace reconstruction.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/phase4.c -->