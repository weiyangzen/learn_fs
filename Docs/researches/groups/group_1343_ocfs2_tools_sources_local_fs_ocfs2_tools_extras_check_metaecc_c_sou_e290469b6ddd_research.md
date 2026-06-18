# Group Research: group_1343_ocfs2_tools_sources_local_fs_ocfs2_tools_extras_check_metaecc_c_sou_e290469b6ddd

Scope: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/check_metaecc.c -->
# File Research: sources/local-fs/ocfs2-tools/extras/check_metaecc.c

Read coverage: complete file read, 292 lines.

Purpose: standalone diagnostic utility for checking OCFS2 metadata block CRC/ECC state on a device.

Behavior:
- Parses `check_metaecc [-F|--force] <device> <block #>`.
- Opens the OCFS2 volume read-only with `ocfs2_open()`.
- Refuses to continue if the volume lacks the metaecc feature unless `--force` is supplied.
- Reads one raw block and identifies its metadata type by signature: superblock, inode, extent block, group descriptor, xattr block, refcount block, dx root/leaf, or directory trailer.
- Extracts the appropriate `ocfs2_block_check` field, clears it in the temporary buffer, recalculates CRC32, then tries hamming ECC fixup if CRC does not match.
- Prints `PASS`, `ECC Fixup`, or `FAIL` plus calculated CRC/ECC values.

Important dependencies: `libocfs2`, OCFS2 on-disk metadata signatures, byteorder helpers, `crc32_le()`, `ocfs2_hamming_encode_block()`, and `ocfs2_hamming_fix_block()`.

Risk notes:
- The program mutates only its in-memory block buffer, not the device.
- Return handling has a bug-like shape: `ret` is initialized to `1` and is never set to success after a passing check, so the process may still exit nonzero.
- Unknown metadata signatures are only checked as directory trailers when directory trailers are supported.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/check_metaecc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/compute_groups.c -->
# File Research: sources/local-fs/ocfs2-tools/extras/compute_groups.c

Read coverage: complete file read, 79 lines.

Purpose: prints predicted OCFS2 group descriptor byte offsets for block-size and cluster-size combinations over a given device size.

Behavior:
- Optional argument overrides the default 2 TiB maximum size.
- Iterates block sizes from 512 bytes through 4096 bytes and cluster sizes from 4 KiB through 1 MiB.
- Uses `ocfs2_group_bitmap_size()` to compute clusters per group for each block size.
- Emits rows of byte offset, cluster-size string, and block-size string.

Dependencies: `libocfs2` group bitmap sizing helper and basic stdio/inttypes.

Risk notes:
- It is a calculation helper; it does not open or modify a filesystem.
- Input size is accepted via `strtoull()` without validation beyond conversion.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/compute_groups.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/decode_lockres.c -->
# File Research: sources/local-fs/ocfs2-tools/extras/decode_lockres.c

Read coverage: complete file read, 149 lines.

Purpose: decodes OCFS2 DLM lock resource names into human-readable lock type, block number, and generation.

Behavior:
- Accepts one or more lockres strings.
- Validates exact OCFS2 lock id length and lock type character.
- Supports metadata, data, superblock, rename, and read/write lock types.
- Parses the 16-hex-digit block number and 8-hex-digit generation from the fixed-format lock name.

Dependencies: local copy of OCFS2 kernel lock-name constants and type characters.

Risk notes:
- The lock format is pasted into the utility; if kernel lock-name encoding changes, this tool can drift.
- It validates length/type but not that pad bytes are exactly `000000`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/decode_lockres.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/encode_lockres.c -->
# File Research: sources/local-fs/ocfs2-tools/extras/encode_lockres.c

Read coverage: complete file read, 96 lines.

Purpose: encodes an OCFS2 DLM lock resource name from lock type, block number, and generation.

Behavior:
- Usage: `encode_lockres [M|D|S] [blkno] [generation]`.
- Validates the requested type against metadata, data, and superblock types.
- Formats the lock resource as type + six zero pad bytes + 16 hex digits of block number + 8 hex digits of generation.

Dependencies: local copy of an older/smaller OCFS2 kernel lock-name enum.

Risk notes:
- Encoder supports only `M`, `D`, and `S`, while `decode_lockres.c` also knows rename and read/write locks.
- Uses `atoll()` for numeric input, so malformed strings can silently become zero.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/encode_lockres.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/find_allocation_fragments.c -->
# File Research: sources/local-fs/ocfs2-tools/extras/find_allocation_fragments.c

Read coverage: complete file read, 239 lines.

