# Group Research: group_1728_reiserfsprogs_sources_local_fs_reiserfsprogs_Makefile_am_sources_lo_c43f7c200270

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/reiserfsprogs` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/Makefile.am -->
# File Research: sources/local-fs/reiserfsprogs/Makefile.am

This top-level Automake file defines the reiserfsprogs build subtree order: `include`, `lib`, `reiserfscore`, `fsck`, `debugreiserfs`, `resize_reiserfs`, `mkreiserfs`, and `tune`.

It also declares distribution-only files: `CREDITS`, `version.h`, and `reiserfsprogs.spec`.

Key role: root build orchestration only. No runtime logic.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/configure.ac -->
# File Research: sources/local-fs/reiserfsprogs/configure.ac

Autoconf configuration for `reiserfsprogs` version `3.6.27`. It initializes Automake/libtool, config header generation, compiler checks, large-file support, required libraries, warning flags, and output Makefiles/manpage substitutions.

Important checks:
- Requires `libcom_err`; warns if `libuuid` is absent.
- Requires either `register_printf_modifier` or `register_printf_specifier`.
- Forces `_FILE_OFFSET_BITS=64` when large-file detection is inconclusive.
- Checks `off_t` and `blkcnt_t` sizes.
- Adds `-I$(top_srcdir)/include` to `CPPFLAGS`.

Build outputs include all major tool subdirectories: `mkreiserfs`, `resize_reiserfs`, `fsck`, `lib`, root `Makefile`, `reiserfscore`, `debugreiserfs`, and `tune`.

Notable option: `--enable-io-failure-emulation` defines `IO_FAILURE_EMULATION`, but the configure text warns it is debugging-only.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/configure.ac -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/Makefile.am -->
# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/Makefile.am

Builds the `debugreiserfs` sbin program from:
`debugreiserfs.c`, `pack.c`, `unpack.c`, `stat.c`, `corruption.c`, `scan.c`, `recover.c`, and `debugreiserfs.h`.

Links against `$(top_builddir)/reiserfscore/libreiserfscore.la`.

Installs compatibility symlinks:
- `debugfs.reiserfs` -> `debugreiserfs`
- `debugfs.reiserfs.8` -> `debugreiserfs.8`

Key role: packaging/build glue for the debugging and metadata extraction tool.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/corruption.c -->
# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/corruption.c

Implements interactive and scripted ReiserFS corruption injection for testing `reiserfsck`.

Main entry points:
- `do_corrupt_one_block(fs, fline)`: corrupts a selected leaf block or edits the superblock if the target block is the superblock.
- `do_one_corruption_in_one_block(...)`: parses single-letter corruption commands.
- `do_leaves_corruption`, `do_bitmap_corruption`, `do_fs_random_corrupt`: random corruption drivers.

Supported targeted corruptions include:
- Editing superblock and journal parameters.
- Changing hash code.
- Cutting directory entries.
- Clobbering directory-entry hashes.
- Changing item type/format/objectid.
- Breaking indirect item pointers.
- Deleting items.
- Making item key order invalid.
- Corrupting old-format stat-data size/first-direct-byte fields.
- Zeroing bytes in item headers or block headers.

Random corruption modes cover:
- Bitmap blocks.
- Leaf block headers.
- Item headers.
- Directory item bodies.
- Stat-data item bodies.
- Indirect item bodies.

Dependencies:
- Uses `debugreiserfs.h` shared mode/data accessors.
- Relies on `reiserfscore` buffer, bitmap, item, key, and directory helpers.
- Uses global `fs` through macros in some helper paths.

Notable risks/quirks:
- It is intentionally destructive and opens the filesystem read-write.
- `corrupt_block_header` ignores the requested offset when calling `memset`; it zeroes from the block header start.
- Many command parsers use loose bounds checks such as `item_num > nr_items`, allowing `item_num == nr_items`.
- Random functions repeatedly seed with `time(NULL)`, reducing randomness if invoked close together.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/corruption.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/debugreiserfs.8.in -->
# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/debugreiserfs.8.in

Manual page template for `debugreiserfs`.

Documents primary modes:
- Default: print filesystem superblock.
- `-j device`: print journal contents.
- `-J`: print journal header.
- `-d`: print formatted tree nodes.
- `-D`: print formatted used blocks.
- `-m`: print bitmap.
- `-o`: print objectid map.
- `-B file`: extract internal bad-block list.
- `-1 block`: print one filesystem block.
- `-p`: pack filesystem metadata to stdout.
- `-u`: unpack packed metadata into an image.
- `-S`: scan entire device instead of bitmap-used blocks.
- `-q`: quiet progress output.
- `-V`: version.

Important behavioral note: `-p` is intended to pack metadata, not file contents, except when corrupt blocks must be copied whole. `-u` recreates filesystem structure from that metadata but not necessarily original data.

Author listed: Vitaly Fertman.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/debugreiserfs.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/debugreiserfs.c -->
# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/debugreiserfs.c

Main program for `debugreiserfs`.

Core responsibilities:
- Parses documented and hidden command-line options.
- Opens the ReiserFS filesystem and journal.
- Dispatches to dump, pack, unpack, corruption, scan, recover, stat, bad-block extraction, and zeroing modes.
- Initializes scan bitmaps from on-disk bitmap, full device, unused blocks, or an external bitmap file.

Important modes:
- `DO_DUMP`: print superblock, filesystem state, optional journal/objectid/bitmap/tree details.
- `DO_PACK`: call `pack_partition` or `pack_one_block`.
- `DO_UNPACK`: call `do_unpack` before opening a filesystem.
- `DO_SCAN`, `DO_SCAN_FOR_NAME`, `DO_LOOK_FOR_NAME`, `DO_SCAN_JOURNAL`: initialize bitmap then call `do_scan`.
- `DO_CORRUPT_ONE`, `DO_CORRUPT_FILE`, `DO_RANDOM_CORRUPTION`: reopen read-write and corrupt.
- `DO_EXTRACT_BADBLOCKS`: walk internal bad-block list and write block numbers.
- `DO_ZERO`: zero all blocks selected by the scan bitmap.

Key helpers:
- `print_disk_tree`: recursive internal-tree printer and block statistics collector.
- `print_disk_blocks`: scans selected bitmap blocks and prints recognizable ReiserFS metadata.
- `print_one_block`: reports bitmap use state and prints or packs one block.
- `init_bitmap`: shared scan-area setup.

Notable risks/quirks:
- Hidden/undocumented options expose experimental scan/map/recover behavior.
- `do_corrupt_blocks` prints debug messages around `free(line)`.
- `debugreiserfs_zero_reiserfs` destructively zeroes selected blocks.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/debugreiserfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/debugreiserfs.h -->
# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/debugreiserfs.h

Shared header for `debugreiserfs`.

Defines:
- Operation modes such as dump, corrupt, scan, recover, pack, unpack, stat, bad-block extraction, file-map, and zero.
- Print/behavior option bits.
- Binary pack format magic values for leaves, full blocks, unformatted bitmap, map records, separated journals, and stream end.
- Packed-item bit masks describing which key/item fields are serialized.
- Packed directory-entry format and masks.
- `struct debugreiserfs_data`, stored in `fs->fs_vp`.
- Accessor macros such as `debug_mode(fs)`, `scan_area(fs)`, `map_file(fs)`, and `be_quiet(fs)`.
- Cross-file function prototypes for stat, corruption, recover, scan, unpack, and map printing.
- `struct saved_item`, used by scan/recover map workflows.

Important format detail: `struct packed_item` compresses item type, mask, and item length into one 32-bit field using bitfield helper macros.

Notable quirks:
- `INTERNAL_START_MAGIC` is defined twice without a value.
- `fread8` is defined twice.
- Serialization macros increment global `sent_bytes`, tying the header tightly to `pack.c`.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/debugreiserfs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/pack.c -->
# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/pack.c

Implements `debugreiserfs -p` metadata packing.

Pack stream layout:
- ReiserFS magic.
- Block size.
- Packed superblock, bitmap blocks, journal blocks.
- Remaining selected metadata blocks.
- End magic.

Packing strategy:
- Leaves are compacted item-by-item when structurally valid.
- Suspicious/corrupt leaves, internal nodes, superblock, bitmap blocks, journal blocks, and unknown blocks requested as mandatory are emitted as full blocks.
- Blocks are cleared from `what_to_pack` after serialization to avoid duplicates.

Leaf item packing:
- Common key fields are omitted when inferable from prior item.
- Offsets may be omitted, stored as 32-bit, or stored as 64-bit.
- Direct items generally omit contents and are later reconstructed as filler, except safe links.
- Indirect items may be serialized whole or compressed as extents/runs.
- Directory items serialize entries, names, object ids, and optional dirid/generation/state.
- Stat data serializes compact old/new stat-data fields.

Journal support:
- Packs internal/default journal from filesystem journal area.
- Supports separated journal markers when a non-standard journal device is supplied.
- Warns and requires confirmation if a separate journal exists but was not specified.

Global counters report compressed leaves, full blocks, bad leaves, internals, and compression ratio.

Notable risks/quirks:
- Internal-node compact packing is stubbed; internals are always full-block packed.
- `descs` and `others` counters are declared but not meaningfully populated.
- Compact direct-item reconstruction loses real file data by design.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/pack.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/recover.c -->
# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/recover.c

Implements the live `do_recover` path for recovering file contents from saved item maps.

The older stdin text-map recovery implementation is disabled with `#if 0`. A second older binary map reader is also commented out.

