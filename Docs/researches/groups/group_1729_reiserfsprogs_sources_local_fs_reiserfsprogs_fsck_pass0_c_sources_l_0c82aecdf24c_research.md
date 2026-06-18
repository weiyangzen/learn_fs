# Group Research: group_1729_reiserfsprogs_sources_local_fs_reiserfsprogs_fsck_pass0_c_sources_l_0c82aecdf24c

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/reiserfsprogs`.

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/pass0.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/pass0.c

`pass0.c` implements pass 0 of `reiserfsck --rebuild-tree`. It scans the selected block set and classifies blocks before tree reconstruction.

Key responsibilities:
- Builds auxiliary bitmaps for found leaf blocks, uniquely referenced unformatted blocks, and multiply referenced unformatted blocks.
- Selects the scan source from used blocks, whole partition, or an external bitmap, then excludes superblock, bitmap blocks, journal/reserved area, and bad blocks.
- Reads candidate blocks, identifies leaf-like blocks, and runs `pass0_correct_leaf()` to normalize leaf structure enough for later passes.
- Repairs or deletes malformed item headers: bad short keys, unknown item types, wrong key formats, item ordering problems, invalid offsets, invalid direct/indirect item shapes, and inconsistent stat-data modes.
- Verifies and repairs directory items by checking entry counts, entry locations, `.`/`..`, hash offsets, visibility bits, and `/lost+found`-style temporary names.
- Registers indirect-item unformatted pointers, zeroing pointers outside data space, into metadata/journal areas, outside the filesystem, or listed as bad blocks.
- Tracks object IDs seen in item keys and directory entries for later object-id-map rebuilding.
- Chooses the directory hash function from observed directory-entry hash hits if the superblock does not already define one.
- Saves and reloads pass-0 state as three bitmaps under `PASS_0_DONE`.

Important exported helpers:
- `is_used_leaf()`
- `is_bad_unformatted()`
- `is_good_unformatted()`
- `still_bad_unfm_ptr_1()`
- `still_bad_unfm_ptr_2()`
- `are_there_allocable_blocks()`
- `alloc_block()`
- `make_allocable()`
- `is_bad_item()`
- `is_leaf_bad()`
- `load_pass_0_result()`
- `pass_0()`

Dependencies and data flow:
- Uses global `fs`, `fsck_data(fs)`, pass statistics, ReiserFS bitmap helpers, item/key helpers, `bread()`/buffer-cache APIs, and balancing/file helpers declared through `fsck.h`.
- Produces the leaf/unformatted classification consumed by pass 1 and allocation routines.
- Produces an object-id map later flushed into the superblock/object-id area.

Notable behavior:
- Pass 0 is heuristic and repair-oriented. It may delete items from leaf blocks during normalization if it cannot infer a safe correction.
- In `FSCK_CHECK`/`FSCK_AUTO`, some structural problems are counted as fixable/fatal rather than repaired.
- Hash mismatch can cause a whole leaf to be skipped as “too old” for the selected hash.
- Many invariants use `die()`/`reiserfs_panic()` because later rebuild passes assume pass 0 removed impossible metadata.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/pass0.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/pass1.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/pass1.c

`pass1.c` implements pass 1 of rebuild-tree: it takes leaf blocks discovered by pass 0 and tries to insert whole leaves into a newly built tree.

Key responsibilities:
- Creates the new on-disk bitmap model, initially marking block 0, pre-super blocks, superblock, bitmap blocks, journal/reserved area, and bad blocks as used.
- Creates an “uninsertable leaves” bitmap where cleared bits represent leaves that pass 1 could not safely attach as whole nodes.
- Builds an allocable-block bitmap from blocks that are neither metadata nor found leaves nor referenced unformatted data.
- Initializes the block allocator/deallocator hooks used by tree balancing.
- Corrects pass-1 leaf contents before insertion:
  - Deletes directory entries hashed with the wrong hash function.
  - Enforces increasing directory entry hash offsets.
  - Zeroes indirect pointers that point to recovered leaves.
  - Keeps only one reference to multiply referenced unformatted blocks.
- Attempts whole-leaf insertion by comparing the candidate leaf’s first/last key against the existing tree position and neighbor delimiting keys.
- Marks successfully inserted leaf items unreachable initially, so the later semantic pass can mark truly reachable objects.
- Marks data blocks referenced by accepted indirect items as used in the new bitmap.
- Persists pass-1 state: new on-disk bitmap, uninsertables bitmap, and allocable bitmap.

Important exported helpers:
- `make_buffer()`
- `is_item_reachable()`
- `mark_item_unreachable()`
- `mark_item_reachable()`
- `remove_saved_item()`
- `load_pass_1_result()`
- `pass_1()`

Dependencies and data flow:
- Consumes `leaves_bitmap`, good/bad unformatted bitmaps, and pointer validation from pass 0.
- Produces `fsck_new_bitmap(fs)`, `fsck_uninsertables(fs)`, and `fsck_allocable_bitmap(fs)` for pass 2.
- Uses tree search, `fix_nodes()`, and `do_balance()` to attach leaf pointers into internal nodes.

Notable behavior:
- Pass 1 only inserts whole leaves when they do not overlap existing keys and cannot be merged with neighbors in a way that would violate balancing expectations.
- Leaves that are malformed, overlap existing tree contents, fall into journal special cases, or cannot satisfy neighbor conditions are deferred to pass 2.
- Duplicate unformatted pointers are resolved by preserving the first accepted reference and zeroing later references.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/pass1.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/pass2.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/pass2.c

`pass2.c` handles leaves that pass 1 could not insert whole. It reconstructs them item by item.

Key responsibilities:
- Maintains a relocation list mapping old `(dir_id, objectid)` pairs to newly allocated object IDs.
- Inserts uninsertable leaves in two passes:
  - First pass inserts valid stat-data items.
  - Second pass inserts valid non-stat-data items.
- Resolves object-id collisions between directory objects and non-directory file objects by relocating files or directories.
- Inserts or merges stat-data items, preferring newer format and newer modification time where appropriate.
- Inserts directory entries one at a time with `reiserfs_add_entry()`, after checking hash correctness.
- Dispatches regular file/direct/indirect item insertion to `reiserfsck_file_write()`.
- Links relocated files into `/lost+found` later through `link_relocated_files()`.
- Saves pass-2 completion as `TREE_IS_BUILT`; no large state is serialized after this point.

Important exported helpers:
- `objectid_for_relocation()`
- `linked_already()`
- `link_relocated_files()`
- `save_item()`
- `save_and_delete_file_item()`
- `should_relocate()`
- `insert_item_separately()`
- `load_pass_2_result()`
- `pass_2()`

Dependencies and data flow:
- Consumes `fsck_uninsertables(fs)` and `fsck_allocable_bitmap(fs)` from pass 1.
- Uses `proper_id_map(fs)` to allocate relocation object IDs.
- Uses `rewrite_file()`, `reiserfsck_file_write()`, and semantic helpers to keep files/directories distinct when keys collide.
- Produces a built tree and updates `fs->fs_bitmap2` from `fsck_new_bitmap(fs)`.

Notable behavior:
- Stat-data insertion is intentionally first so later file items can be matched to an object.
- Directory stat data causes same-key non-directory items to be moved away; non-directory stat data may be relocated if directory items already occupy the key.
- If no root metadata is found after pass 2, `pass_2()` emits a long diagnostic about possible partition-start shifts or wiped data.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/pass2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/pass4.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/pass4.c

`pass4.c` implements the final cleanup pass after semantic reachability has been computed.

Key responsibilities:
- Walks the tree starting from `root_dir_key`.
- Deletes every item whose item-header reachability flag remains unset.
- Clears residual item-header flags on retained items.
- Reports pass-4 statistics.
- Copies `fsck_new_bitmap(fs)` into the filesystem bitmap.
- Recomputes and stores the free-block count from the new bitmap.
- Flushes object-id map, bitmap, superblock, and all dirty buffers.

Important exported helper:
- `pass_4_check_unaccessed_items()`

Dependencies and data flow:
- Consumes reachability flags set by semantic rebuild/check logic.
- Consumes `fsck_new_bitmap(fs)` from rebuild passes.
- Calls `reiserfsck_delete_item()` for unreachable metadata and `id_map_flush()` before final flush.

Notable behavior:
- This pass is deliberately simple: semantic pass decides reachability; pass 4 removes everything not marked reachable.
- It also sanitizes retained item flags so repaired metadata does not keep fsck-only flags.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/pass4.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/reiserfsck.8.in -->
# File Research: sources/local-fs/reiserfsprogs/fsck/reiserfsck.8.in

This file is the `reiserfsck(8)` manual page template.

Key content:
- Defines `reiserfsck` as the ReiserFS checking and repair tool.
- Documents main modes:
  - `--check`: default consistency check, no repair.
  - `--fix-fixable`: fixes limited corruption without full tree rebuild.
  - `--rebuild-tree`: rebuilds the full filesystem tree from discovered leaves.
  - `--rebuild-sb`: reconstructs a missing/damaged superblock.
  - `--clean-attributes`: clears old stat-data reserved fields before extended attributes use.
- Documents journal handling with `--journal` and expert `--no-journal-available`.
- Documents repair modifiers such as `--adjust-size`, `--badblocks`, `--logfile`, `--nolog`, `--quiet`, `--yes`, `--force`, and `--scan-whole-partition`.
- Gives an operational example: run `--check`, then `--fix-fixable` for exit code 1, or `--rebuild-tree` for fatal corruption/exit code 2.
- Lists exit codes 0, 1, 2, 4, 6, 8, and 16.
- Warns that `--rebuild-tree` should be backed up first and not interrupted once started.

Relationship to code:
- The documented pass behavior maps to the rebuild flow implemented by `pass0.c`, `pass1.c`, `pass2.c`, `semantic_rebuild.c`, and `pass4.c`.
- `--fix-fixable` behavior maps to semantic/stat-data fixes in `semantic_check.c` and shared file validation in `ufile.c`.
- `--rebuild-sb` maps to the interactive logic in `super.c`.

Notable documentation details:
- `--yes` is explicitly disabled for `--rebuild-tree` for safety.
- `--scan-whole-partition` expands rebuild-tree scanning beyond used blocks, matching pass-0 scan-area logic.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/reiserfsck.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/semantic_check.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/semantic_check.c

`semantic_check.c` implements the semantic pass used by `--check` and `--fix-fixable`.

Key responsibilities:
- Recursively walks the directory tree from `root_dir_key`.
- Detects directory loops with a linked list of short keys representing the current traversal path.
- Validates regular files through `are_file_items_correct()` and shared stat-data validators.
- Checks and optionally fixes stat-data fields:
  - mode
  - size
  - block count
  - old-format first-direct-byte metadata
- Checks directory structure:
  - stat data exists
  - `.` and `..` exist and point correctly
  - directory entries are properly hashed
  - new-format entry lengths are aligned
  - names point to existing stat data
  - directory size and block count match entries
- Checks safe links under dirid `-1`, including invalid safe links and truncate links.
- In `FSCK_FIX_FIXABLE`, removes bad entries, adds/fixes `.`/`..`, fixes stat data, updates bitmaps, and applies bad-block list changes.
- In check-only mode, counts fixable/fatal corruptions without mutating most structures.

Important exported helper:
- `semantic_check()`

Important internal helpers:
- `check_path_key()`, `add_path_key()`, `del_path_key()`
- `check_check_regular_file()`
- `get_next_directory_item()`
- `check_semantic_pass()`
- `check_safe_links()`

Dependencies and data flow:
- Uses shared validators from `semantic_rebuild.c` and `ufile.c`: `wrong_mode()`, `wrong_st_blocks()`, `wrong_st_size()`, `wrong_first_direct_byte()`, `get_object_key()`, `print_name()`, `erase_name()`.
- Uses global `trunc_links` to avoid reporting wrong file size for files with valid truncate safe links.
- In fixable mode, initializes `fsck_new_bitmap(fs)` and `fsck_allocable_bitmap(fs)` from the current bitmap so repair operations can allocate/deallocate safely.

Notable behavior:
- Semantic checking is skipped if earlier structural tree checks found bad nodes or fatal corruptions.
- Directory hard links are treated as corruption except for valid `..` traversal.
- Some relocation logic is compiled out for fix-fixable because file rewrite can be too invasive for that mode.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/semantic_check.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/semantic_rebuild.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/semantic_rebuild.c

`semantic_rebuild.c` implements pass 3, the semantic phase of `--rebuild-tree`.

Key responsibilities:
- Provides progress display helpers `print_name()` and `erase_name()` for showing the current traversal path.
- Provides shared stat-data validation/correction helpers used by both rebuild and check:
  - `wrong_st_size()`
  - `wrong_st_blocks()`
  - `wrong_mode()`
  - `wrong_first_direct_byte()`
- Relocates directories when object IDs collide with already reached objects.
- Recursively walks from the root directory, marks reachable items, fixes `.`/`..`, updates link counts, and repairs directory/file stat data.
- Handles regular files via `rebuild_check_regular_file()`, which increments link count, marks reachable file items, validates item sequence, and corrects size/block/mode fields.
- Creates or validates `/lost+found`, including stat data and `.`/`..`, and inserts it into the root directory if needed.
- Links relocated files into `/lost+found`.
- Adds bad-block list entries after semantic rebuild.
- Saves semantic completion as `SEMANTIC_DONE`.

Important exported helpers:
- `print_name()`
- `erase_name()`
- `wrong_st_size()`
- `wrong_st_blocks()`
- `wrong_mode()`
- `wrong_first_direct_byte()`
- `relocate_dir()`
- `rebuild_check_regular_file()`
- `get_object_key()`
- `fix_obviously_wrong_sd_mode()`
- `is_dot()`
- `is_dot_dot()`
- `not_a_directory()`
- `not_a_regfile()`
- `zero_nlink()`
- `modify_item()`
- `load_semantic_result()`
- `pass_3_semantic()`

Dependencies and data flow:
- Consumes the rebuilt tree from pass 2.
- Uses `semantic_id_map(fs)` to detect object-id sharing during traversal.
- Uses `proper_id_map(fs)` for allocation of new object IDs and persistence.
- Sets reachability flags consumed by `pass4.c`.

Notable behavior:
- At the start of rebuild, stat-data link counts have been zeroed and items marked unreachable. Traversal increments link counts and marks reachable items.
- Non-root entries pointing nowhere are removed during rebuild.
- Root `..` pointing to `REISERFS_ROOT_PARENT_OBJECTID` is tolerated.
- Directory and regular-file collisions are handled by relocation and directory-entry key updates.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/semantic_rebuild.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/super.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/super.c

`super.c` implements interactive superblock reconstruction and normalization for `reiserfsck --rebuild-sb`.

Key responsibilities:
- Determines filesystem version interactively when it cannot infer it from magic strings and superblock location.
- Handles both cases:
  - A ReiserFS superblock is found but contains damaged/inconsistent fields.
  - No usable ReiserFS superblock is found and a new one must be created.
- Normalizes or reconstructs:
  - ReiserFS format version
  - block count and block size
  - object-id map sizes
  - bitmap count
  - root block
  - free-block count
  - unmount state
  - object-id cursor size
  - tree height
  - hash code
  - UUID and superblock flags for newer formats
- Handles standard and non-standard journal layouts.
- Opens/checks the journal and compares journal-header parameters with superblock journal parameters.
- Prompts for journal offset and size when needed.
- Can mark journal as needing `reiserfstune` when `--no-journal-available` is used.
- Rebuilds the journal header after confirmation when parameters are inconsistent.
- Prints the candidate superblock and asks the user before writing it.

Important exported helper:
- `rebuild_sb()`

Dependencies and data flow:
- Uses ReiserFS creation/open/journal helpers, `count_blocks()`, journal-parameter advisory helpers, UUID support when available, and user confirmation routines.
- Mutates `fs->fs_ondisk_sb` and journal header buffers only after validation and user confirmation.

Notable behavior:
- This path is intentionally interactive and exits when complete.
- It sets `FS_ERROR` on rebuilt/modified superblocks so the filesystem still requires a subsequent `reiserfsck --check`.
- It refuses unsafe journal/superblock combinations, such as specifying a separate journal for a filesystem whose superblock indicates a default journal.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/ubitmap.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/ubitmap.c

`ubitmap.c` contains bitmap and allocation helpers used while rebuilding the tree.

Key responsibilities:
- Tests and marks blocks in `fsck_new_bitmap(fs)`, the bitmap representing blocks used by the rebuilt tree.
- Prevents duplicate block use with hard failures in `mark_block_used()` and `mark_block_free()`.
- Represents uninsertable leaves by clearing bits in `fsck_uninsertables(fs)`.
- Allocates new blocks through `reiserfsck_reiserfs_new_blocknrs()` using the allocable bitmap prepared by pass 1.
- Returns new buffer heads for newly allocated blocks with `reiserfsck_get_new_buffer()`.
- Frees blocks from the new bitmap and returns them to the allocable pool.

Important exported helpers:
- `is_block_used()`
- `mark_block_used()`
- `is_block_uninsertable()`
- `mark_block_uninsertable()`
- `reiserfsck_reiserfs_new_blocknrs()`
- `reiserfsck_get_new_buffer()`
- `reiserfsck_reiserfs_free_block()`

Dependencies and data flow:
- Consumes allocation helpers from `pass0.c`: `are_there_allocable_blocks()`, `alloc_block()`, and `make_allocable()`.
- Consumes `fsck_new_bitmap(fs)`, `fsck_uninsertables(fs)`, and `fsck_allocable_bitmap(fs)` created by pass 1/load routines.
- Supplies allocator hooks assigned to `fs->block_allocator` and `fs->block_deallocator`.

Notable behavior:
- Block 0 is ignored by `mark_block_used()`.
- `reiserfsck_get_new_buffer()` does not zero the buffer; callers that need zero-filled blocks explicitly clear it.
- The file comments document the rebuild model: old disk bitmap is scanned, new bitmap tracks the emerging tree, and allocable bitmap tracks blocks safe for repair allocations.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/ubitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/ufile.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/ufile.c

`ufile.c` contains shared file-item validation, rewrite, conversion, and insertion logic used by pass 2 and semantic passes.

Key responsibilities:
- Validates file item sequences with `are_file_items_correct()`:
  - walks direct/indirect items by offset
  - detects holes, overlaps, wrong ordering, directories where file data should be, and same-type adjacent items in one node
  - computes real size and block count
  - optionally marks file items reachable
  - fixes key-format mismatches where allowed
  - detects symlink/tail cases
  - converts final indirect items back to direct items when stat data indicates they should be tails/symlinks
- Rewrites files by saving items, deleting them, optionally relocating object IDs, and reinserting items in order.
- Makes files writable before merging new items by checking/rebuilding their existing item sequence.
- Inserts first file items, creating indirect items and unformatted blocks as needed.
- Converts direct items/tails to indirect items and unformatted blocks when appending/overwriting requires block storage.
- Appends file data, including zero unformatted pointers for holes.
- Overwrites existing file regions with direct or indirect incoming data.
- Main write entry point `reiserfsck_file_write()` inserts or merges a recovered file item into the rebuilt tree.
- Maintains corruption counters for check/fix modes.

Important exported helpers:
- `delete_N_items_after_key()`
- `are_file_items_correct()`
- `rewrite_file()`
- `reiserfsck_append_file()`
- `must_there_be_a_hole()`
- `reiserfs_append_zero_unfm_ptr()`
- `reiserfsck_file_write()`
- `one_more_corruption()`
- `one_less_corruption()`

Dependencies and data flow:
- Uses relocation helpers from `pass2.c`: `objectid_for_relocation()`, `should_relocate()`, `save_and_delete_file_item()`, `insert_item_separately()`.
- Uses bitmap/allocation helpers from `ubitmap.c` and pointer checks from `pass0.c`.
- Uses semantic helpers such as `not_a_directory()` and `fix_obviously_wrong_sd_mode()`.
- Heavily depends on tree search and item mutation primitives from the ReiserFS library.

Notable behavior:
- Direct data recovered from a leaf may be copied into newly allocated unformatted nodes when the rebuilt file representation requires indirect storage.
- Incoming indirect pointers from items not already in the tree are checked with `still_bad_unfm_ptr_2()` before being marked used.
- Existing direct items may be converted to indirect items before overwrite to avoid conflicting file layouts.
- Files without stat data are skipped during pass-2 item insertion.
- If a target file remains inconsistent after rewrite, insertion is skipped rather than forcing more corruption into the rebuilt tree.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/ufile.c -->