Purpose: scans an OCFS2 chain allocator inode and reports contiguous free-bit fragments in its group descriptors.

Behavior:
- Usage: `find_allocation_fragments <device> <allocator_inode_block>`.
- Opens the volume read-only.
- Validates that the target inode has bitmap, chain, system, and valid flags.
- Walks each chain list entry and follows linked group descriptors.
- Finds clear-bit runs in each group bitmap, prints run length, bit offset, and group block.
- Tracks the largest free extent and builds a small histogram for free runs under 200 bits.

Dependencies: `libocfs2` inode/group descriptor reads, chain-list structures, and bitmap bit-search helpers.

Risk notes:
- Read-only diagnostic.
- It trusts chain traversal except for library read validation; a corrupted loop could lead to repeated traversal depending on lower-level safeguards.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/find_allocation_fragments.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/find_dup_extents.c -->
# File Research: sources/local-fs/ocfs2-tools/extras/find_dup_extents.c

Read coverage: complete file read, 287 lines.

Purpose: scans all valid inodes and reports data clusters claimed by more than one extent tree.

Behavior:
- Opens the volume read-only.
- Creates a cluster bitmap for seen extents and another for duplicate clusters.
- First inode scan marks every data extent cluster and records duplicate cluster bits.
- If duplicates were found, a second inode scan reports each inode and cluster that intersects the duplicate bitmap.
- Skips invalid inodes, selected system metadata inodes, and fast symlinks without allocated clusters.

Dependencies: OCFS2 inode scanner, extent iterator, cluster bitmap APIs, `ocfs2_rec_clusters()`, and block-to-cluster conversion.

Risk notes:
- Read-only diagnostic.
- Main exits `0` even on some scan/open errors after printing `com_err()`, so shell callers cannot rely on status alone.
- It reports duplicate physical clusters but does not resolve whether they are legitimate refcounted/reflink sharing.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/find_dup_extents.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/find_hardlinks.c -->
# File Research: sources/local-fs/ocfs2-tools/extras/find_hardlinks.c

Read coverage: complete file read, 281 lines.

Purpose: walks system and root directory trees to find directory entries that reference the same inode more than once.

Behavior:
- Usage: `find_hardlinks <device-or-image> [-q]`.
- Opens the volume read-only.
- Builds an inode bitmap and duplicate-inode bitmap while recursively walking directories.
- Skips `.` and `..`; appends `/` to displayed directory paths.
- Seeds system directory and root directory inodes into the seen bitmap.
- If duplicates are found, performs a second walk and prints all paths whose inode is in the duplicate bitmap.

Dependencies: `ocfs2_dir_iterate()`, OCFS2 directory entry types, block bitmap APIs.

Risk notes:
- Read-only diagnostic.
- Recursion follows directory entries directly and assumes directory graph sanity; severe directory loops could cause repeated recursion.
- Path buffers are fixed at 4096 bytes; longer paths abort that directory walk.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/find_hardlinks.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/find_inode_paths.c -->
# File Research: sources/local-fs/ocfs2-tools/extras/find_inode_paths.c

Read coverage: complete file read, 207 lines.

Purpose: finds all directory paths pointing to a requested inode block number.

Behavior:
- Usage: `find_inode_paths <device-or-image> <inode #>`.
- Opens the volume read-only.
- Recursively walks the system directory and root directory.
- Prints `[found] <inode> <path>` for every matching directory entry.
- Has trace-printing support but `quiet` is hard-coded on in `main()`.

Dependencies: `ocfs2_dir_iterate()`, OCFS2 superblock root/system directory block fields, and libocfs2 allocation helpers.

Risk notes:
- Read-only diagnostic.
- Fixed 4096-byte path buffer.
- Does not guard against cycles beyond whatever directory iterator and on-disk structure provide.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/find_inode_paths.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/mark_journal_dirty.c -->
# File Research: sources/local-fs/ocfs2-tools/extras/mark_journal_dirty.c

Read coverage: complete file read, 263 lines.

Purpose: destructive test/maintenance helper that assigns a node to a slot and marks that slot journal dirty.

Behavior:
- Usage: `mark_journal_dirty <device> <node #> <slot #>`.
- Opens the filesystem read-write.
- Reads the slot map system file, rejects duplicate node entries, writes the supplied node number into the requested slot, and writes the backing slot-map data block directly.
- Looks up the requested slot journal inode.
- Sets `OCFS2_JOURNAL_DIRTY_FL` in the journal inode and writes it back.

