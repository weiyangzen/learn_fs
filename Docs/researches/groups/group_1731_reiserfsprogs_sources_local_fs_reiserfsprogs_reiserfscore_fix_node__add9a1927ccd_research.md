# Group Research: group_1731_reiserfsprogs_sources_local_fs_reiserfsprogs_reiserfscore_fix_node__add9a1927ccd

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/reiserfsprogs` is in subset A. All nine listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/fix_node.c -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/fix_node.c

## Purpose
`fix_node.c` performs the pre-balance analysis for ReiserFS tree updates. Before insertion, paste, delete, or cut operations mutate the tree, it builds a virtual representation of the affected node, decides whether data can stay in place, shift to neighbors, merge, split, or require new blocks, and gathers the required parents, neighbors, and free buffers.

## Main Responsibilities
- Builds `struct virtual_node`/`struct virtual_item` state from the real path node.
- Computes how many items or bytes can move left/right.
- Handles direct, indirect, stat-data, and directory items with different split rules.
- Determines balancing parameters in `struct tree_balance`.
- Allocates free empty buffers for new nodes through `reiserfs_new_blocknrs`.
- Finds direct/far parents and neighboring nodes needed by later balancing.
- Cleans up path, neighbor, parent, and unused new-node buffers in `unfix_nodes`.

## Key Functions
- `create_virtual_node()` constructs virtual item metadata from `S[h]`, including item lengths, type flags, directory entry sizes, offsets, and left/right mergeability.
- `check_left()` / `check_right()` calculate how much of the virtual node can fit into left/right neighbors. Leaf splitting is constrained by 8-byte direct-item alignment, unformatted-pointer granularity, and whole directory entries.
- `get_num_ver()` estimates how many output nodes are needed under different shifting and flowing scenarios.
- `set_parameters()` writes the selected balancing plan into `tree_balance` fields such as `lnum`, `rnum`, `blknum`, `lbytes`, `rbytes`, `s0num`, `s1num`, and `s2num`.
- `are_items_mergeable()`, `is_left_mergeable()`, and `is_right_mergeable()` decide whether adjacent file/directory items can share a header after shifting.
- `get_parents()`, `get_far_parent()`, `get_direct_parent()`, and `get_neighbors()` resolve the path-relative parent/neighbor buffers used by execution code.
- `ip_check_balance()` handles increasing node size for insert/paste.
- `dc_check_balance_internal()` and `dc_check_balance_leaf()` handle decreasing node size for delete/cut.
- `fix_nodes()` is the public entry point; it walks levels bottom-up, computes plans, fetches resources, and propagates required insert sizes to higher levels.
- `unfix_nodes()` releases all resources and returns unused free blocks.

## Data and Control Flow
The file is the planning half of ReiserFS balancing. `fix_nodes()` starts at the leaf, validates the direct parent, initializes `tb->tb_vn`, and calls `check_balance()`. `check_balance()` sets virtual-node mode metadata and dispatches to insertion/paste or deletion/cut logic based on `tb->insert_size[h]`.

For leaf nodes, the analysis works in item/body units. Direct items can split only on 8-byte boundaries, indirect items on `UNFM_P_SIZE`, directory items only by complete directory entries, and stat-data or newly inserted empty directory items are not split. For internal nodes, the analysis works in fixed `DC_SIZE + KEY_SIZE` units.

The planner tries to minimize new node count, then minimize shifted neighbors, then prefer cached left neighbors. After a level is planned, `fix_nodes()` may allocate FEB buffers and compute the `insert_size` that must be propagated to the next tree level.

## Integration Points
- Calls `search_by_key`, `pathrelse`, `get_rkey`, `replace_key`-related helpers, and buffer-cache APIs.
- Supplies execution parameters consumed by `lbalance.c`, `ibalance.c`, and `do_balance.c`.
- Uses item/key helpers from `node_formats.c` and on-disk access macros from ReiserFS headers.
- Uses allocator functions such as `reiserfs_new_blocknrs()` and `reiserfs_free_block()`.

## Risks and Edge Cases
- The code relies heavily on path correctness and panics on inconsistent parent/child relationships.
- Directory splitting has special constraints for `.` and `..`; invalid counts can silently alter balance choices.
- `get_empty_nodes()` allocates blocks before final mutation and depends on `unfix_nodes()` to free unused FEB entries.
- Multiple comments reference historical kernel scheduling/SMP concerns, but this userspace implementation still assumes serialized buffer manipulation.
- Mergeability checks read neighbor leaves through tree searches; stale or corrupt paths can produce hard panics.

## Testing Signals
Good tests would cover insert/paste/delete/cut cases that trigger: no balancing, single-side shift, two-side shift, leaf merge/removal, internal merge/removal, root growth, root shrink, directory-entry splits, direct-item alignment, and indirect-pointer splits.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/fix_node.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/hashes.c -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/hashes.c

## Purpose
`hashes.c` implements the directory-name hash functions used by ReiserFS directory ordering and validation.

## Main Responsibilities
- Provides the TEA-based keyed hash.
- Provides the legacy Rupasov/Yura hash.
- Provides the legacy `r5` hash.
- Contains a disabled standalone test harness under `#if 0`.

