# Group Research: group_457_gfs2_utils_sources_local_fs_gfs2_utils_gfs2_fsck_initialize_c_source_bcf01597a2df

Scope: `Docs/research_subset_a.md` includes `sources/local-fs/gfs2-utils`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/initialize.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/initialize.c

## Purpose
Bootstraps `fsck.gfs2` against a target device. It opens the device safely, reads or repairs the superblock, blocks concurrent mounters when safe, initializes resource groups and system inodes, replays journals, checks resource group integrity, and tears down global fsck state.

## Main Elements
- `block_mounters()`: rewrites the superblock lock protocol prefix between `lock_` and `fsck_` to discourage mounting while fsck runs.
- Tree cleanup helpers: `dup_free()`, `dirtree_free()`, `inodetree_free()`, and `empty_super_block()`.
- `set_block_ranges()`: derives `first_data_block`, `last_data_block`, `last_fs_block`, and verifies the highest block can be read.
- `check_rgrp_integrity()` / `check_rgrps_integrity()`: recompute resource-group bitmap counts, optionally reclaim unlinked dinodes, and repair `rt_free`.
- `rebuild_sysdir()`: rebuilds the master system directory and reconnects or recreates `jindex`, `per_node`, `inum`, `statfs`, `rindex`, and `quota`.
- `lookup_per_node()`: finds or later rebuilds the `per_node` directory.
- `read_rgrps()`, `fetch_rgrps_level()`, `fetch_rgrps()`: read and validate the rindex/resource group set across escalating trust/rebuild levels.
- `init_system_inodes()`: loads root, inum, statfs, quota, per_node, and computes filesystem boundaries.
- Superblock repair path: `find_rgs_for_bsize()`, `peruse_metadata()`, `peruse_system_dinode()`, `peruse_user_dinode()`, and `sb_repair()`.
- `initialize()`: top-level setup called by `main.c`.
- `destroy()`: unblocks mounters, fsyncs, frees trees/resource groups, closes the device, and drops caches after mounted-read-only repairs when possible.

## Control Flow
`initialize()` opens the device read-only for `-n` or read-write exclusive otherwise. If exclusive open fails because the device is mounted read-only, it allows a limited root-filesystem style check. It then reads the device info, reads or repairs the superblock, blocks mounters if preen policy permits, reads or rebuilds the master directory, locates `per_node`, initializes `rindex`, fetches resource groups, reads and replays journals, marks the filesystem clean for preen if all journals were clean, then initializes the remaining system inodes.

## Dependencies And Integration
Uses libgfs2 superblock, inode, rindex, rgrp, bitmap, and builder APIs; journal recovery from `fs_recovery.h`; metadata helpers from `metawalk.h`; inode tree deletion from `inode_hash.h`; and query/logging utilities from `util.h`. Globals initialized here are consumed by later passes, especially `last_fs_block`, `first_data_block`, and `last_data_block`.

## Risk Notes
This file contains high-impact recovery logic: superblock reconstruction, root/master guessing, system inode rebuilding, rgrp count correction, and lock protocol rewriting. Most destructive paths are query-gated, but correctness depends on recovered metadata heuristics and on restoring the lock protocol in `destroy()`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/initialize.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/inode_hash.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/inode_hash.c

## Purpose
Implements a red-black tree keyed by inode block address for non-directory inode link-count tracking during fsck.

## Main Elements
- `inodetree_find()`: searches `cx->inodetree` by `num.in_addr`.
- `inodetree_insert()`: returns an existing node for a block or allocates/inserts a new `struct inode_info`.
- `inodetree_delete()`: removes a node from the tree and frees it.

## Dependencies And Integration
Uses `osi_tree` style node operations via `osi_link_node()`, `osi_insert_color()`, and `osi_erase()`. Called by link counting, bitmap repair, pass1 cleanup, duplicate resolution, and global teardown.

## Behavioral Notes
The tree is keyed only by block address. Formal inode number mismatches are checked by callers such as `incr_link_count()`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/inode_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/inode_hash.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/inode_hash.h

## Purpose
Declares the inode tree API used by fsck link and bitmap state management.

## Main Elements
- Forward declaration for `struct inode_info`.
- Prototypes for `inodetree_find()`, `inodetree_insert()`, and `inodetree_delete()`.