Dependencies: `ocfs2_lookup_system_inode()`, `ocfs2_read_whole_file()`, raw slot-map layout, inode read/write helpers, byteorder conversion.

Risk notes:
- This is write-capable and can intentionally make a filesystem require journal recovery.
- Slot bounds are not explicitly checked against `s_max_slots` before `slots[slot]` assignment.
- Main exits `0` even when several operations fail after logging errors.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/mark_journal_dirty.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/resize_slotmap.c -->
# File Research: sources/local-fs/ocfs2-tools/extras/resize_slotmap.c

Read coverage: complete file read, 185 lines.

Purpose: write-capable utility to change the logical size of the OCFS2 `//slotmap` system file.

Behavior:
- Usage: `resize_slotmap <device> <size>`.
- Warns that running against a mounted filesystem can damage it and asks for confirmation.
- Opens the volume read-write.
- Looks up and reads the slot-map system inode.
- Validates it is a valid system inode.
- Rejects requested sizes larger than allocated clusters or smaller than `OCFS2_MAX_SLOTS * sizeof(struct ocfs2_extended_slot)`.
- Asks for a second confirmation, then updates `i_size` and `i_mtime`.

Dependencies: cached inode APIs, slot-map system inode lookup, OCFS2 byte/cluster conversion.

Risk notes:
- Direct metadata mutation; intended for offline use.
- The file contains an unused `INSTALL_SIGNAL` macro referencing `handle_signal`, but no signal handler is defined or installed.
- Exits `0` even when resize/open errors are reported.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/resize_slotmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/set_random_bits.c -->
# File Research: sources/local-fs/ocfs2-tools/extras/set_random_bits.c

Read coverage: complete file read, 225 lines.

Purpose: destructive test helper that sets an alternating bit pattern in the global bitmap or another bitmap inode.

Behavior:
- Usage: `set_random_bits [-i <inode_blkno>] <device>`.
- Opens the volume read-write.
- Defaults to the global bitmap system inode if `-i` is not supplied.
- Walks all blocks in the target inode with `ocfs2_block_iterate()`.
- ORs every 32-bit word with `0x55555555`, counts set bits, writes each bitmap block back, then updates the bitmap inode's `i_used` count.

Dependencies: block iteration, raw block I/O, system inode lookup, OCFS2 bitmap inode layout.

Risk notes:
- Intentionally corrupts/changes allocation bitmaps; only suitable for controlled testing.
- It never clears bits, so it only increases apparent allocation.
- Main exits `0` even on many errors.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/set_random_bits.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/verify_backup_super -->
# File Research: sources/local-fs/ocfs2-tools/extras/verify_backup_super

Read coverage: complete file read, 159 lines.

Purpose: shell helper that finds filesystem objects occupying clusters reserved for OCFS2 backup superblocks, useful before enabling backup superblocks retroactively.

Behavior:
- Requires `debugfs.ocfs2`, `awk`, `seq`, `tee`, and `date`.
- Reads block-size bits, cluster-size bits, and cluster count from `debugfs.ocfs2 -R stats`.
- Verifies `debugfs.ocfs2` version is at least 1.2.3.
- Exits early if the BackupSuper compat feature is already enabled.
- Converts fixed backup-super offsets from 512-byte sectors to filesystem blocks.
- Runs `debugfs.ocfs2 -R "icheck ..."` to find inodes using those blocks.
- If any are found, runs `debugfs.ocfs2 -R "findpath ..."` to map inodes to names.

Dependencies: external OCFS2 debugfs command and shell arithmetic.

Risk notes:
- Read-only script.
- Uses `/tmp/__${timestamp}__` without cleanup or collision hardening.
- The `get_sizes()` empty checks use `-a` string tests in a suspicious way, but intent is to reject missing stats.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/verify_backup_super -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/watch-hb.sh -->
# File Research: sources/local-fs/ocfs2-tools/extras/watch-hb.sh

Read coverage: complete file read, 40 lines.

Purpose: watches OCFS2 heartbeat data through `debugfs.ocfs2`.

Behavior:
- Accepts either `-r <region>` or `-d <device>`.
- For a region, reads `$region/dev` and tries to read a slot-byte attribute; for direct device mode, uses 512-byte slots.
- Runs `watch -n 3 -d` around a pipeline that cats `//heartbeat` through `debugfs.ocfs2 -n`, formats it with `od`, and filters slot-aligned rows with `awk`.

Dependencies: `watch`, `debugfs.ocfs2`, `od`, `awk`, shell `/sys`-style heartbeat region files.

