# Group Research: group_630_jfsutils_sources_local_fs_jfsutils_fsck_fsckimap_c_sources_local_fs__ae96f9224bfa

Scope: `Docs/research_subset_a.md` includes `sources/local-fs/jfsutils`. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckimap.c -->
# File Research: sources/local-fs/jfsutils/fsck/fsckimap.c

## Purpose
Implements JFS fsck inode allocation map handling. It records and duplicate-checks inode extents, validates or rebuilds aggregate/fileset inode allocation maps, checks and repairs redundant primary/secondary aggregate inode structures, and contains a small append-only xtree builder used when rebuilding the secondary fileset inode map.

## Main Elements
- Workspace structures:
  - `struct fsck_iag_info` bundles the current IAG, inode-map control page, fsck imap/IAG/AG workspace tables, aggregate-vs-fileset ownership, and message context.
  - `struct xtree_buf` and static `fsim_node_pages` track rightmost xtree pages while reconstructing a fileset inode map tree.
- Free-list scanning and validation:
  - `iagfr_list_scan()` / `iagfr_list_validation()` validate the imap free-IAG list.
  - `agfrino_lists_scan()` / `agfrino_lists_validation()` validate per-AG free-inode IAG lists.
  - `agfrext_lists_scan()` / `agfrext_lists_validation()` validate per-AG free-extent IAG lists.
- Redundant aggregate inode structure checking:
  - `AIS_redundancy_check()` compares the primary and secondary aggregate inode tables and then compares the secondary aggregate inode map.
  - `AIS_inode_check()` compares special aggregate inode fields, timestamps, EA descriptor, and optional rooted tree bytes.
  - `AIM_check()` compares the primary aggregate inode map with the secondary aggregate inode map extent named by `s_aim2` and the secondary AIT root.
  - `FSIM_check()` compares primary/secondary fileset inode map leaf nodes, including non-inline leaf chains.
  - `IM_compare_leaf()` compares inode-map leaf XAD offsets, addresses, lengths, and node header fields.
- Redundant aggregate inode structure repair:
  - `AIS_replication()` rebuilds the target AIT from whichever primary/secondary table was selected as source for each part.
  - `AIS_inode_replication()` copies one source dinode to the target and adjusts `di_ixpxd` for the primary-vs-secondary table location.
  - `AIM_replication()` copies one AIM image to the other and adjusts the target root XAD and IAG `inoext[0]`.
  - `FSIM_replication()` rebuilds an independent target fileset inode-map xtree whose leaves reference the same control/IAG extents as the source.
  - `FSIM_add_extents()`, `xtAppend()`, `xtSplitPage()`, and `xtSplitRoot()` append source leaf extents into the rebuilt target xtree.
- Inode extent recording:
  - `record_imap_info()` records first-leaf offsets and root-leaf status for aggregate and fileset imaps.
  - `record_dupchk_inode_extents()` records inode extents for aggregate and fileset IAGs.
  - `record_dupchk_inoexts()` walks every allocated `inoext[]` PXD, calls `process_extent(..., FSCK_RECORD_DUPCHECK)`, and either clears corrupt inode extents in read-write mode or reports unrecoverable corruption in read-only mode.
  - `first_ref_check_inode_extents()` and `first_refchk_inoexts()` query inode extents for unresolved first references to duplicate-allocated blocks.
- IAG map rebuild/verify:
  - `iag_alloc_scan()` builds fsck truth maps (`amap`, `fextsumm`, `finosumm`) from inode records and existing IAG extent slots.
  - `iag_alloc_rebuild()` writes rebuilt pmap/wmap/summary maps, free counts, and forward list links into an IAG.
  - `iag_alloc_ver()` compares on-disk IAG maps, counts, and list membership against fsck truth.
  - `iags_rebuild()` / `iags_validation()` process all IAGs for one imap.
  - `iamap_rebuild()` / `iamap_validation()` rebuild or verify the imap control page and all IAG/list state.
  - `rebuild_agg_iamap()`, `rebuild_fs_iamaps()`, `verify_agg_iamap()`, and `verify_fs_iamaps()` are the public aggregate/fileset entry points.

## Control Flow
Early fsck phases call `record_dupchk_inode_extents()`, which first calls `record_imap_info()` so later `inode_get()`/`iag_get()` operations know where the imap leaf data begins. It then records aggregate inode-table extents and fileset inode-table extents through `record_dupchk_inoexts()`.

In read-only verification, `verify_agg_iamap()` and `verify_fs_iamaps()` fetch the imap control page and call `iamap_validation()`. That path scans free lists, builds expected IAG maps from fsck inode records, compares every IAG, validates remaining list counts, and finally checks imap control-page counters.