## Key Functions
- `keyed_hash()` hashes a signed character buffer using a TEA-derived Davis-Meyer construction. It processes 16-byte chunks with partial rounds, pads the tail with repeated length bytes, then performs full rounds.
- `yura_hash()` converts name bytes into a decimal-like accumulator with padding-style loops, then shifts the result left by 7.
- `r5_hash()` accumulates each byte’s high/low nibbles and multiplies by 11.

## Data and Control Flow
The hash functions return `u32` values. Higher-level code masks or extracts hash/generation portions when comparing directory entry offsets. `node_formats.c` registers these functions in the hash table and uses them to detect or verify the active filesystem hash.

## Integration Points
- Used through `hashf_t` mappings in `node_formats.c`.
- Directory validation calls `hash_value()`/`GET_HASH_VALUE()` against these functions.
- Superblock hash-code conversion maps stored hash IDs to these function pointers.

## Risks and Edge Cases
- `keyed_hash()` builds 32-bit words from `signed char`; negative `msg[i]` values can sign-extend before conversion on platforms where char values exceed ASCII.
- It uses deliberate null writes in impossible guard branches, a legacy crash-on-bug pattern.
- `yura_hash()` has unusual loops that depend on integer overflow behavior for long names.
- These are compatibility hashes, not cryptographic security primitives.

## Testing Signals
Useful tests should verify known ReiserFS hash vectors for `tea`, `rupasov`, and `r5`, including empty names, short names, long names, non-ASCII byte values, and names whose hash maps to directory offset masks.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/hashes.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/ibalance.c -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/ibalance.c

## Purpose
`ibalance.c` executes internal-node balancing plans computed by `fix_node.c`. It mutates internal node key arrays and disk-child pointer arrays for shifts, merges, splits, inserts, deletes, root creation, and root collapse.

## Main Responsibilities
- Copies, inserts, deletes, and moves internal node keys and child pointers.
- Shifts child pointers between `S[h]`, `L[h]`, and `R[h]`.
- Updates delimiting keys in common parents.
- Handles borrowing/merging after deletion.
- Creates a new root when the tree grows.
- Replaces the root and decrements tree height when the old root becomes empty.
- Returns promoted split keys and new child pointers to the next level.

## Key Functions
- `internal_define_dest_src_infos()` maps shift modes to source/destination `buffer_info`, common parent, and delimiting key index.
- `internal_insert_childs()` inserts child pointers and keys into an internal node and updates child-size accounting in the parent.
- `internal_delete_pointers_items()` and `internal_delete_childs()` remove internal pointers/keys and adjust free space.
- `internal_copy_pointers_items()` and `internal_move_pointers_items()` copy/move fixed-size internal records between nodes.
- `internal_shift_left()`, `internal_shift1_left()`, `internal_shift_right()`, and `internal_shift1_right()` implement the concrete left/right transfer operations.
- `balance_internal_when_delete()` executes deletion-specific plans, including root shrink and neighbor borrow/merge.
- `replace_lkey()` and `replace_rkey()` update delimiting keys after leaf/internal boundary changes.
- `balance_internal()` is the public executor for one internal level.

## Data and Control Flow
`balance_internal()` interprets `tb->insert_size[h]` as a count of inserted or deleted internal units. Negative values dispatch to `balance_internal_when_delete()`. Positive values apply any planned left shift, right shift, split, or root creation before inserting remaining keys and child pointers into the current node.

If `tb->blknum[h] == 2`, it obtains an FEB buffer for `S_new`, moves roughly half of `S[h]` into it, and prepares `new_insert_key`/`new_insert_ptr` for the parent level. If no `S[h]` exists, it creates a new root from an FEB buffer and updates the superblock root block and tree height.