## Dependencies And Integration
Includes `fsck.h` for `struct fsck_cx` and `struct lgfs2_inum`. This header is included by initialization, pass1, metawalk, link, and duplicate handling code.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/inode_hash.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/link.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/link.c

## Purpose
Tracks on-disk link counts and counted directory-entry references so later fsck passes can detect and repair link-count mismatches.

## Main Elements
- Globals:
  - `nlink1map`: one-bit map for non-directory dinodes whose on-disk `i_nlink` is exactly 1.
  - `clink1map`: one-bit map for non-directory dinodes with exactly one counted reference.
- `link1_set()`: sets or clears one-bit map entries.
- `set_di_nlink()`: records an inode’s on-disk link count in `dirtree`, `nlink1map`, or `inodetree`.
- `incr_link_count()`: increments counted references for directories, known inodes, one-link-map entries, or promotes a one-link inode into the full inode tree when a second reference is found.
- `decr_link_count()`: decrements counted references for directory/inode tree entries or clears the counted-one-link bit.

## Dependencies And Integration
Uses directory tracking from `dirtree_find()`, inode tracking from `inode_hash.c`, bitmap helpers from `util.h`, and `fsck_load_inode()` / `fsck_inode_put()` when validating promoted hard links. Called by directory traversal, lost+found repair, duplicate cleanup, and pass4 link reconciliation.

## Behavioral Notes
`incr_link_count()` validates formal inode numbers and can return `INCR_LINK_CHECK_ORIG` when a second reference to a previously one-link non-directory inode requires checking the first reference. The one-bit maps avoid allocating full tree nodes for the common one-link case.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/link.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/link.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/link.h

## Purpose
Declares link-count tracking state and APIs shared across fsck passes.

## Main Elements
- Extern maps `nlink1map` and `clink1map`.
- Increment result enum: `INCR_LINK_BAD`, `INCR_LINK_GOOD`, `INCR_LINK_INO_MISMATCH`, `INCR_LINK_CHECK_ORIG`.
- Prototypes for one-bit map updates and link count set/increment/decrement helpers.

## Dependencies And Integration
Includes `fsck.h` for fsck context, bitmap, inode, and inum types. Used by pass1, pass1b, lost+found, metawalk, and main cleanup.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/link.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/lost_n_found.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/lost_n_found.c

## Purpose
Creates or locates `lost+found` and reconnects orphaned or damaged inodes into it during fsck repairs.

## Main Elements
- `add_dotdot()`: rewrites an orphan directory’s `..` entry to point at `lost+found`, decrementing the old parent’s counted/on-disk link when appropriate.
- `make_sure_lf_exists()`: creates or finds root `lost+found`, updates root/lost+found link accounting, marks the new dinode in fsck/rgrp bitmaps, and marks the directory connected.
- `add_inode_to_lf()`: chooses a `lost_*` name by inode mode, adds a directory entry in `lost+found`, updates counted links, and writes the lost+found dinode.

## Dependencies And Integration
Uses global `lf_dip` and `lf_was_created` from `main.c`, directory mutation APIs from libgfs2, link accounting from `link.c`, directory tree state, and bitmap setting from `metawalk.h`. Invoked by later passes when disconnected inodes/directories must be preserved.

## Risk Notes
Directory reconnection changes parentage and link counts. The old `..` target is checked by formal inode number before decrementing, which limits damage from stale parent references.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/lost_n_found.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/lost_n_found.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/lost_n_found.h

## Purpose
Declares lost+found repair entry points.

## Main Elements
- `add_inode_to_lf()`: reconnect one inode into lost+found.
- `make_sure_lf_exists()`: ensure the lost+found directory exists before reconnecting.

## Dependencies And Integration
Includes `libgfs2.h` for inode types and is used by fsck passes that recover disconnected inodes.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/lost_n_found.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/main.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/main.c

## Purpose
Defines the `fsck.gfs2` command-line frontend, global fsck state, pass sequencing, signal interruption behavior, final cleanup, and fsck-compatible exit status calculation.