In read-write repair, `rebuild_agg_iamap()` and `rebuild_fs_iamaps()` call `iamap_rebuild()`. It resets control lists/counters, scans all IAGs, writes rebuilt maps and forward list links, makes a second pass to fill backward links, then writes the control page.

Redundant AIT/AIM handling is separate. `AIS_redundancy_check()` is the read-only consistency path. `AIS_replication()` is the repair path; it may use different primary/secondary sources for the filesystem inode map and the other special aggregate inodes, writes target extents with endian swapping, and updates `JFS_BAD_SAIT` when secondary replication fails.

## Dependencies And Integration
The file depends on global `sb_ptr`, `agg_recptr`, and `Vol_Label`; low-level device I/O (`readwrite_device()`, `ujfs_rw_diskblocks()`); inode/IAG access (`inode_get()`, `iag_get()`, `iag_put()`, `iag_get_first()`, `iag_get_next()`, `inotbl_get_ctl_page()`, `inotbl_put_ctl_page()`); xtree traversal (`find_first_leaf()`, `xTree_processing()`, `init_xtree_root()`); block allocation/recording (`process_extent()`, `extent_unrecord()`, `fsck_alloc_fsblks()`); workspace allocation; endian helpers; and fsck message emission.

Primary external callers are declared in `xfsckint.h` and used by `fsckmeta.c` and `xchkdsk.c`: redundancy checking in metadata verification, inode-extent recording in early block ownership passes, and imap rebuild/verification plus AIT replication in later repair/verify phases.

## Behavioral Notes
The code assumes classic JFS release-1 layout details in several places: one fileset, special aggregate inodes in the first AIT extent, and a small aggregate inode map with one IAG/root-leaf representation.

`iag_alloc_scan()` is not purely observational in read-write mode: if an inode extent is backed but none of its inodes remain allocated, it unrecords the extent, clears the IAG PXD, and reduces the backed extent count.

Secondary-repair failures are treated differently from primary-repair failures. Failure to repair the primary AIT/AIM marks the aggregate dirty; failure to repair the secondary structure warns and sets `JFS_BAD_SAIT` so future maintenance avoids trusting the flawed secondary copy.

## Risk Notes
This file is high-risk repair code because it translates fsck’s workspace truth back into allocation metadata. Incorrect IAG counts, list membership, source/target AIT selection, or extent clearing can orphan inode ranges or make allocation maps disagree with real inode usage.

Notable fragile points include endian swap boundaries around AIT writes, the positive/negative “remaining list length” validation convention, append-only xtree reconstruction for FSIM replication, and interaction between `primary_ait_4part1`/`primary_ait_4part2`.

Two apparent copy/paste hazards stand out from the implementation: `AIS_inode_check()` computes `secondary_root` from `primary_inoptr` rather than `secondary_inoptr`, so tree-byte comparison can compare the primary root with itself; and `agfrext_lists_validation()` gates free-extent validation on `frino_list_bad` rather than `frext_list_bad`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckimap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckino.c -->
# File Research: sources/local-fs/jfsutils/fsck/fsckino.c

## Purpose
Implements per-fileset-inode fsck validation and repair helpers. It validates EA, ACL, file data, directory data, inline inode storage layout, inode sizes and block counts; records/unrecords valid inode-owned extents; releases bad inodes; clears corrupt EA/ACL descriptors; checks duplicate-allocation first references; and builds/display paths for inode diagnostics.

## Main Elements
- EA/ACL cleanup:
  - `backout_EA()` and `backout_ACL()` unrecord out-of-line EA/ACL extents from fsck workspace maps and decrement inode/fileset running totals.
  - `clear_EA_field()` and `clear_ACL_field()` unrecord eligible EA/ACL extents, update block counters, and zero descriptor length/address fields.
- Path reporting:
  - `get_path()` walks upward from an inode and parent directory by repeatedly calling `direntry_get_objnam()`, converting Unicode names to UTF-8, and assembling a path backward in `agg_recptr->path_buffer`.
  - `display_path()` emits type-specific path messages and distinguishes expected vs illegal hard-link parents for directories.
  - `display_paths()` emits all observed paths, using parent extension records when multiple parents were recorded.
- Duplicate-allocation first-reference queries:
  - `first_ref_check_inode()` queries EA, ACL, and validated data extents with `process_extent(..., FSCK_QUERY)` or valid-data helpers.
- Inline layout and inode identity:
  - `in_inode_data_check()` verifies that inline data, inline EA, and inline ACL descriptions do not overlap inode storage.
  - `inode_is_in_use()` checks inode stamp, number, fileset, inode-table PXD, and nonzero link count.
  - `parent_count()` counts the primary parent plus parent extension records.