## Integration Points
- Consumes `tree_balance` fields filled by `fix_node.c`.
- Uses `buffer_info` helpers and buffer dirtying primitives.
- Uses `replace_key()`, `reiserfs_invalidate_buffer()`, `get_FEB()`, and superblock accessors.
- Feeds promoted keys/pointers back to the caller, normally higher-level balance orchestration.

## Risks and Edge Cases
- All data movement uses raw `memmove`/`memcpy` over packed on-disk arrays; off-by-one errors corrupt tree shape.
- Deletion uses negative `lnum`/`rnum` to mean borrowing from neighbors, while other signs mean shifts/joins. The sign convention is critical.
- New root creation writes into `PATH_OFFSET_PBUFFER(..., ILLEGAL_PATH_ELEMENT_OFFSET)`, so path layout assumptions must match header macros.
- Parent child-size accounting must remain synchronized with internal free space or later planning becomes wrong.

## Testing Signals
Tests should trigger internal left/right shifts, borrow from left/right, merge with left/right, split into `S_new`, create root, collapse root, and insert at boundary positions including `child_pos == -1`.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/ibalance.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/includes.h -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/includes.h

## Purpose
`includes.h` is the shared local include umbrella for `reiserfscore` source files.

## Main Responsibilities
- Includes generated `config.h` when available.
- Pulls in local APIs: `io.h`, `misc.h`, `reiserfs_lib.h`, and `reiserfs_err.h`.
- Pulls in required C/library/system headers used throughout the core implementation.

## Included Dependencies
- Local: `io.h`, `misc.h`, `reiserfs_lib.h`, `reiserfs_err.h`.
- Standard/system: `string.h`, `stdlib.h`, `errno.h`, `asm/types.h`, `fcntl.h`, `malloc.h`, `sys/vfs.h`, `time.h`.

## Integration Points
Most files in this group include `includes.h`, making it the central dependency point for buffer I/O, allocation helpers, on-disk structure accessors, error handling, and ReiserFS type definitions.

## Risks and Edge Cases
- Use of Linux-specific headers such as `asm/types.h` and `sys/vfs.h` narrows portability.
- Including broad headers through a common umbrella can hide per-file dependency requirements.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/includes.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/journal.c -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/journal.c

## Purpose
`journal.c` opens, validates, creates, replays, prints, and closes ReiserFS journals. It handles both standard journals on the filesystem device and non-standard/separate journals.

## Main Responsibilities
- Validates descriptor and commit block pairs.
- Finds oldest/newest valid transactions in the circular journal area.
- Iterates transactions and transaction blocks.
- Replays journal blocks to their in-place filesystem targets.
- Creates journal headers and initializes superblock journal parameters.
- Opens/reopens/closes journal devices and manages `fs_jh_bh`.
- Checks consistency between superblock journal parameters and journal header parameters.
- Advises valid journal transaction sizing.

## Key Functions
- `does_desc_match_commit()` compares descriptor and commit transaction ID/length.
- `commit_expected()` and `next_desc_expected()` calculate circular journal positions.
- `transaction_check_content()` validates descriptor, commit, and target block journalability.
- `transaction_check_desc()` performs descriptor/commit structural validation.
- `get_boundary_transactions()` scans the journal for valid transactions and records oldest/newest by transaction ID.
- `next_transaction()` advances to the next valid transaction up to a boundary transaction.
- `for_each_block()` maps each journal payload block to its in-place target block and calls an action callback.
- `replay_one_transaction()` writes all transaction blocks to their target locations.
- `for_each_transaction()` iterates valid transactions in order.
- `reiserfs_open_journal()` opens the journal device/file and reads the journal header.
- `reiserfs_create_journal()` validates location/size and writes journal parameters into both journal header and superblock.
- `reiserfs_replay_journal()` replays valid post-header transactions and updates the journal header after each replay.

## Data and Control Flow
Journal replay starts with `reiserfs_replay_journal()`, which reads control state from the journal header, scans for boundary transactions, skips transactions already flushed according to header state, then replays contiguous transactions with matching mount ID and incrementing transaction ID. Each replay copies blocks from the journal device to the filesystem device and writes them synchronously.

Transaction block target numbers are split across descriptor and commit blocks: the first half is in descriptor `j2_realblock`, and the remainder is in commit `j3_realblock`.