## Main Elements
- Globals: lost+found inode/state, block progress counters, abort/skip flags, error counters, duplicate counters, `sb_fixed`, and logging level.
- `read_cmdline()`: parses `-a/-p`, `-f`, `-h`, `-n`, `-q`, `-v`, `-V`, and `-y`, enforcing mutually exclusive preen/yes/no modes.
- `interrupt()`: SIGINT handler offering abort, skip current pass, or continue.
- `check_statfs()`: recomputes total/free/dinode counts from resource groups and optionally rewrites the statfs file.
- `passes[]`: ordered pass table: `pass1`, `pass1b`, `pass2`, `pass3`, `pass4`, `check_statfs`.
- `fsck_pass()`: logs and times one pass, handles abort/skip state, exits on pass error.
- `startlog()` / `exitlog()`: syslog command and exit status.
- `main()`: initializes locale/syslog/options, calls `initialize()`, optionally exits early for clean preen, installs SIGINT handler, runs all passes, releases system inodes, fsyncs, destroys link maps and context, warns after superblock reset, and computes final status.

## Dependencies And Integration
Top-level integration point for `initialize.c`, pass modules, link maps, metawalk state, libgfs2 inode lifetimes, logging, syslog, and command-line policy.

## Behavioral Notes
Skipping pass1 is explicitly discouraged inside pass1 itself. Final status is `FSCK_OK` if no errors were found, `FSCK_NONDESTRUCT` if all found errors were corrected, and `FSCK_UNCORRECTED` otherwise.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/metawalk.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/metawalk.c

## Purpose
Provides the callback-driven metadata traversal and repair engine used by GFS2 fsck passes. It walks inode metadata trees, directory hash/leaf structures, directory entries, data pointers, and extended attributes while delegating pass-specific decisions to `struct metawalk_fxns`.

## Main Elements
- Bitmap synchronization:
  - `check_n_fix_bitmap()` compares discovered block state to rgrp bitmap state, query-repairs mismatches, and updates rgrp free/dinode counts.
  - `_fsck_bitmap_set()` wraps bitmap repair with debug tracing.
- Inode helpers:
  - `dupfind()` searches duplicate-block tree.
  - `fsck_system_inode()`, `fsck_load_inode()`, `fsck_inode_get()`, `fsck_inode_put()` special-case system inodes and `lost+found`.
- Directory entry/leaf checking:
  - `dirent_repair()` and `dirblk_truncate()` repair corrupt directory entry lengths or truncate a block.
  - `check_entries()` walks linear or leaf directory entries and calls pass-specific `check_dentry`.
  - `check_leaf()` validates one exhash leaf, repairs bad leaf pointers, checks entries, and fixes leaf entry counts.
  - `check_leaf_blks()` reads the directory hash table, readaheads leaves, validates chained leaves, and adapts to directory depth/height changes.
  - `check_linear_dir()` and `check_dir()` expose directory checking for stuffed and exhash directories.
- Extended attributes:
  - `check_eattr_entries()` walks EA headers and extended data pointers.
  - `check_leaf_eattr()` validates one EA leaf.
  - `check_indirect_eattr()` walks indirect EA leaf pointer blocks and handles no-hole semantics.
  - `check_inode_eattr()` dispatches direct versus indirect EA validation.
- Metadata/data tree walking:
  - `build_and_check_metalist()` builds per-height metadata buffer lists and calls `check_metalist`.
  - `metawalk_check_data()` calls pass-specific `check_data` for data pointers.
  - `undo_check_data()` and metadata undo logic reverse pass work after unrecoverable errors.
  - `check_metatree()` is the main inode metadata walker and invalidates corrupt inodes when requested.

## Control Flow
Passes provide a `metawalk_fxns` table. `check_metatree()` builds metadata lists from the dinode outward, checks metadata blocks, branches to directory leaf checking for exhash directories, or checks regular data pointers for files. On fatal metadata/data errors, it can ask to remove the invalid inode, run pass-specific undo callbacks, delete duplicate references, and mark the dinode free.

## Dependencies And Integration
Used heavily by pass1, pass1b, lost+found repair, and later directory/link passes. Depends on libgfs2 buffer/inode/dir/EA APIs, duplicate tracking, link maps, directory/inode trees, and query/logging utilities.

## Risk Notes
This is a shared repair engine, so callback contracts are critical: callbacks must distinguish fatal errors, skip-one, skip-further, duplicate references, and valid blocks consistently. It intentionally performs query-gated destructive operations such as clearing bitmap states, truncating directory blocks, deleting EA chains, and invalidating inodes.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/metawalk.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/metawalk.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/metawalk.h