Live behavior:
- Reads `struct saved_item` records from `map_file(fs)` or stdin.
- Opens `recovery_file(fs)` for output.
- Reconstructs a file by reading each saved item’s source block and item index.
- For direct items, writes item body bytes at key offset.
- For indirect items, reads each unformatted block pointer and writes pointed block data.
- Handles overlapping/problem item ranges interactively by printing candidate items and asking which should be left.

Dependencies:
- Uses `struct saved_item` from `debugreiserfs.h`.
- Uses item/key helpers from `reiserfscore`.

Notable risks/quirks:
- The saved-item file is raw native struct data minus the pointer field, so it is ABI/endian/layout fragile.
- Uses interactive stdin selection for overlaps.
- Opens recovery output with `"w+"`, truncating existing files.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/recover.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/scan.c -->
# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/scan.c

Implements scanning by filename pattern, key, name lookup, item-map saving, and map printing.

Primary flows:
- `DO_SCAN_FOR_NAME`: regex-scan selected blocks for directory entries matching a name pattern, index names by name and pointed key, then scan for matching file items.
- `DO_SCAN`: prompt for dirid/objectid and scan selected blocks for matching items or directory entries.
- `DO_LOOK_FOR_NAME`: interactively search a directory using tree lookup, locate the file, and flush a map.
- `DO_FILE_MAP`: print previously saved item records.

