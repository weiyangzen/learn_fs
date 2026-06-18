# Group Research: group_632_jfsutils_sources_local_fs_jfsutils_fsck_fsckwsp_c_sources_local_fs_j_3ed202e4a5ad

Scope: `Docs/research_subset_a`

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckwsp.c -->
# File Research: sources/local-fs/jfsutils/fsck/fsckwsp.c

## Purpose
Implements the main in-memory and on-device workspace services used by `jfs_fsck`: dynamic workspace allocation, fsck block-ownership bitmap management, duplicate-block tracking, inode-record lookup tables, temporary buffers, tree queues, service-log buffers, and cleanup.

## Key Elements
Provides a custom arena-style allocator through `alloc_wrksp()` and `alloc_wsp_extent()`. Workspace extents are linked from `agg_recptr->wsp_extent_list`, rounded to 8-byte alignment, zero-initialized, and tagged for normal fsck use or `logredo` use. `release_logredo_allocs()` rewinds only logredo-tagged extents, and `workspace_release()` frees the very-large buffer plus all allocated workspace extents.

Manages the fsck block map through `establish_wsp_block_map_ctl()`, `establish_wsp_block_map()`, `blkall_increment_owners()`, `blkall_mark_free()`, `extent_record_dupchk()`, `extent_unrecord()`, and `process_extent()`. The block map is either backed by the aggregate’s reserved fsck workspace when write access is available or by dynamic storage in read-only mode. `process_extent()` bounds-checks extents against valid metadata/fileset block ranges and marks owning inode records for repair when extents are impossible or clipped.

Tracks multiply allocated blocks with a sorted doubly linked list of `struct dupall_blkrec`. `dupall_insert_blkrec()`, `dupall_find_blkrec()`, `blkall_split_blkrec()`, `extent_1stref_chk()`, and `extent_record_dupchk()` maintain duplicate ranges, owner counts, and unresolved first-reference counts. Inodes involved in unresolved duplicates are flagged for release or EA/ACL field clearing depending on where the bad extent came from.

Builds inode workspace structures for aggregate and fileset inodes. `establish_agg_workspace()` creates the aggregate inode map/table assumptions for release-1 JFS. `establish_fs_workspace()` reads the selected AIT extent, derives fileset IAG count, allocates fileset inode maps/tables, and sets up the initial root metadata record tables. `get_inorecptr()`, `inorec_agg_search_insert()`, `inorec_fs_search_insert()`, `get_inorecptr_first()`, and `get_inorecptr_next()` provide random and sequential inode-record access.

Also owns reusable queues/buffers: `treeQ_*` for xtree breadth-first traversal, `dtreeQ_*` for directory-tree processing, directory reconstruction buffers from the very-large buffer, EA buffer setup, temporary inode/node buffers, and fsck service-log lifecycle via `fscklog_start()`, `fscklog_init()`, and `fscklog_end()`.

## Dependencies
Uses global `sb_ptr`, `agg_recptr`, and `bmap_recptr` from `xchkdsk.c`; message emission from `message.h`; disk I/O helpers such as `ujfs_rw_diskblocks()`; endian conversion for fsck block-map pages; inode/AIT helpers such as `inode_get()` and `ait_special_read_ext1()`; and many constants/types from `xfsckint.h`.

## Behavior/Risks
The file is a central state manager. Most routines mutate global aggregate state rather than returning rich objects, so callers depend on side effects such as `corrections_needed`, `ignore_alloc_blks`, `selected_to_rls`, `dup_block_count`, and `unresolved_1stref_count`.

Duplicate-block handling is range-based but backed by a one-bit “already owned” block map plus a separate duplicate list for owner counts above one. Any boundary mistake in splitting duplicate records can affect later owner decrements and first-reference resolution.

`fsck_alloc_fsblks()` searches the workspace map page by page for contiguous free blocks, then records the chosen extent as allocated. It rejects allocations that would start in the reserved fsck workspace by comparing against `highest_valid_fset_datablk`.

The very-large buffer is deliberately reused for different phases (`EA`, directory buffers, inode extents), so correctness depends on phase ordering and `vlarge_current_use` discipline rather than independent ownership.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckwsp.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckxtre.c -->
# File Research: sources/local-fs/jfsutils/fsck/fsckxtre.c

## Purpose
Validates, searches, initializes, and accounts for JFS xtrees, the B+ tree format used for file data extents and some inode-rooted metadata. It connects tree structural validation with fsck’s block ownership and inode repair flags.

## Key Elements
`find_first_leaf()` descends from an inode’s xtree root to locate the leftmost leaf node, returning whether the data is root-leaf or inline/no-data. `init_xtree_root()` resets an inode’s xtree root to an empty root leaf and clears `di_nblocks`/`di_size`.