Risk notes:
- Read-only display helper.
- The region branch references `$attr` without setting it in this script, so region mode likely depends on external environment or is broken.
- Uses `eval` unnecessarily for simple assignments.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/watch-hb.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/Makefile

Read coverage: complete file read, 113 lines.

Purpose: builds and installs `fsck.ocfs2` plus its man pages.

Behavior:
- Defines `fsck.ocfs2` as an sbin program.
- Builds from core fsck sources: main driver, directory helpers, extent checking, inode counts, journal replay/checking, passes 0-5, problem prompts, refcount, slot recovery, strings, util, and xattr.
- Links against `libocfs2`, `libo2dlm`, `libo2cb`, `libtools-internal`, com_err, and AIO libraries.
- Adds cluster-stack libraries conditionally for fsdlm/cmap support.
- Uses static linking unless `OCFS2_DYNAMIC_FSCK` is set.
- Generates `prompt-codes.h` by parsing `.SS "CODE"` sections from `fsck.ocfs2.checks.8.in`.
- Provides `check-prompt-dups` to detect duplicate prompt code call sites in the binary.

Risk notes:
- The manual page is part of the build contract: undocumented prompt codes will fail to generate the expected define.
- `prompt-codes.h` is generated in the source directory and cleaned by `o2fsck-clean`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/dirblocks.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/dirblocks.c

Read coverage: complete file read, 260 lines.

Purpose: maintains fsck's in-memory red-black tree of directory data blocks and directory inodes requiring directory-index rebuild.

Behavior:
- `o2fsck_add_dir_block()` inserts a directory block record keyed by block number.
- `o2fsck_dir_block_iterate()` walks records in block order and optionally readaheads batches of up to 1024 directory blocks through vector I/O.
- Readahead is skipped if no I/O channel exists or cache size is too small.
- `o2fsck_search_reidx_dir()` and `o2fsck_try_add_reidx_dir()` manage a second rb-tree keyed by directory inode number.
- `o2fsck_rebuild_indexed_dirs()` truncates and rebuilds indexed directory trees for queued non-inline directories.

Dependencies: kernel-style rbtrees, libocfs2 malloc/free, `io_vec_read_blocks()`, `ocfs2_dx_dir_truncate()`, `ocfs2_dx_dir_build()`.

Risk notes:
- Insert logic assumes no duplicate directory block keys; equal keys leave the search loop without moving `p`, which would be unsafe if duplicates are inserted.
- Rebuild skips inline directories and expects index corruption decisions to be made by pass logic.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/dirblocks.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/dirparents.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/dirparents.c

Read coverage: complete file read, 153 lines.

Purpose: records directory parent relationships discovered during fsck so pass 3 can verify directory connectivity and `..` correctness.

Behavior:
- Stores `o2fsck_dir_parent` nodes in an rb-tree keyed by directory inode.
- Each record tracks the directory inode, its `..` target, the parent directory entry that points to it, connection status, loop number, and orphan-dir membership.
- Provides add, lookup, first, next, and remove helpers.

Dependencies: kernel-style rbtrees and pass-level directory metadata collection.

Risk notes:
- Add path assumes callers prevent duplicate directory inodes; duplicates return internal failure.
- Uses `calloc/free` directly rather than libocfs2 allocation wrappers.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/dirparents.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/extent.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/extent.c

Read coverage: complete file read, 495 lines.

Purpose: verifies and optionally repairs OCFS2 extent trees hanging from inodes during fsck pass 1.

Behavior:
- `check_eb()` reads extent blocks without full validation, checks block number and filesystem generation, optionally invalidates or fixes them, then checks their embedded extent list.
- `check_el()` validates list depth, count, next-free record, record cpos ordering, hole policy, out-of-range blocks, and recursively descends interior records.
- `check_er()` checks individual records, delegates leaf-record validation, and clears invalid extent-block references when prompted.
- `o2fsck_check_extent_rec()` fixes unaligned physical block starts, truncates extents that overrun the volume, clears unsupported unwritten/refcounted flags.
- Leaf data extents are marked allocated or refcounted through `o2fsck_mark_tree_clusters_allocated()`.
- `o2fsck_check_extents()` wires inode-specific callbacks and also corrects directory `i_size` when extents describe less data than recorded; it clears indexed-dir state so pass 2 can rebuild indexes.

Dependencies: prompt framework, OCFS2 extent list/record helpers, refcount tracking, allocation bitmap marking, inode writeback helper.