Data structures:
- `saved_name`: stores found names, parent directory key, pointed object key, occurrence count, item tree, and duplicate-name chain.
- `saved_item`: records item header, block number, item index, and entry position.
- `file_map`: experimental in-memory layout with indirect block head and direct-item tails.

Storage/indexing:
- Uses GNU obstacks for name/item allocation.
- Uses `tsearch`/`tfind` trees for name, key, and item indexing.
- Writes one map file per matched name as `<map_file>.<n>` when `-a` is supplied.

Notable disabled code:
- Older richer `MAP_MAGIC` file-map writer is commented out.
- Current `make_map` writes raw `saved_item` records instead.

Notable risks/quirks:
- Produces `scan.log` unconditionally.
- Regex uses basic `regcomp` flags.
- Some map code is marked as not working for long files.
- Raw saved-item serialization is not portable.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/scan.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/stat.c -->
# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/stat.c

Implements `debugreiserfs -t` statistics over selected blocks.

Behavior:
- Initializes an obstack and binary tree of unique item headers.
- Scans the input bitmap.
- Keeps only blocks that look like leaves or broken-header leaves with item arrays.
- Counts total items, unique items, leaves, skippable blocks, and item types.
- Clears bitmap bits for non-leaf blocks and leaf blocks containing no unique items.
- If an input bitmap filename was supplied, saves the updated bitmap back to that file.

Uniqueness comparison uses key ordering plus item length and entry count.

Purpose: identify duplicate/redundant leaf content and optionally produce a reduced bitmap for later pack/scan operations.

Notable quirks:
- Comments say statistics do not fully work.
- A second pass is unreachable because the function returns before it.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/stat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/unpack.c -->
# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/unpack.c

Implements `debugreiserfs -u`, reconstructing a filesystem image from the custom pack stream produced by `pack.c`.

Main flow:
- `do_unpack(host, journal_filename, bitmap_filename, verbose)` opens target device/image and optional separated journal target.
- `unpack_partition` validates stream magic and block size, then consumes records until `END_MAGIC`.
- Full-block records are written verbatim.
- Compact leaf records are reconstructed into block headers, item headers, directory entries, stat data, indirect items, and filler direct item bodies.
- A bitmap of unpacked blocks is created when the superblock is encountered and saved at the end.

Supported record types:
- Compact leaves.
- Full blocks.
- Separated journal start/end.
- Unformatted bitmap records, which are skipped.
- End marker.