## Integration Points
- Uses block classification from `node_formats.c`, especially `who_is_this()` and `not_journalable()`.
- Uses buffer I/O primitives from the local `io` layer.
- Uses progress reporting through `progbar.h`.
- Writes superblock fields and marks filesystem dirtiness during journal creation and replay.

## Risks and Edge Cases
- `next_transaction()` loops until it finds a valid descriptor; a badly damaged circular journal could cause long scans.
- Replay refuses non-journalable targets, protecting superblock-before-area and journal blocks.
- Separate journal creation intentionally caps defaults and warns about oversized journals that can make filesystems hard to mount.
- `reiserfs_journal_params_check()` may repair old standard-journal header mismatch by copying superblock parameters into the journal header.
- Several error paths return numeric status codes with different meanings (`-1`, `0`, `1`, `2`), so callers must preserve semantics.

## Testing Signals
Tests should cover standard and separate journal open/create, too-small journals, journal beyond device size, descriptor/commit mismatch, invalid target blocks, no transactions, already-flushed transactions, contiguous replay, broken transaction stop, and parameter mismatch repair.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/lbalance.c -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/lbalance.c

## Purpose
`lbalance.c` executes leaf-node item movement and mutation for ReiserFS balancing. It copies, shifts, merges, splits, inserts, pastes, cuts, and deletes leaf items according to `tree_balance` plans.

## Main Responsibilities
- Copies directory entries between leaf nodes.
- Merges boundary items when adjacent items are mergeable.
- Splits “liquid” direct, indirect, or directory items across nodes.
- Moves items from `S[0]` to left/right/new nodes or between neighbors.
- Inserts whole items into a leaf buffer.
- Pastes bytes or directory-entry space into an existing item.
- Cuts bytes or directory entries from an item.
- Deletes whole items from a leaf.
- Updates item headers, item locations, free-space counters, item counts, parent child sizes, and dirty flags.

## Key Functions
- `leaf_copy_dir_entries()` copies complete directory entries and creates or extends a destination directory item.
- `leaf_copy_boundary_item()` handles mergeable first/last items at node boundaries.
- `leaf_copy_items_entirely()` copies whole item headers and bodies.
- `leaf_item_bottle()` splits part of a direct, indirect, or directory item into another node.
- `leaf_copy_items()` combines boundary merging, whole-item copy, and partial-item copy.
- `leaf_move_items()` copies then deletes items from the source.
- `leaf_shift_left()` and `leaf_shift_right()` move items out of `S[0]` and update delimiting keys.
- `leaf_delete_items()` removes whole or partial items after movement.
- `leaf_insert_into_buf()` inserts a new item header and body into a leaf.
- `leaf_paste_in_buffer()` grows an existing item by bytes.
- `leaf_cut_entries()` and `leaf_cut_from_buffer()` remove directory entries or byte ranges.
- `leaf_paste_entries()` inserts directory entry headers and record bytes.
- `delete_item()` and `cut_entry()` are wrappers for single-buffer operations.

## Data and Control Flow
The file treats leaf node bodies as a compact region growing backward from block end while item headers grow forward after the block header. Insert/paste/cut/delete operations must move body bytes and then fix every affected `ih_location`.

Directory entries are special: the entry header array is at the start of the item body, while names/records are packed from the end backward. Copying and cutting directory entries therefore updates both `deh_location` values and item keys when the first entry changes.

## Integration Points
- Consumes `tree_balance` decisions from `fix_node.c`.
- Uses `replace_key()` to update parent delimiting keys after shifts.
- Uses `are_items_mergeable()` from `fix_node.c`.
- Uses item/key/directory helpers from `node_formats.c`.
- Called by higher-level balancing orchestration when leaf mutations are required.

## Risks and Edge Cases
- Directory entry manipulation is dense and location-sensitive; malformed `deh_location` values can cause overlapping `memmove`.
- Direct item split/merge updates offsets by bytes; indirect item split/merge updates offsets by `UNFM_P_SIZE * blocksize`.
- `leaf_paste_in_buffer()` prepares space for directory entries but leaves actual directory entry header insertion to `leaf_paste_entries()`.
- Boundary item merging can eliminate item headers, so parent child sizes and delimiter keys must stay synchronized.
- Several validation panics call `is_a_leaf()` after mutation, useful for catching corruption but abrupt in production tools.