## Purpose
Declares the metadata walking API, callback return codes, inode pointer helper type, and `struct metawalk_fxns` callback table.

## Main Elements
- Directory constants: `DIR_LINEAR`, `DIR_EXHASH`.
- Public walkers: `check_inode_eattr()`, `check_metatree()`, `check_leaf_blks()`, `check_dir()`, `check_linear_dir()`, and `check_leaf()`.
- Bitmap/duplicate helpers: `_fsck_bitmap_set()`, `check_n_fix_bitmap()`, `dupfind()`, and `fsck_system_inode()`.
- Macros: `fsck_bitmap_set()` and `fsck_bitmap_set_noino()` add callsite metadata; `iptr_*` macros decode indirect pointer positions.
- `enum meta_check_rc`: `META_ERROR`, `META_IS_GOOD`, `META_SKIP_FURTHER`, `META_SKIP_ONE`.
- `struct iptr`: current inode, buffer, and offset for indirect pointer callbacks.
- `struct metawalk_fxns`: pass-specific callbacks for leaves, metadata, data, EA indirect/leaf/entry/extentry, hash tables, leaf repair, undo, delete, and large-file progress.

## Dependencies And Integration
Includes `util.h` and is the primary contract between generic traversal in `metawalk.c` and pass-specific policy in pass1/pass1b/later passes.

## Risk Notes
The header exposes a broad callback interface where return-code semantics control whether fsck continues, skips, repairs, or deletes. The `is_duplicate(dblock)` macro appears inconsistent with the declared `dupfind(struct fsck_cx *, uint64_t)` signature and would be unsafe if used as written.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/metawalk.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/pass1.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/pass1.c

## Purpose
Implements fsck pass 1: scans dinodes from resource-group bitmaps, validates inode format/type, metadata trees, data pointers, directory leaves, extended attributes, block counts, system inodes, duplicate references, and builds the primary block/link maps used by later passes.

## Main Elements
- Block map state:
  - Static `bl`: two-bit fsck blockmap for discovered block state.
  - `blockmap_set()`, `_fsck_blockmap_set()`, `fsck_blockmap_set()`: synchronize fsck blockmap with rgrp bitmap repairs.
  - `blockmap_create()`, `link1_create()`, `bmap_create()`, destroy helpers, and `enomem()`.
- Pass1 metawalk callbacks:
  - `p1_check_metalist()`: validates indirect/hash-table blocks, detects duplicates, zeroes bad indirect pointers if approved.
  - `p1_check_data()`: validates data pointers, classifies duplicate data/meta/dinode conflicts, and adds duplicate refs.
  - `p1_check_leaf()`: marks exhash directory leaf blocks and records duplicate leaf references.
  - `p1_repair_leaf()`: patches bad directory leaf references by zeroing hash table slots.
  - EA callbacks validate indirect EA blocks, EA leaves, EA entries, and extended EA data blocks.
  - Undo callbacks reverse metadata/data work when an inode is invalidated.
- Range checking:
  - `rangecheck_block()` and related callbacks preflight inodes for excessive invalid/duplicate pointers before destructive cleanup.
- Inode processing:
  - `set_ip_blockmap()` classifies dinodes by mode and inserts directories into the directory tree.
  - `handle_ip()` orchestrates rangecheck, dinode marking, link tracking, metadata/data/EA checks, lost+found reprocessing, and block-count repair.
  - `handle_di()` loads an inode from a dinode buffer, repairs bad inode address fields, checks allocation goal, and calls `handle_ip()`.
- System inode repair:
  - `resuscitate_metalist()` / `resuscitate_dentry()` keep system directory contents alive.
  - `check_system_inode()` validates or rebuilds master, root, inum, statfs, jindex, rindex, quota, per_node, and journals.
  - Builders wrap libgfs2 creation for root, master, per_node, inum, statfs, rindex, quota, and journals.
- Resource-group scan:
  - `pass1_process_rgrp()` scans each rgrp bitmap for dinodes.
  - `pass1_process_bitmap()` reads each dinode candidate, detects invalid/duplicate dinodes, and dispatches inode handling.