Reconstruction details:
- Directory entry hashes are recalculated from serialized names when a hash function is available.
- Direct item data is replaced with `'a'` bytes unless it is a safe link.
- Indirect items are expanded from whole arrays or run-compressed pointer sequences.
- Stat data supports old and new formats with compact nlink/size encodings.

Notable risks/quirks:
- Ignores progress text embedded in streams by skipping percent-like tokens.
- Requires separated journal filename if separated journal records are present.
- The output image recreates metadata structure, not original file contents.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/debugreiserfs/unpack.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/Makefile.am -->
# File Research: sources/local-fs/reiserfsprogs/fsck/Makefile.am

Builds the `reiserfsck` sbin program.

Source set includes the main driver, rebuild passes, semantic checks, lost+found handling, bitmap/objectid/tree/file helpers, superblock repair, and `fsck.h`.

Links against `$(top_builddir)/reiserfscore/libreiserfscore.la`.

Installs compatibility symlinks:
- `fsck.reiserfs` -> `reiserfsck`
- `fsck.reiserfs.8` -> `reiserfsck.8`

Key role: build glue for the filesystem checker/repair utility.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/check_tree.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/check_tree.c

Core tree-consistency checker for `reiserfsck --check`, `--fix-fixable`, and auto checks.

Main entry point:
- `check_fs_tree(fs)`

Core algorithm:
- Builds a `control_bitmap` representing blocks legitimately used by metadata, journal/reserved area, bad blocks, tree nodes, and unformatted data pointers.
- Copies the on-disk bitmap into `source_bitmap`.
- Walks the internal tree with `pass_through_tree`.
- Validates every internal node, leaf, item, item order, delimiter key, child size, and block pointer.
- Compares reconstructed usage against on-disk bitmap and superblock free-block count.

Validation coverage:
- Internal node key order and child block legality.
- Leaf structure through `leaf_structure_check`.
- Item flags and key-format consistency.
- Bad-block list item structure and pointers.
- Safe-link item patterns.
- Stat-data objectid allocation/sharing.
- Indirect item length and unformatted pointers.
- Directory item entry counts, locations, name lengths, hash order, and visible state.
- Neighbor item ordering and allowed per-file sequences.
- Left/right delimiting keys and parent child-size accounting.

Fixable actions in `FSCK_FIX_FIXABLE`:
- Clean item-header flags.
- Correct item key format.
- Zero bad indirect/badblock pointers.
- Normalize directory-entry state.
- Correct internal child-size fields.
- Merge control bitmap usage into source bitmap and update superblock free count.

Fatal conditions generally require `--rebuild-tree`.

Additional entry point:
- `do_clean_attributes(fs)`: clears v2 stat-data attribute fields across leaves and marks the superblock `reiserfs_attrs_cleared`.

Notable quirks:
- Some historical relocation/fix helpers are disabled.
- A log call in the wrong-key error path appears to pass block/item arguments in swapped order.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/check_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/fsck.h -->
# File Research: sources/local-fs/reiserfsprogs/fsck/fsck.h

Shared header for `reiserfsck`.

Defines:
- Exit codes.
- Fsck modes: check, fix-fixable, rebuild superblock, rebuild tree, rollback, clean attributes, auto.
- Option flags: interactive, adjust-size, quiet, silent, background, skip journal, hash-defined, pass dump, rollback, yes, badblocks, force.
- Cross-pass function prototypes for pass0/pass1/pass2/semantic/lost+found/pass4, tree checking, bitmap allocation, objectid maps, rollback, and superblock rebuild.
- Rebuild/check statistics structures.
- `struct rebuild_info`, `struct check_info`, and `struct fsck_data`, stored in `fs->fs_vp`.
- Convenience macros for accessing pass stats, bitmaps, mode/options, logs, progress streams, and objectid maps.

Important shared state:
- Rebuild uses source/new/allocable/uninsertable bitmaps.
- Check uses corruption counters plus a deallocation bitmap.
- Objectid maps track proper and semantic allocation/relocation state.
- Progress output may go to stderr or `fsck.run`.

Macros:
- `fsck_log` suppresses messages under `OPT_SILENT`.
- `fsck_progress` writes and flushes progress output.
- `fsck_exit` reports and exits with user error.

Key role: central contract tying all fsck passes and main orchestration together.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/fsck.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/info.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/info.c

Contains user interaction and stage reporting helpers.

Functions:
- `fsck_user_confirmed(fs, q, a, default_answer)`: asks only in interactive mode; otherwise returns the supplied default.
- `stage_report(pass, fs)`: prints statistics for rebuild/check stages and then clears the rebuild stats union.