## Testing Signals
Tests should cover full item copies, left/right boundary merges, directory item splits, direct item splits at head/tail, indirect item splits, insertion at beginning/middle/end, deleting all items, cutting directory entries including first entry key update, and parent child-size accounting.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/lbalance.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/node_formats.c -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/node_formats.c

## Purpose
`node_formats.c` defines core ReiserFS on-disk format recognition, validation, key/type conversion, hash mapping, directory item validation, stat-data access, object-id map manipulation, and block classification helpers.

## Main Responsibilities
- Recognizes leaves, internal nodes, superblocks, journal descriptors, and unknown blocks.
- Validates leaf header/item-header consistency.
- Validates internal node fixed-size layout.
- Handles ReiserFS 3.5, 3.6, and non-standard-journal magic strings.
- Calculates required journal start locations.
- Classifies bitmap, journal, data, and journalable blocks.
- Maps hash codes/names/functions.
- Validates directory entries and indirect items.
- Builds empty directory stat-data and directory item bodies.
- Converts between key formats, offsets, types, and uniqueness values.
- Gets/sets v1/v2 stat-data fields.
- Tracks used object IDs in the superblock object-id map.

## Key Functions
- `leaf_count_ih()`, `leaf_free_space_estimate()`, `is_a_leaf()`, and `leaf_item_number_estimate()` inspect leaf item-header arrays.
- `is_correct_internal()` and `is_tree_node()` validate formatted tree nodes.
- `who_is_this()` classifies a raw block buffer.
- `block_of_journal()`, `block_of_bitmap()`, `not_data_block()`, and `not_journalable()` classify block-number roles.
- `get_journal_start_must()` chooses old/new journal placement based on superblock location.
- `get_bytes_number()` returns logical byte coverage for direct/indirect items.
- `is_properly_hashed()`, `find_hash_in_use()`, `code2name()`, `func2code()`, `code2func()`, and `name2func()` bridge directory hash functions and stored hash codes.
- `is_it_bad_item()` validates stat-data, direct, directory, and indirect item bodies.
- `make_dir_stat_data()`, `make_empty_dir_item_v1()`, and `make_empty_dir_item()` synthesize directory metadata.
- `key_format()`, `get_offset()`, `get_type()`, `set_type()`, `set_offset()`, and `set_type_and_offset()` abstract v1/v2 key layouts.
- `entry_length()`, `name_in_entry()`, and `name_in_entry_length()` decode directory entries.
- `get_set_sd_field()` reads or writes common stat-data fields across old/new formats.
- `is_objectid_used()` and `mark_objectid_used()` query/update the object-id interval map.
- `is_blocksize_correct()` checks supported power-of-two block sizes from 512 to 8192.

## Data and Control Flow
Block classification is layered: superblock magic first, then leaf recognition, internal recognition, journal descriptor magic, then unknown. Leaf recognition distinguishes a fully consistent leaf from a damaged block that still has a plausible item-header array.

Hash detection starts with filesystem hash unset; directory validation tries known hashes against a name and offset, setting `reiserfs_hash(fs)` if exactly one function matches. Ambiguous matches leave the hash unknown but do not necessarily fail the entry.

Object-id map logic treats the superblock tail as alternating busy/free boundaries. `mark_objectid_used()` expands, shrinks, merges, or appends intervals depending on the target object ID and available map space.

## Integration Points
- Used by journal replay for descriptor detection and target block safety.
- Used by balancing code for key offsets, item type, directory entry sizing, and byte coverage.
- Used by print/debug code to decode nodes, superblocks, directories, bitmaps, and object IDs.
- Used by mkfs/fsck-style code to synthesize stat-data and empty directories.

## Risks and Edge Cases
- Directory validation can optionally treat hash mismatch as fatal via `bad_dir`.
- `is_bad_indirect()` delegates block-pointer validation through a callback, so safety depends on caller-provided policy.
- Object-id map updates modify packed superblock data in place and must maintain interval ordering.
- Leaf recognition intentionally tolerates damaged block headers when item-header arrays look plausible, which is useful for repair but risky if callers assume full validity.
- Hash names include quoted strings such as `"tea"`, so callers of `name2func()` must pass matching quoted names.

## Testing Signals
Tests should cover valid/corrupt leaves, internal nodes, journal descriptors, all superblock magic variants, old/new journal starts, bitmap layouts, directory hash detection ambiguity, bad directory locations, indirect item pointer validation, v1/v2 key conversion, stat-data field access, and object-id interval map transitions.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/node_formats.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/prints.c -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/prints.c