- `pass1()`: allocates maps, checks system inodes, marks rgrp metadata blocks, processes every rgrp, then calls `pass5(cx, bl)` to reconcile bitmaps.

## Control Flow
Pass 1 first creates `bl`, `nlink1map`, and `clink1map`. It validates system inodes before scanning user dinodes. For each resource group it marks rgrp header/bitmap blocks as used, scans bitmap dinode states, skips already-processed system inodes, validates dinode headers, processes inode metadata and EA trees via metawalk, records duplicates, and tracks link counts. After scanning, it invokes pass5 immediately to reconcile discovered block state with on-disk bitmaps.

## Dependencies And Integration
Uses `metawalk.c` as the traversal engine; duplicate tracking and delete helpers from fsck common code; journal/per_node builders from libgfs2 and recovery code; link accounting from `link.c`; inode tree helpers; and global progress/abort state from `main.c`.

## Risk Notes
Pass1 is intentionally destructive under query control: it can mark dinodes free, zero indirect pointers, remove extended attributes, repair block counts, rebuild system inodes, allocate system structures, and rewrite bitmap/rgrp accounting. Its preflight bad-pointer tolerance is a safety guard against treating garbage pointer fields as authoritative.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/pass1.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/pass1b.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/pass1b.c

## Purpose
Implements pass 1b duplicate-block resolution. It rescans inodes to find all references to blocks pass1 marked duplicate, classifies each duplicate by actual block type, deletes or repairs invalid references, clones duplicate data blocks when possible, and updates bitmaps to reflect the remaining owner.

## Main Elements
- Data structures:
  - `fxn_info`: search state for a block.
  - `dup_handler`: live duplicate tree/ref counts while repairs mutate the tree.
  - `clone_target`: target block and first-reference flag for cloning.
  - `meta_blk_ref`: metadata block/offset where a target data reference was found.
- Reference discovery:
  - `find_block_ref()` loads a dinode, records self-reference, walks metadata/data/EA references, and adds refs for known duplicates.
  - `check_leaf_refs()`, `check_metalist_refs()`, `check_data_refs()`, `check_eattr_*_refs()` are metawalk callbacks that call `add_duplicate_ref()`.
- Duplicate logging and accounting:
  - `log_inode_reference()` reports per-inode duplicate reference type counts.
  - `revise_dup_handler()` recalculates reference counts after each mutation.
- Repair actions:
  - `resolve_dup_references()` removes invalid references first, then wrong-type references, then extra valid references. It can remove EAs, delete corrupt dinodes, run delete callbacks over metadata trees, remove tree/link state, and delete duplicate list entries.
  - `clone_data_block()` finds a specific data pointer and clones it.
  - `clone_data()` allocates a replacement block, copies content, rewrites the pointer, or optionally zeroes the reference.
  - `clone_dup_ref_in_inode()` clones repeated references to the same duplicate within one inode.
  - `resolve_last_reference()` sets the final block bitmap state from the surviving reference type and deletes the duplicate tree node.
  - `handle_dup_blk()` drives the full four-step duplicate resolution for one block.
- `pass1b()`: scans all dinode blocks to discover original duplicate references, then drains `cx->dup_blocks` by calling `handle_dup_blk()`.

## Control Flow
If the duplicate tree is empty, pass1b exits. Otherwise it scans block numbers up to `last_fs_block`, uses bitmap states to find dinodes, and calls `find_block_ref()` until all original duplicate references are found or the scan ends. It then repeatedly takes the first duplicate tree node, logs references, determines the acceptable reference type from the duplicate block’s on-disk metadata header, removes invalid references, removes wrong-type references, removes extra valid references, and fixes or frees the remaining block state.

## Dependencies And Integration
Uses duplicate-tree/list APIs from fsck common code, delete callbacks from `afterpass1_common.h`, metawalk traversal, link and inode/directory tree cleanup, bitmap repair from `metawalk.c`, and libgfs2 allocation/buffer/inode APIs.

## Risk Notes
Pass1b repairs can delete inodes, remove extended attributes, free metadata/data trees, clone blocks, and change bitmap state. It constantly recomputes duplicate counts because repairs mutate the duplicate tree. User “no” answers can leave references unresolved, in which case pass1b preserves remaining refs rather than silently forcing a repair.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/pass1b.c -->