Reported stages:
- Pass 0: scanned blocks, leaves, corrected/skipped leaves, wrong pointers, objectids.
- Pass 1: leaves read/inserted, metadata pointers zeroed, saved items, uninsertable leaves, non-unique pointers.
- Pass 2: item-by-item inserted leaves, shared objectids, relocated/rewritten files.
- Semantic pass: files, directories, symlinks, broken files, fixed sizes, deleted names, objectid sharing.
- Lost+found pass: recovered/lost objects, linked dirs/files, relocated objectid-sharing objects.
- Pass 4: deleted unreachable items.
- Final check stats: leaves, internals, dirs, files, data pointers, zero pointers, safe links.

Key role: centralized human-readable fsck progress summaries.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/info.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/lost+found.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/lost+found.c

Implements rebuild-tree pass 3a: linking unreachable directories/files into `/lost+found`.

Main flow:
- `_look_for_lost(fs, link_lost_dirs)` scans tree items marked unreachable.
- First pass links lost directories.
- Second pass links lost regular files.
- `pass_3a_look_for_lost(fs)` updates `/lost+found` size, blocks, and mode, then flushes metadata.

Behavior:
- Skips already reachable items.
- Recovers missing directory stat data when a directory item exists without stat data.
- Avoids linking empty lost directories.
- Handles objectid sharing by relocating directories or rewriting files.
- Adds entries named `<dirid>_<objectid>` under `/lost+found`.
- Runs semantic rebuild on linked directories and regular-file validation on linked files.
- Marks recovered file stat data reachable.

State handling:
- `load_lost_found_result` initializes new/allocable bitmaps and objectid maps when resuming from a dump.
- `save_lost_found_result` writes a stage marker file.
- `after_lost_found` updates superblock fsck state, flushes objectid map/bitmap, prints stage report, and either exits or continues.

Notable details:
- Sets `/lost+found` mode to `drwx------`.
- Uses `semantic_id_map` to detect objectid reuse during recovery.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/lost+found.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/main.c -->
# File Research: sources/local-fs/reiserfsprogs/fsck/main.c

Main program and orchestrator for `reiserfsck`.

Command-line modes:
- `--check`
- `--fix-fixable`
- `--rebuild-sb`
- `--rebuild-tree`
- `--rollback-fsck-changes`
- `--clean-attributes`
- auto modes `-a` / `-p`
- version/no-op mode `-V`

Important options:
- Journal device, bad-block file, logfile/nolog, adjust-size, quiet, yes, force.
- Hidden/expert options include external bitmap scan, pass dump, whole-partition scan, hash override, rollback data, background mode, and no-journal-available.

Major orchestration:
- `parse_options`: validates mode/option combinations and fills `fsck_data`.
- `warn_what_will_be_done`: prints mode-specific warnings and asks for confirmation.
- `prepare_fs_for_check`: reopens read-write, rejects rw-mounted filesystems, handles ro-mounted restrictions, checks/replays journal.
- `check_fs`: standard check/fix-fixable path; opens bitmap, calls `check_fs_tree`, runs `semantic_check`, updates fs state and exit code.
- `auto_check`: lightweight boot-time check based on superblock state, clean unmount state, mount count, check interval, bitmap sanity, and root-tree scan.
- `rebuild_tree`: runs pass0, pass1, pass2, semantic pass, lost+found, and pass4, with resume support.
- `clean_attributes`: validates filesystem state and format, then clears stat-data attribute garbage.
- `fsck_rollback`: restores saved rollback blocks.
- `main`: sets terminal width, rlimit, background handling, opens filesystem/journal/badblocks, registers DMA monitoring, and dispatches mode.

Safety/integrity behavior:
- Replays journal before checks when possible and unmounted.
- Refuses rw-mounted filesystems.
- Locks memory when modifying ro-mounted filesystems.
- Marks fatal/error/consistent states in the superblock.
- Updates v2 last-check, mount count, max mount count, and check interval on success.
- Monitors DMA mode/speed changes and warns about hardware issues.

Rebuild resume:
- Uses superblock fsck state and pass dump magic to resume from pass0, pass1, tree-built, semantic, lost+found, or pass4 states.

Notable risks/quirks:
- Uses intentional switch fallthrough in `rebuild_tree` to continue passes.
- Background mode forks but still warns that confirmations may be needed from stdin.
- Auto check may switch into fix-fixable mode by falling through after `auto_check`.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/fsck/main.c -->