## Purpose
`prints.c` implements diagnostic and debug printing for ReiserFS metadata, including custom printf specifiers, item/node dumps, superblock dumps, bitmap dumps, object-id maps, and journal transaction summaries.

## Main Responsibilities
- Registers ReiserFS-specific printf specifiers through glibc printf hooks.
- Prints keys, short keys, item headers, block headers, disk children, modes, and UUIDs.
- Dumps directory items, indirect items, stat-data items, direct item bodies, leaves, internals, and generic blocks.
- Prints superblock and journal parameter details.
- Prints tree-balance state.
- Prints bitmap usage ranges and object-id maps.
- Prints journal headers and transactions.

## Key Functions
- `reiserfs_warning()` lazily registers specifiers `%K`, `%k`, `%H`, `%b`, `%y`, `%M`, and `%U`, then delegates to `vfprintf`.
- `print_directory_item()` prints directory entry names, key targets, hash/generation, location, state, and detected hash function.
- `print_indirect_item()` coalesces consecutive indirect block pointers into compact sequences.
- `print_stat_data()` decodes old and new stat-data layouts and returns whether the item represents a symlink.
- `reiserfs_print_item()` prints one item for debug tooling.
- `print_internal()` and `print_leaf()` dump formatted tree nodes.
- `print_super_block()` prints filesystem format, block counts, clean state, tree height, hash function, object-id map size, journal parameters, fs state, UUID/label, mount-count fields, and check interval.
- `print_block()` dispatches descriptor, superblock, leaf, internal, or unformatted output.
- `print_tb()` dumps `struct tree_balance` buffers and balance parameters.
- `print_bmap()` and `print_bmap_block()` print bitmap block ranges and used/free counts.
- `print_objectid_map()` prints busy/free object-id intervals.
- `print_journal_header()`, `print_one_transaction()`, and `print_journal()` print journal metadata and transaction block mappings.

## Data and Control Flow
Printing generally performs lightweight format recognition before decoding. `print_block()` tries journal descriptor, superblock, leaf, internal, then unknown data. Leaf printing can run in summary mode or detailed mode. In detailed mode it prints every real item and dispatches by item type.

The custom specifier system centralizes formatting for keys and on-disk structures. Most output goes through `reiserfs_warning()`, even for normal diagnostic output, to gain those specifiers.

## Integration Points
- Depends on format helpers from `node_formats.c`.
- Uses journal iteration from `journal.c`.
- Uses misc/device helpers and UUID support when available.
- Used by debug tools and error paths throughout reiserfsprogs.

## Risks and Edge Cases
- Global `is_symlink` state in leaf printing can affect direct-item rendering across items.
- `timestamp()` uses a single static buffer and `localtime()`, so it is not thread-safe.
- Custom printf registration is process-global.
- `reiserfs_print_item()` appears to compute the item index using pointer subtraction divided by `sizeof(struct item_head)`, even though pointer subtraction already returns element count.
- Detailed direct-item printing may emit arbitrary file bytes to the output stream.
- Some `asprintf()` results are checked only through `len == -1`; allocation failure paths are minimal.

## Testing Signals
Tests should cover custom format specifiers, old/new stat-data, directory entries with bad locations, indirect sequence compaction, superblock short/full printing, bitmap spread and packed layouts, object-id maps, journal printing, and `print_block()` dispatch for all recognized block classes.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/prints.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/reiserfscore.pc.in -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/reiserfscore.pc.in

## Purpose
`reiserfscore.pc.in` is the pkg-config template for the ReiserFS core library.

## Contents
- Defines `prefix`, `exec_prefix`, `libdir`, and `includedir` substitution variables.
- Publishes package metadata:
  - `Name: reiserfscore`
  - `Description: ReiserFS Core Library`
  - `Version: @PACKAGE_VERSION@`
- Publishes compile flags:
  - `-I${includedir}/reiserfs -I${includedir}`
- Publishes link flags:
  - `-L${libdir} -lreiserfscore`

## Integration Points
Generated during configure/build and installed for downstream consumers that compile against `libreiserfscore`.

## Risks and Edge Cases
- Consumers rely on both include paths, so installed headers must match `${includedir}/reiserfs` and `${includedir}` expectations.
- The template only links `-lreiserfscore`; if platform-specific dependencies are required, build tooling must add them elsewhere or extend this file.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/reiserfscore.pc.in -->