Risk notes:
- Many fixes can truncate data or drop invalid subtree references, but every mutation goes through `prompt()`.
- The file deliberately treats read failures differently from bad extent-block magic.
- Directory index clearing does not directly free index blocks; later fsck accounting/reclaim is expected to handle them.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/extent.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/fsck.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/fsck.c

Read coverage: complete file read, 1163 lines.

Purpose: main `fsck.ocfs2` driver. It owns option parsing, device safety checks, cluster locking, journal replay, slot recovery, pass sequencing, superblock writeback, cleanup, and exit status.

Behavior:
- Supports `-n`, `-y`, `-p`/`-a`, `-f`, `-F`, `-b`, `-B`, `-r`, `-D`, `-G`, `-P`, `-t`, `-u`, `-v`, and `-V`.
- Refuses read-write checking on mounted/busy filesystems; warns and asks before read-only mounted checks or skipped cluster checks.
- Initializes error tables, progress display, signal handlers, and shared `o2fsck_state`.
- Can recover the primary superblock from a numbered backup superblock before opening normally.
- Opens the filesystem, validates minimal superblock state, locks the cluster via o2cb/DLM unless local/read-only/skipped, and prints filesystem identity.
- Checks journal files, decides whether journal replay is needed, replays dirty journals, closes/reopens after replay, then grows the I/O cache.
- Initializes inode/link/dir/cluster tracking state after journal replay.
- Runs slot recovery for local allocators, truncate logs, and orphan dirs, forcing a full check if recovery reports errors.
- Skips full pass work if the filesystem is clean and no force condition applies.
- Runs passes 0 through 5 in order, then writes superblock state, optionally clears dirty journal flags and jbd2 errno, and formats the slot map.
- Exit code is the fsck bitmask defined in `util.h`.

Key shared state:
- `o2fsck_state` tracks filesystem handle, allocator inodes, inode type bitmaps, allocated/duplicate clusters, inode/link reference counts, directory blocks, parent graph, refcount trees, prompt policy, repair flags, statistics, and progress/resource tracking.

Dependencies: all fsck pass modules, journal/slot recovery, libocfs2, libo2cb/libo2dlm cluster services, prompt framework, progress library.

Risk notes:
- `-F` is intentionally dangerous and guarded only by an interactive warning.
- `-n` opens read-only and skips journal replay/slot recovery, so later reported errors can be spurious.
- Memory allocation and most I/O/pass errors are treated as fatal.
- Signal handling attempts to release cluster resources and close the filesystem before exit.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/fsck.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/fsck.ocfs2.8.in -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/fsck.ocfs2.8.in

Read coverage: complete file read, 142 lines.

Purpose: manual page template for `fsck.ocfs2`.

Content:
- Documents synopsis, device argument, options, exit codes, related tools, authors, and copyright.
- Highlights repair modes: `-n` no-write diagnostics, `-y` answer yes, `-p` preen, and `-a` compatibility alias for `-p`.
- Documents cluster-safety option `-F` with explicit corruption warning.
- Documents backup superblock recovery with `-r`, alternate superblock/block size with `-b`/`-B`, forced check with `-f`, directory optimization with `-D`, progress/stats/debug/version options.

Exit-code contract:
- Matches e2fsck-style bitmask: `0`, `1`, `2`, `4`, `8`, `16`, `32`, and `128`.

Risk notes:
- The man page is the user-visible safety contract for dangerous options.
- It points detailed repair prompts to `fsck.ocfs2.checks(8)`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/fsck.ocfs2.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/fsck.ocfs2.checks.8.in -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/fsck.ocfs2.checks.8.in

Read coverage: complete file read, 1193 lines.

Purpose: manual page template documenting every fsck prompt code and the effect of answering yes.

Behavior and build role:
- The Makefile parses each `.SS "CODE"` heading to generate `prompt-codes.h`.
- Prompt call sites use these generated codes through `PR_<CODE>`.
- The document is both user documentation and a build-time registry of repair prompts.