- Valid-inode recording:
  - `record_valid_inode()` records already-validated EA/ACL extents and data extents.
  - `unrecord_valid_inode()` reverses recording for EA/ACL and directory/file data.
  - `release_inode()` sets `di_nlink` to zero on disk and unrecords valid blocks when they are trusted.
- Descriptor/data validation:
  - `validate_EA()` validates EA DXD flags, inline bounds, extent size bounds, extent allocation, reads out-of-line EA data when small enough, and validates FEALIST format via `jfs_ValidateFEAList()`.
  - `validate_ACL()` validates ACL DXD flags and inline/extent bounds, then records extent-backed ACL blocks.
  - `validate_data()` validates non-directory regular-file/symlink data rooted in an xtree, with special handling for short inline symlinks.
  - `validate_dir_data()` validates directory dTree data and, when directory indexing is enabled, the directory table xtree; it schedules index-table rebuild when the xtree is bad but the dTree can still be used.
  - `validate_record_fileset_inode()` is the main orchestrator for one in-use fileset inode.

## Control Flow
The normal per-inode path is `inode_is_in_use()` followed by `validate_record_fileset_inode()`. The validator creates or fetches the fsck inode record, marks it in use, classifies the inode type, subtracts the on-disk link count from the fsck link-count accumulator, then validates EA, ACL, and object data.

For regular files and long symlinks, `validate_data()` checks that `di_dxd` is an xtree root and calls `xTree_processing(..., FSCK_RECORD_DUPCHECK)`. If the tree is corrupt, it marks the inode for release, backs out recorded tree/EA/ACL extents when possible, and uses fatal metadata return codes for metadata inodes.

For directories, `validate_dir_data()` first handles optional directory-index xtree validation, then runs `dTree_processing(..., FSCK_RECORD_DUPCHECK)`. If dTree validation fails, it unre records dTree extents and backs out EA/ACL extents. If the directory index tree is bad but the dTree is usable, it clears index checking, marks `rebuild_dirtable`, unre records the directory-table xtree, and fixes `di_nblocks` to the observed valid block count.

After structure validation, `validate_record_fileset_inode()` checks `di_nblocks` against `agg_recptr->this_inode.all_blks`, checks non-directory byte size against allocated data capacity, verifies inline storage overlap, schedules INLINEEA mode-bit corrections, and updates global EA/ACL/file/directory block totals for keepers.

## Dependencies And Integration
The file depends on `xfsckint.h`, JFS byte-order and Unicode helpers, globals `sb_ptr`, `agg_recptr`, `Uni_Name`, and `Str_Name`; extent processing (`process_extent()`, `extent_record()`); data processors (`process_valid_data()`, `process_valid_dir_data()`, `xTree_processing()`, `dTree_processing()`); EA I/O and validation (`ea_get()`, `jfs_ValidateFEAList()`); inode access (`inode_get()`, `inode_put()`, `get_inorecptr()`); directory lookup (`direntry_get_objnam()`); and fsck message emission.

External callers include `xchkdsk.c` for the main fileset inode scan, path reporting, first-reference checks, inode release, and EA/ACL clearing. `fsckmeta.c` also uses the valid-inode record/unrecord and first-reference helpers for metadata inode handling.

## Behavioral Notes
EA and ACL extent blocks count toward inode/fileset allocation totals but are excluded from file/directory object data totals. Short symlinks are treated as inline data with an extra null terminator not counted in `di_size`.

Directories are not subjected to the same `di_size` capacity check used for regular files and symlinks. Directory consistency is driven primarily by dTree validation and directory-index handling.

`validate_dir_data()` forcibly sets `DXD_INDEX` on directory data roots as a workaround for an older bug that could clear the bit. This mutates the in-memory inode before checking the root flags.

`clear_EA_field()` clears the EA flag to zero, while `clear_ACL_field()` sets the ACL flag to `DXD_CORRUPT` with zero length/address. That asymmetry is visible in the code and matters to later repair interpretation.

## Risk Notes
The highest-risk behavior is counter and block-map rollback after late validation failure. If a tree appears valid until a block-count or size check fails, the code must unrecord EA, ACL, and data extents in the same shape they were recorded.

The tree-corruption rollback paths back out ACL only inside the `!ignore_ea_blks` branch, so EA/ACL ignore-state combinations are delicate. Directory-index rebuild handling is also fragile because it temporarily restores `ignore_alloc_blks` to the xtree result before unrecording directory-table extents.

Path construction depends on parent records and directory entries still being usable; disconnected or selected-for-release parents intentionally produce partial paths rather than rooted paths.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/fsck/fsckino.c -->