`process_valid_data()` walks an already validated xtree by level and sibling chain, calling `process_extent()` on each XAD and updating aggregate/inode block accounting. It supports record, unrecord, and query modes.

`xTree_processing()` is the main validator. It validates root header fields, normalizes fileset-inode-map action variants, detects dense-file front gaps, processes root leaf/internal nodes, then uses the `treeQ_*` queue from `fsckwsp.c` for breadth-first traversal of child nodes. It checks node level transitions, sibling forward/backward links, `header.self` against the parent XAD PXD, empty non-root nodes, valid leaf/internal flags, and consistency of corruption detection across later passes.

`xTree_process_internal_extents()` validates internal-node XAD flags and ascending keys, records each child-node extent through `process_extent()`, updates non-data block counts, and enqueues child nodes with their expected address, length, level, and first key.

`xTree_process_leaf_extents()` validates leaf XAD flags, ascending keys, dense-file gaps, odd-sized extents, and records/unrecords/query-checks data extents. It updates `this_inode.data_size`, `all_blks`, `data_blks`, and fileset block counts. Odd-sized extents are allowed only as the last possible extent, except for the bad-block inode.

`xTree_search()` descends the xtree to find a leaf XAD covering a requested file offset. It uses `xTree_binsrch_page()` to select the nearest XAD in each page and then either descends or checks whether the selected leaf extent covers the key.

## Dependencies
Depends on `xfsckint.h` xtree/XAD/PXD types and macros, `jfs_byteorder.h`, global `sb_ptr` and `agg_recptr`, `node_get()`, `treeQ_*` workspace queue routines, `process_extent()`, and fsck message helpers.

## Behavior/Risks
The validator is intentionally fail-fast: once structural corruption is detected, it sets `inorecptr->ignore_alloc_blks` and stops processing further allocations for that tree. Repair decisions elsewhere use this flag to release an inode, skip suspect allocation accounting, or keep later passes consistent.

Dense files are required to have contiguous leaf offsets, while sparse files only require strictly increasing non-overlapping keys. The code treats directory data roots specially by using `di_dirtable`; other inodes use `di_btroot`.

Fileset inode-map xtrees use special action aliases and skip leaf extent processing for that metadata tree, while still validating internal node storage. This distinction is important because callers can request FSIM-specific record/unrecord/query operations.

The traversal assumes the queue and node buffers are globally shared workspace resources. Corruption paths clean up pending queue elements before returning, but the code relies on `treeQ_back/front` being reset correctly between validations.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckxtre.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/xchkdsk.c -->
# File Research: sources/local-fs/jfsutils/fsck/xchkdsk.c

## Purpose
Implements the `jfs_fsck` program entry point and top-level phase orchestration. It owns global fsck state, parses command-line options, opens and validates the target aggregate, coordinates journal replay, runs phases 0-9, performs approved repairs, emits summaries, flushes modified metadata, and exits with fsck-compatible status codes.

## Key Elements
Defines global process state used across fsck modules: superblock buffer `sb_ptr`, aggregate record `agg_recptr`, block-map record `bmap_recptr`, volume/program names, directory Unicode scratch buffers, device I/O handle, block sizes, log device path, lost+found Unicode names, and dynamic-storage error context.

`main()` initializes global records, allocates the very-large buffer, runs `initial_processing()`, starts the heartbeat, executes phases 0 through 9 unless early completion is requested, performs final processing and buffer flushes, records end time/return code in the fsck workspace control page, marks the aggregate clean or dirty, ends service logging, releases workspace, closes the volume, and returns `exit_value`.

`initial_processing()` starts the fsck service log, parses options, checks mount status, verifies parameters, opens the volume, validates/repairs the superblock, computes aggregate layout fields from the superblock, initializes alternating fsck service-log regions, and establishes valid fileset data block bounds. `parse_parms()` supports `-a`, `-p`, `-r`, `-f`, `-j`, `-n`, `-o`/`--omit_journal_replay`, `--replay_journal_only`, `-d`, `-v`, `-V`, and `-y`. `verify_parms()` resolves option interactions and selects message level.

The phase functions define the high-level checker pipeline:
- Phase 0 replays the journal unless omitted, handles clean-if-dirty/autocheck early exit, and releases logredo workspace.
- Phase 1 initializes I/O/workspace, records fixed metadata, selects and validates AIT, builds fileset workspace, validates metadata and fileset inodes, records block ownership, and detects fatal duplicate metadata allocations.
- Phase 2 checks directory integrity and link counts.
- Phase 3 resolves first references for duplicate blocks and validates parent relationships.
- Phase 4 reports inode problems and decides approved repairs.
- Phase 5 checks connectedness when write access is available.
- Phase 6 marks the filesystem dirty, resolves/creates `/lost+found`, allocates directory buffers, performs inode repairs, and reconnects orphaned inodes.
- Phase 7 rebuilds or verifies inode allocation maps/tables and replicates aggregate inode structures.
- Phase 8 rebuilds or verifies the aggregate block allocation map.
- Phase 9 reformats the journal if log replay failed and write access is available.