Covered check families:
- Extent blocks/lists/records: block number, generation, depth/count/free fields, invalid extent blocks, out-of-range extents, unsupported unwritten/refcount flags, holes, overlaps, and CRC.
- Chain allocators and group descriptors: expected group positions, generations, parent/chain fields, loops, counts, free bits, discontiguous block groups, and global cluster count.
- Inodes/local allocators/truncate logs: inode allocator repair, generation mismatch, inode block location, root directory type, symlink consistency, directory zero blocks, inode size/clusters, inline data, sparse data, local allocators, and truncate records.
- Refcount trees: invalid flags/locations, refcount block fields, record ranges/collisions, empty/invalid blocks, cluster/file counts, redundant records, and refcount mismatch.
- Duplicate clusters: clone/delete/refcount-convert decisions for files and system files.
- Directory entries and connectivity: dot/dotdot rules, invalid names, inode ranges/free targets, file type mismatch, duplicate directory parents, duplicate filenames, record lengths, directory trailers, missing root/lost+found, disconnected directories/files, and link counts.
- Journals and cluster info: backup superblock recovery, missing orphan dirs, invalid or inconsistent journal files/features/sizes, dirty journal handling, and cluster-stack reconfiguration.
- Xattr/quota/directory index: invalid xattr blocks/entries/layout/hash/free accounting, quota block corruption choices, missing/corrupt directory indexes.

Risk notes:
- Prompt semantics explicitly say answering no leaves the filesystem unchanged, possibly causing later errors.
- Because prompt code generation depends on headings, changing this man page can affect compilation.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/fsck.ocfs2.checks.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/icount.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/icount.c

Read coverage: complete file read, 242 lines.

Purpose: compact inode reference/link count table used by fsck.

Behavior:
- Represents count `1` in a block bitmap and counts greater than `1` in an rb-tree keyed by inode block number.
- `o2fsck_icount_set()` keeps bitmap and tree synchronized.
- `o2fsck_icount_get()` reads either the single-count bitmap or multi-count tree.
- `o2fsck_icount_delta()` adjusts counts and logs internal failure on negative transitions.
- `o2fsck_icount_next_blkno()` finds the next inode with a recorded count across both structures.
- `o2fsck_icount_new()` allocates state; `o2fsck_icount_free()` releases bitmap and tree nodes.

Dependencies: OCFS2 block bitmap APIs and kernel-style rbtrees.

Risk notes:
- Insert helper assumes duplicates are not inserted.
- Count storage is `uint16_t`, matching OCFS2 link-count scale but requiring caller discipline for overflows.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/icount.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/dirblocks.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/dirblocks.h

Read coverage: complete file read, 58 lines.

Purpose: declares directory-block tracking and indexed-directory rebuild helpers.

Key API:
- `o2fsck_dirblocks` rb-tree root plus block count.
- `o2fsck_dirblock_entry` fields for owning inode, block number, and block count.
- `o2fsck_add_dir_block()`, `o2fsck_dir_block_iterate()`, reindex-directory lookup/add helpers, `o2fsck_rebuild_indexed_dirs()`, and `o2fsck_check_dir_index()`.

Dependencies: OCFS2 structures and kernel rbtree API.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/dirblocks.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/dirparents.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/dirparents.h

Read coverage: complete file read, 59 lines.

Purpose: declares directory-parent records used to validate parentage and connectivity.

Key data:
- `dp_ino`: directory inode.
- `dp_dot_dot`: inode referenced by `..`.
- `dp_dirent`: inode containing the directory entry that points to this directory.
- `dp_connected`, `dp_loop_no`, and `dp_in_orphan_dir` are pass 3 connectivity state.

Key API: add, lookup, first, next, and remove helpers.

Dependencies: kernel rbtree API.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/dirparents.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/extent.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/extent.h

Read coverage: complete file read, 71 lines.

Purpose: declares fsck extent-tree validation hooks and state.

Key data:
- `check_leaf_er_func` validates leaf extent records.
- `mark_leaf_er_alloc_func` accounts for leaf extent allocations.
- `struct extent_info` accumulates max byte size, cluster count, last extent block, expected depth, callback pointers, and callback data.

Key API: `o2fsck_check_extents()`, generic `check_el()`, `o2fsck_check_extent_rec()`, and `o2fsck_mark_tree_clusters_allocated()`.

Dependencies: `fsck.h` and OCFS2 extent structures.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/extent.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/fsck.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/fsck.h

Read coverage: complete file read, 136 lines.

Purpose: central state and utility definitions for `fsck.ocfs2`.

Key data:
- `o2fsck_resource_track` stores elapsed/user/system time and I/O stats.
- `o2fsck_state` holds the filesystem handle, cached allocator inodes, inode and cluster bitmaps, inode-count tables, directory block and parent indexes, refcount tracking state, prompt/repair flags, error/status flags, progress state, and filesystem object counters.
- Defines `OCFS2_MAX_PATH_DEPTH` histogram size for extent depths.

Key API: `o2fsck_state_reinit()` and verbose logging macro.

Dependencies: inode-count and directory-block headers plus tools progress API.