`check_parents_and_first_refs()` traverses fileset inode records, resolves duplicate-block first references, detects unallocated inodes referenced by directories, finds missing parent links, flags directory hard-link cases, and marks incorrect directory parent inode numbers for repair.

`report_problems_setup_repairs()` walks flagged inode records, displays paths, reports selected releases, corrupt data trees, duplicate claims, EA/ACL issues, inline EA flag fixes, bad directory entries, and directory index rebuilds. In read-write mode it approves implied repairs such as parent directory adjustment; in read-only mode it clears repair flags and marks the aggregate dirty where appropriate.

`repair_fs_inodes()` applies approved inode-level repairs: releases bad inodes, adjusts link counts, corrects directory parents, clears EA/ACL fields, toggles inline EA bits, rebuilds directory indexes, removes bad directory entries, and writes modified inodes.

`resolve_lost_and_found()` and `create_lost_and_found()` locate, validate, or create `/lost+found` for reconnect processing. They ensure the target is an in-use directory without unresolved dangerous duplicate claims, initialize a spare inode if needed, add the root directory entry, and set aggregate reconnect state.

`final_processing()` reports aggregate block discrepancies and usage summaries, updates external-log device information, replicates the superblock in read-write mode, and emits standard capacity/inode/directory/file/EA/ACL/free-space messages.

## Dependencies
Depends on most fsck subsystems: workspace allocation and block-map routines, inode validation/repair, directory checking and reconnect code, aggregate/fileset inode-map rebuild/verify code, block allocation map rebuild/verify code, superblock validation/replication, journal replay (`jfs_logredo`), journal formatting (`jfs_logform`), message/logging code, device open/close/mount helpers, Unicode helpers, and JFS on-disk structure macros.

## Behavior/Risks
The checker is global-state driven. Phase functions mainly coordinate subsystem calls and mutate `agg_recptr` flags such as `fsck_is_done`, `processing_readonly`, `processing_readwrite`, `corrections_needed`, `corrections_approved`, `ag_dirty`, and `ag_modified`.

Read-only mode is not just a file-open mode; it changes phase behavior, disables repair approval, may skip journal replay depending on options, and converts would-be fixes into dirty/error reporting.

The repair phase deliberately marks the superblock dirty before applying changes, then later final processing and `agg_clean_or_dirty()` decide whether the aggregate can be marked clean. Interrupted repair therefore leaves an intentionally unmountable/dirty filesystem.

Mount checking can ask the user to continue for mounted or non-JFS-mounted devices unless the selected mode allows read-only reporting. `-r` and `-y` are compatibility options rather than distinct interactive behavior.

There is a suspicious reserved-space calculation in `final_processing()` using `kbytes_total - -kbytes_for_dirs ...`, which should be reviewed before relying on the reported reserved-kilobyte summary.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/xchkdsk.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/xchkdsk.h -->
# File Research: sources/local-fs/jfsutils/fsck/xchkdsk.h

## Purpose
Defines option-index constants used by `jfs_fsck` to record parsed command-line behavior in `agg_recptr->parm_options`.

## Key Elements
Contains include guards and a single `enum xchkdsk_options` with entries for check levels, if-dirty/autocheck behavior, verbosity/debug, clear-bad-block-list support, diagnostic block/inode/filename options, and the total `UFS_CHKDSK_OPTIONS` count.

The active users in this group are `xchkdsk.c` option parsing and verification routines, which set and inspect values such as `UFS_CHKDSK_LEVEL0`, `UFS_CHKDSK_LEVEL2`, `UFS_CHKDSK_LEVEL3`, `UFS_CHKDSK_IFDIRTY`, `UFS_CHKDSK_VERBOSE`, `UFS_CHKDSK_DEBUG`, `UFS_CHKDSK_CLRBDBLKLST`, and `UFS_CHKDSK_SKIPLOGREDO`.

## Dependencies
No external includes. The enum values are consumed by fsck aggregate-record option arrays declared in the internal fsck headers.

## Behavior/Risks
The enum order is part of the implicit ABI between option parsing and the aggregate record’s fixed-size option array. Adding or reordering entries would require checking all `parm_options[...]` indexing sites.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/xchkdsk.h -->