Risk notes:
- Most fsck modules mutate shared `o2fsck_state`; correct pass ordering is required.
- Prompt flags and write-error flags are global to a run.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/fsck.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/icount.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/icount.h

Read coverage: complete file read, 46 lines.

Purpose: declares fsck inode-count table abstraction.

Key data:
- `o2fsck_icount` combines a bitmap for count-one inodes with an rb-tree for higher counts.

Key API: set, get, delta, allocate, free, and find-next helpers.

Dependencies: OCFS2 bitmap API and kernel rbtree API.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/icount.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/journal.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/journal.h

Read coverage: complete file read, 36 lines.

Purpose: declares fsck journal checking, replay, and cleanup APIs.

Key API:
- `o2fsck_replay_journals()`
- `o2fsck_should_replay_journals()`
- `o2fsck_clear_journal_flags()`
- `o2fsck_check_journals()`

Dependencies: `fsck.h` and libocfs2 journal structures.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/journal.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/o2fsck_strings.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/o2fsck_strings.h

Read coverage: complete file read, 44 lines.

Purpose: declares rb-tree-backed string set helpers used by fsck for duplicate-name detection.

Key data:
- `o2fsck_strings` stores a root node and byte-allocation accounting.

Key API: existence test, insert with duplicate result, init, free, and allocated-byte reporting.

Dependencies: OCFS2 and kernel rbtree headers.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/o2fsck_strings.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass0.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass0.h

Read coverage: complete file read, 32 lines.

Purpose: declares fsck pass 0.

API: `o2fsck_pass0(o2fsck_state *ost)`.

Role: pass 0 validates and repairs chain allocators and group descriptor structures before inode/data passes depend on allocator accounting.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass0.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass1.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass1.h

Read coverage: complete file read, 33 lines.

Purpose: declares fsck pass 1 and inode allocator cleanup.

API:
- `o2fsck_pass1(o2fsck_state *ost)`
- `o2fsck_free_inode_allocs(o2fsck_state *ost)`

Role: pass 1 walks allocated inodes, validates inode metadata and extent trees, and builds allocation/reference accounting.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass1.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass1b.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass1b.h

Read coverage: complete file read, 24 lines.

Purpose: declares duplicate-cluster repair pass.

API: `ocfs2_pass1_dups(o2fsck_state *ost)`.

Role: handles overclaimed clusters detected during pass 1, including clone/delete/refcount-oriented repairs.

Risk note: include guard closing comment names `PASS1_H`, likely a cosmetic copy/paste mismatch.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass1b.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass2.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass2.h

Read coverage: complete file read, 33 lines.

Purpose: declares fsck pass 2 directory-entry checks.

API:
- `o2fsck_pass2(o2fsck_state *ost)`
- `o2fsck_test_inode_allocated(o2fsck_state *ost, uint64_t blkno)`

Role: validates directory entries and records relationship/link metadata for later passes.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass2.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass3.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass3.h

Read coverage: complete file read, 33 lines.

Purpose: declares fsck pass 3 connectivity checks.

API:
- `o2fsck_pass3(o2fsck_state *ost)`
- `o2fsck_reconnect_file(o2fsck_state *ost, uint64_t inode)`

Role: ensures directories are reachable and reconnects orphaned filesystem objects to `lost+found` when needed.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass3.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass4.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass4.h

Read coverage: complete file read, 33 lines.

Purpose: declares fsck pass 4 and orphan-dir replay helper.

API:
- `replay_orphan_dir(o2fsck_state *ost, int slot_recovery)`
- `o2fsck_pass4(o2fsck_state *ost)`

Role: resolves inode link counts, handles disconnected non-directory inodes, and replays orphan directory cleanup.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass4.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass5.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass5.h

Read coverage: complete file read, 26 lines.

Purpose: declares fsck pass 5.

API: `o2fsck_pass5(o2fsck_state *ost)`.

Role: quota-related final pass that loads, merges, recomputes, or recreates quota state.

Risk note: include guard closing comment names `PASS4_H`, likely cosmetic copy/paste mismatch.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass5.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/problem.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/problem.h

Read coverage: complete file read, 61 lines.

Purpose: defines the fsck prompt framework and prompt-code integration.

Behavior:
- Defines prompt default flags `PY` and `PN`.
- Wraps `prompt_input()` in a `prompt()` macro that creates a unique symbol containing the prompt code and source line.
- Includes generated `prompt-codes.h`, built from `fsck.ocfs2.checks.8.in`.
- Declares `prompt_input()` with printf-format checking.

Risk notes:
- The unique-symbol trick supports the Makefile duplicate-prompt-code check.
- Prompt documentation and code generation must stay synchronized.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/problem.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/refcount.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/refcount.h

Read coverage: complete file read, 33 lines.

Purpose: declares fsck refcount-tree validation and accounting APIs.

Key API:
- `o2fsck_check_refcount_tree()`
- `o2fsck_mark_clusters_refcounted()`
- `o2fsck_check_mark_refcounted_clusters()`

Role: supports reflink/refcounted extent validation and detects whether refcount records match physical cluster sharing.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/refcount.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/slot_recovery.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/slot_recovery.h

Read coverage: complete file read, 30 lines.

Purpose: declares slot recovery helpers run before or after fsck passes.

Key API:
- `o2fsck_replay_truncate_logs()`
- `o2fsck_replay_local_allocs()`
- `o2fsck_replay_orphan_dirs()`

Role: recovers per-slot allocator, truncate-log, and orphan-dir state outside normal pass scanning.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/slot_recovery.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/util.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/util.h

Read coverage: complete file read, 97 lines.

Purpose: declares common fsck utilities, exit codes, cache controls, bitmap wrappers, write helpers, slot-system-file iteration, abort handling, and resource tracking.

Key details:
- Defines e2fsck-compatible exit-code bitmask constants.
- Defines cache modes: none, journal-sized, and full recovery cache.
- Declares inode writeback, cluster allocation marking, publish-block reading, bit counting, slot-system-file handling, and resource statistics.
- Bitmap set/clear macros pass caller function names into fatal-on-error wrappers.

Dependencies: `fsck.h`, libocfs2 bitmap/I/O/stat APIs.

Risk notes:
- Bitmap wrapper comments state bitmap operations are not expected to fail and should abort if they do.
- Exit-code constants are part of the command-line compatibility contract.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/util.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/xattr.h -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/xattr.h

Read coverage: complete file read, 26 lines.

Purpose: declares extended-attribute validation entry point.

API: `o2fsck_check_xattr(o2fsck_state *ost, struct ocfs2_dinode *di)`.

Role: lets inode scanning validate and repair inode/block/bucket xattr structures.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/journal.c -->
# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/journal.c

Read coverage: complete file read, 1138 lines.

Purpose: checks, replays, repairs, and clears OCFS2 per-slot JBD2 journal state for fsck.

Major behavior:
- Maintains `journal_info` per slot: slot number, replay flag, journal inode/cached inode, journal superblock and block, revoke rb-tree, final sequence, and shared duplicate-block bitmap.
- `o2fsck_should_replay_journals()` scans all journal inodes for `OCFS2_JOURNAL_DIRTY_FL`, reads journal superblocks, and decides whether any `s_start` requires replay.
- `o2fsck_replay_journals()` performs a first scan of each dirty journal to validate tags, detect duplicate journal block mappings, build revoke records, and determine final sequence; then performs recovery scans that write journaled blocks to target disk blocks unless revoked.
- Replay resets `s_start` and advances `s_sequence`, but intentionally leaves the dirty flag until orphan-dir handling can be completed.
- Journal walking understands descriptor, commit, and revoke blocks, JBD2 sequence wrap comparisons, tag sizes, `JBD2_FLAG_LAST_TAG`, `JBD2_FLAG_SAME_UUID`, and escaped magic restoration.
- `o2fsck_check_journals()` validates all journal files before normal fsck: reads journal superblocks, records feature sets and sizes, finds a good reference journal or consistent known problem, and prompts to regenerate/extend/reset journals when possible.
- `o2fsck_clear_journal_flags()` clears OCFS2 dirty flags and clears any JBD2 superblock `s_errno`.

Important dependencies:
- JBD2 on-disk headers, tags, commit/revoke semantics.
- OCFS2 system inode lookup, cached inode extent mapping, journal superblock read/write helpers, block bitmap APIs, and raw block I/O.
- Prompt codes for invalid journals, unknown/missing features, too-small journals, and dirty flag cleanup.
- `handle_slots_system_file()` for applying cleanup to all slot journal inodes.

Risk notes:
- The file intentionally ignores journals with consistency problems rather than replaying unsafe data.
- I/O errors during replay can cause partial replay, following kernel JBD2 expectations, and fsck warns the user.
- Revoke handling is present but comments note it was historically untested.
- If every journal has unsupported features, fsck refuses and tells the user to upgrade instead of rewriting unknown-format journals.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/fsck.ocfs2/journal.c -->