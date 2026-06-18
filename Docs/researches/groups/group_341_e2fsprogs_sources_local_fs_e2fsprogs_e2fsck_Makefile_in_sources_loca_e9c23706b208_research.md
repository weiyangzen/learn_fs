# Group Research: group_341_e2fsprogs_sources_local_fs_e2fsprogs_e2fsck_Makefile_in_sources_loca_e9c23706b208

Scope checked against `Docs/research_subset_a.md`: all files are within `sources/local-fs/e2fsprogs`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/Makefile.in -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/Makefile.in

## Purpose
Autoconf makefile template for building, testing, installing, and cleaning the `e2fsck` checker and related helper programs/manpages.

## Build Contents
- Builds primary `e2fsck` from pass modules, journal/recovery/revoke, directory metadata helpers, problem/message handling, quota, extent rebuild, readahead, logging, and encrypted file support.
- Supports normal, static, and profiled binaries.
- Builds test/helper targets including `tst_refcount`, `tst_region`, `tst_problem`, `tst_logfile`, `extend`, `flushb`, `iscan`, and `iscan.static`.
- Generates `e2fsck.8` and `e2fsck.conf.5` from `.in` templates through substitution.

## Install Behavior
- Installs `e2fsck` into `$(root_sbindir)`.
- Links `fsck.ext2`, `fsck.ext3`, and `fsck.ext4` to `e2fsck`.
- Installs manpages and links filesystem-specific fsck manpages to `e2fsck.8`.

## Integration
This makefile is the authoritative local build map for which e2fsck modules are linked into the main checker. Files such as `emptydir.c`, `extend.c`, `flushb.c`, and `iscan.c` are not part of the main `OBJS` list except where explicitly built as helper targets.

## Risks / Notes
- Dependency lines are generated and occupy much of the file; updates to included headers or sources require dependency regeneration.
- Optional `MTRACE` and profiling blocks are present but commented/configuration-driven.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/badblocks.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/badblocks.c

## Purpose
Maintains the ext filesystem bad-block inode from either a supplied bad-block list file or the external `badblocks` scanner.

## Main Flow
`read_bad_blocks_file()`:
- Ensures bitmaps are loaded.
- Scans the bad-block inode and clears illegal existing block references.
- If appending, reads the current bad-block inode into a `badblocks_list`.
- If a file is supplied, opens it; otherwise runs `badblocks -b <blocksize> -X ... <device> <last_block>` via `popen`.
- Reads bad blocks with `ext2fs_read_bb_FILE()`.
- Updates the bad-block inode through `ext2fs_update_bb_inode()`.

## Validation
`check_bb_inode_blocks()` rejects block numbers below `s_first_data_block` or beyond filesystem block count, clears the invalid pointer, and returns `BLOCK_CHANGED`.

## Integration
Used by e2fsck command-line bad block options (`-c`, `-l`, `-L`) through the declaration in `e2fsck.h`.

## Risks / Notes
- The `badblocks` command string is assembled with `sprintf` into a 1024-byte buffer; device names are normally controlled by CLI input.
- On fatal errors it sets `E2F_FLAG_ABORT`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/badblocks.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/dirinfo.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/dirinfo.c

## Purpose
Maintains e2fsck’s directory information database: inode number, `..` parent, and tree-walk parent. This avoids repeated directory I/O across passes.

## Data Model
- `struct dir_info_db` stores count/size, in-memory sorted array, last lookup cache, and optional TDB scratch-file state.
- `struct dir_info` entries are sorted by inode number.
- `struct dir_info_iter` abstracts array and TDB iteration.

## Main Behavior
- `setup_db()` initializes the database, using `ext2fs_get_num_dirs()` to size the array.
- With `CONFIG_TDB`, `setup_tdb()` can switch directory info storage to a temporary TDB file based on profile settings under `scratch_files`.
- `e2fsck_add_dir_info()` inserts entries in inode order, handling rare out-of-order inserts by shifting entries.
- `e2fsck_get_dir_info()` does cached lookup, TDB lookup, or binary search.
- Setter/getter functions update or read `parent` and `dotdot`.
- Iteration supports both array traversal and TDB key traversal.
- `e2fsck_free_dir_info()` closes/deletes TDB scratch files and releases arrays.

## Integration
Created during pass 1 and filled/used by later directory passes for connectivity, `..` validation, and parent lookups. Its public API is declared in `e2fsck.h`.

## Risks / Notes
- TDB mode uses a temporary file derived from filesystem UUID and configured scratch directory.
- Array mode depends on sorted insertion for binary search correctness.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/dirinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/dx_dirinfo.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/dx_dirinfo.c

## Purpose
Maintains metadata for indexed/HTREE directories that require validation, repair, or rehashing.

## Data Model
Uses `ctx->dx_dir_info`, a sorted array of `struct dx_dir_info`. Each entry records:
- directory inode,
- hash version,
- casefold hash marker,
- number of directory blocks,
- per-block `dx_dirblock_info` array.

## Main Behavior
- `e2fsck_add_dx_dir()` allocates/grows the array and inserts sorted by inode.
- Tracks whether directory hashing is casefold-aware via `EXT4_CASEFOLD_FL`.
- `e2fsck_get_dx_dir_info()` uses binary search.
- `e2fsck_free_dx_dir_info()` frees each per-directory block array and the main table.
- Count and iterator helpers expose the table to pass/rehash code.

## Integration
Used by pass 1/2 and directory rehash logic for indexed directories. Public declarations are in `e2fsck.h`.

## Risks / Notes
Sorted insertion is required for lookup correctness, similar to `dirinfo.c`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/dx_dirinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/e2fsck.8.in -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/e2fsck.8.in

## Purpose
Manual page template for the `e2fsck(8)` command.

## Covered Behavior
Documents:
- ext2/ext3/ext4 checking and journal replay behavior.
- Safety warning for mounted filesystems.
- Interactive repair modes and answers.
- Main options: alternate superblock/blocksize, bad block scanning/list replacement, progress FD, directory optimization, force, flush, external journal, bad block preservation, read-only/no/preen/yes modes, timing, verbose, version, undo files.
- Extended options including `ea_ver`, `journal_only`, `fragcheck`, `discard`, extent optimization toggles, inode count fullmap, readahead, `bmap2extent`, `fixes_only`, `check_encoding`, and `unshare_blocks`.
- Exit code bit meanings.
- SIGUSR1/SIGUSR2 progress control.
- Bug-reporting guidance and `E2FSCK_CONFIG`.

## Integration
Generated to `e2fsck.8` by the makefile using substitution macros for version/date and conditional external journal content.

## Risks / Notes
This file is documentation, but it is also the user-facing contract for many options implemented across `unix.c`, `badblocks.c`, `journal.c`, `extents.c`, pass code, and logging/config code.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/e2fsck.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/e2fsck.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/e2fsck.c

## Purpose
Core lifecycle and pass dispatcher for an e2fsck run.

## Main Behavior
- `e2fsck_allocate_context()` allocates and initializes `struct e2fsck_struct`, setting defaults such as inode processing size, extended attribute version, page block count, HTREE slack, and current time. `E2FSCK_TIME` can override time for tests.
- `e2fsck_reset_context()` frees per-run bitmaps, dirinfo/dx-dirinfo, EA refcounts, encrypted-file info, invalid metadata flags, casefold maps, counters, journal I/O, and pass statistics.
- `e2fsck_free_context()` calls reset, releases blkid/profile/logging resources, closes problem XML logs, and frees the context.
- `e2fsck_run()` executes pass sequence: pass1, pass1e, pass2, pass3, pass4, pass5. It updates MMP before each pass and honors abort/restart/cancel flags.

## Integration
This is the control skeleton for all e2fsck passes. Most modules in this group allocate data into `e2fsck_t` fields and rely on reset/free to dispose of them.

## Risks / Notes
The context reset path is broad and central; leaked or stale per-pass state usually needs to be wired into this file.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/e2fsck.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/e2fsck.conf.5.in -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/e2fsck.conf.5.in

## Purpose
Manual page template for `e2fsck.conf(5)`, the configuration file controlling default e2fsck behavior.

## Configuration Areas
Documents INI-style stanzas:
- `[options]`: cancellation, time-fudge/system-clock behavior, test flag clearing, battery deferral, indexed-directory slack, inode count fullmap, logging, problem squelching, extent optimization, readahead, reporting.
- `[defaults]`: undo directory behavior.
- `[problems]`: per-problem overrides for messages, preen behavior, maximum counts, default answers, forced no-fix behavior, and not-a-fix optimization markers.
- `[scratch_files]` when enabled: directory, thresholds, dirinfo/icount scratch-file usage.

## Logging Contract
Defines percent expansions used by `logfile.c`: date/time, hostname, device basename, PID, epoch seconds, username, UTC modifier, and year/month/day fields.

## Integration
Generated to `e2fsck.conf.5` by the makefile. Its settings map directly into profile reads in `dirinfo.c`, `logfile.c`, and other e2fsck option/config code.

## Risks / Notes
The `[problems]` section can change repair behavior and is explicitly documented as source-code-sensitive.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/e2fsck.conf.5.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/e2fsck.h -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/e2fsck.h

## Purpose
Central public/internal header for e2fsck modules. It defines the global context, pass flags/options, major shared data structures, and cross-module prototypes.

## Key Structures
- `struct dir_info` and `struct dx_dir_info` for directory parent and indexed-directory metadata.
- `struct resource_track` for timing, memory, and I/O accounting.
- `struct extent_list` and fast-commit replay state used by extent rebuild and journal replay.
- `struct e2fsck_struct`, the main context object containing filesystem handle, names, logs, flags/options, maps, refcounts, dirinfo, encrypted file state, journal I/O, quota context, statistics, progress state, readahead, undo file, and fast-commit replay state.

## Options / Flags
Defines:
- fsck exit codes.
- e2fsck CLI/config options such as readonly, preen, yes/no, badblock checking, journal-only, discard, extent conversion/optimization, fullmap inode counts, unshare blocks, check encoding.
- internal flags for abort/cancel/restart, progress, journal inode creation, superblock specified, time insane, problems fixed, allocation permitted.

## API Surface
Declares pass entrypoints, context lifecycle, badblocks, dirinfo/dx-dirinfo, EA refcount, error handler, encrypted file policy helpers, extent rebuild APIs, journal APIs, logging, quota hooks, pass helpers, readahead, region allocation, rehashing, signal handling, superblock checks, and utility functions.

## Integration
Every substantial e2fsck C file in this group includes this header. It is the primary coupling point between passes and helper modules.

## Risks / Notes
Adding persistent per-run state requires updating both this header and context cleanup in `e2fsck.c`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/e2fsck.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/ea_refcount.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/ea_refcount.c

## Purpose
Implements a compact sorted-array refcount map used for extended attribute blocks, EA inode references, and quota accounting maps.

## Data Model
`struct ea_refcount` contains:
- count,
- allocated size,
- cursor for locality/iteration,
- sorted list of `(ea_key, ea_value)` elements.

Keys are `__u64` and can represent block numbers or inode numbers depending on caller.

## Main Behavior
- `ea_refcount_create()` allocates an initial list, defaulting to 500 entries.
- `get_refcount_el()` looks up by cursor fast path, then binary search, optionally inserting while preserving sorted order.
- `refcount_collapse()` removes zero-valued entries to reclaim slots.
- Public operations fetch, increment, decrement, store, return capacity, and iterate nonzero entries.
- Decrement rejects missing or already-zero values.

## Test Harness
Under `TEST_PROGRAM`, includes validation and a bytecode-like scripted test sequence for create/store/fetch/increment/decrement/collapse/list.

## Integration
Referenced from `e2fsck.h` and stored in `ctx->refcount`, `refcount_extra`, `ea_block_quota_*`, and `ea_inode_refs`.

## Risks / Notes
Insertions use `memmove`; performance is best for mostly sequential keys and modest map sizes. Zero stores remove logical entries only after later collapse.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/ea_refcount.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/ehandler.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/ehandler.c

## Purpose
Installs I/O read/write error handlers for an e2fsck session.

## Main Behavior
- Multi-block read/write errors are decomposed into single-block operations to isolate the failing block.
- Single-block read errors are reported with optional current operation text.
- Read errors can be ignored, and if ignored the user can force a rewrite of the block unless it is beyond filesystem end.
- Write errors can be ignored interactively.
- `preenhalt()` is called before prompting, preventing automatic preen from silently continuing through serious I/O errors.
- `ehandler_operation()` sets/restores the global operation description.
- `ehandler_init()` assigns handlers to an `io_channel`.

## Integration
Works through libext2fs `io_channel` callbacks. Uses `ctx` via `fs->priv_data`.

## Risks / Notes
The current operation string is static global state, not per-context.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/ehandler.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/emptydir.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/emptydir.c

## Purpose
Appears intended to detect and remove empty directory blocks by compacting directory block mappings.

## Main Behavior
- Defines `empty_dir_info_struct` with a dblist, block bitmap of empty directory blocks, inode bitmap of affected directories, a block buffer, current inode/inode data, logical block counter, and freed block count.
- `init_empty_dir()` allocates the state, dblist, empty-block bitmap, and directory inode map.
- `add_empty_dirblock()` records empty directory blocks except inode 11, usually `lost+found`.
- `empty_pass1()` uses `ext2fs_bmap2()` to skip empty blocks and rewrite block references.
- `fix_directory()` reads an inode, iterates blocks with `empty_pass1()`, and adjusts size/block counts if blocks were freed.
- `process_empty_dirblock()` is meant to allocate block buffer, iterate the dblist, and free state.

## Integration
This file is not included in the main `OBJS` list in `Makefile.in`.

## Risks / Notes
The file appears stale/incomplete as read:
- `init_empty_dir()` checks `retval` immediately after `e2fsck_allocate_memzero()` even though `retval` has not been assigned by that call.
- `process_empty_dirblock()` uses undeclared `retval`.
- `process_empty_dirblock()` calls `ext2f_get_mem`, which appears to be a typo for an ext2fs/e2fsck allocator.
These issues explain why it is likely not built into the normal checker.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/emptydir.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/encrypted_files.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/encrypted_files.c

## Purpose
Tracks encryption policies for encrypted inodes across e2fsck passes so pass 2 can verify children of encrypted directories use the correct policy.

## Data Model
- On-disk fscrypt contexts v1/v2 include policy fields plus nonce.
- In-memory policy strips nonce so files sharing a policy compare equal.
- `encrypted_file_info` contains:
  - run-length encoded inode ranges mapped to policy IDs,
  - red-black tree mapping unique policies to policy IDs,
  - next policy ID counter.
- Special policy IDs represent no xattr, corrupt policy, and unrecognized future policy.

## Main Flow
- `read_encryption_xattr()` reads xattr `"c"` from an inode.
- `fscrypt_context_to_policy()` validates v1/v2 context sizes and extracts policy fields.
- `get_encryption_policy_id()` assigns or reuses policy IDs using an rb-tree.
- `append_ino_and_policy_id()` appends ranges and merges adjacent inode numbers with identical policy IDs.
- `add_encrypted_file()` handles encrypted inodes during pass 1, including missing/corrupt xattr repair decisions.
- `find_encryption_policy()` binary-searches ranges during pass 2.
- Destroy functions release policy tree and ranges.

## Integration
Called from pass 1 for `EXT4_ENCRYPT_FL` inodes and from pass 2 directory checks. State hangs off `ctx->encrypted_files` and is cleaned by `e2fsck_reset_context()`.

## Risks / Notes
The range compression assumes encrypted inodes are processed in strictly increasing inode order and calls `fatal_error()` otherwise.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/encrypted_files.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/extend.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/extend.c

## Purpose
Small standalone helper that extends a file to at least a requested number of blocks by reading and rewriting the final target block.

## Main Behavior
- CLI: `extend filename nblocks blocksize`.
- Allocates a zeroed block buffer.
- Opens file read/write.
- Seeks to `(nblocks - 1) * blocksize`, reads a block, seeks back, and writes a block.

## Integration
Built as optional helper target `extend` in `Makefile.in`, not part of the main `e2fsck` binary.

## Risks / Notes
Uses `int` for seek offset result and block arithmetic, so it is not suitable for very large offsets on all platforms. Error message after failed write says `"read"`, likely a copy/paste typo.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/extend.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/extents.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/extents.c

## Purpose
Evaluates and rebuilds extent trees, including conversion from block maps to extents and optimization of overly wide/deep extent trees.

## Main Flows
- `e2fsck_rebuild_extents_later()` schedules an inode in `ctx->inodes_to_rebuild`, or rebuilds immediately if allocation is allowed.
- `load_extents()` walks an existing extent tree, frees internal extent tree blocks for later rebuild, coalesces adjacent leaf extents, and records leaf mappings.
- `find_blocks()` collects block-mapped file mappings into synthetic extents.
- `rewrite_extent_replay()` clears the inode’s extent tree, inserts extents, splits oversized initialized/uninitialized extents to legal lengths, updates quota and block counters, fixes parents, and writes the inode.
- `e2fsck_rewrite_extent_tree()` is a public rewrite helper, also used by fast-commit replay.
- `rebuild_extents()` implements pass 1E over the scheduled inode bitmap.
- `e2fsck_check_rebuild_extents()` scans an inode’s extent tree for conversion/optimization opportunities.
- `e2fsck_should_rebuild_extents()` decides whether to rebuild based on forced corruption, depth, width, and optimization settings.
- `e2fsck_pass1e()` runs pass 1E.

## Integration
Pass 1 schedules conversion/optimization through this module. Journal fast-commit replay uses `e2fsck_read_extents()` and `e2fsck_rewrite_extent_tree()` to apply extent updates.

## Risks / Notes
This module mutates allocation accounting and quota accounting while rebuilding extent metadata. Correct bitmap state and allocation permission are prerequisites.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/extents.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/flushb.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/flushb.c

## Purpose
Standalone benchmarking helper to flush a block device’s buffer cache.

## Main Behavior
- CLI: `flushb disk`.
- Opens the device read-only.
- On Linux or systems defining `BLKFLSBUF`, invokes `ioctl(fd, BLKFLSBUF, 0)`.
- Reports unsupported ioctl otherwise.

## Integration
Built as optional helper target `flushb` in `Makefile.in`. The file comment warns it is not generally useful outside benchmarking scripts.

## Risks / Notes
The file explicitly warns older Linux 2.2 kernels could corrupt filesystems under heavy load when using this operation.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/flushb.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/iscan.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/iscan.c

## Purpose
Standalone performance test for scanning an ext inode table.

## Main Behavior
- CLI: `iscan [-F] [-I inode_buffer_blocks] device`.
- Optional `-F` flushes the device via `ext2fs_sync_device()`.
- Opens filesystem with `ext2fs_open()`.
- Starts an inode scan with configurable inode buffer blocks.
- Iterates all inodes with `ext2fs_get_next_inode()`.
- Prints memory/time/I/O resource stats and total inode count.

## Resource Tracking
Contains local `resource_track` implementation similar to e2fsck timing support:
- records wall/user/system time,
- tracks heap growth or malloc info,
- tracks I/O stats from the channel manager.

## Integration
Built as optional `iscan` and `iscan.static` helper targets. It links against the same ext2fs/support libraries.

## Risks / Notes
The getopt string is `"FI"` but `-I` consumes `optarg`; normally this should be `"FI:"`. As read, argument parsing for `-I` appears suspect.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/iscan.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/jfs_user.h -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/jfs_user.h

## Purpose
Compatibility layer allowing e2fsck/debugfs user-space code to include and reuse kernel JBD/JBD2 journal recovery code.

## Key Definitions
- User-space `buffer_head`, `inode`, and `kdev_s` substitutes.
- `K_DEV_FS` and `K_DEV_JOURNAL` device selectors.
- No-op kernel primitives such as buffer locking and readahead.
- Simple `kmem_cache`, `kmalloc`, `kfree`, hash helpers, checksum helper, and descriptor checksum setter.
- Includes `<ext2fs/kernel-jbd.h>` for journal definitions.

## Declared Kernel-Compatibility APIs
Declares functions implemented in `journal.c`:
- `jbd2_journal_bmap`
- `getblk`
- `sync_blockdev`
- `ll_rw_block`
- `mark_buffer_dirty`
- `mark_buffer_uptodate`
- `brelse`
- `buffer_uptodate`
- `wait_on_buffer`

Also declares recovery/revoke APIs supplied by local recovery/revoke sources.

## Integration
Included by `journal.c`, `recovery.c`, and `revoke.c`. With `DEBUGFS`, adapts types to `ext2_filsys`; otherwise uses `e2fsck_t`.

## Risks / Notes
This file intentionally mirrors kernel expectations in user space, so ABI/semantic drift between imported journal code and these shims is a key maintenance risk.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/jfs_user.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/journal.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/journal.c

## Purpose
Handles ext3/ext4 journal discovery, validation, recovery, reset, release, external journal hints, hidden journal inode migration, and ext4 fast-commit replay.

## Kernel Compatibility Layer
Implements `jfs_user.h` shims:
- `jbd2_journal_bmap()` maps journal logical blocks via inode bmap for internal journals.
- `getblk()` allocates user-space buffer heads over filesystem or journal I/O.
- `ll_rw_block()` reads/writes blocks through libext2fs I/O.
- `brelse()` writes dirty buffers before freeing.
- buffer state helpers mirror kernel interfaces.

## Journal Checksums
Provides journal superblock checksum verification and setting for checksum v2/v3 journals, using CRC32C and validating checksum type.

## Fast-Commit Replay
The file implements ext4 fast-commit scan and replay:
- Scan validates tag ordering, expected transaction ID, supported features, extent encodings, and tail CRC.
- Replay handles create/link/unlink dentry tags, inode tags, add-range/delete-range extent tags, padding/head/tail.
- Extent replay keeps a cached `extent_list` per inode, modifies ranges in memory, marks block bitmap allocation state, and flushes via `e2fsck_rewrite_extent_tree()`.
- Replay marks the filesystem temporarily erroneous and `EXT4_FC_REPLAY` because replay updates are not atomic; at completion it recalculates summary stats, writes bitmaps, restores superblock state, updates checksums, and flushes.

## Journal Loading
`e2fsck_get_journal()`:
- Allocates journal and kdev state.
- Handles internal journal inode lookup and fallback to superblock backup journal blocks.
- Handles external journal discovery by UUID/devno and validates external journal superblock, UUID, and metadata checksum.
- Opens journal I/O, reads the journal superblock block, and installs fast-commit callback if enabled.

`e2fsck_journal_load()`:
- Reads journal superblock.
- Verifies magic/type/version/features/checksum.
- Handles v1/v2 compatibility cleanup.
- Sets journal tail, transaction sequence, first/last blocks, and fast-commit region bounds.

## Recovery / Repair
- `e2fsck_check_ext3_journal()` ensures superblock journal fields are consistent, handles missing/bad journal inode, corrupt journal superblock, unsupported features, stale recovery state, nonzero journal start, and journal errno propagation.
- `recover_ext3_journal()` initializes revoke caches/table, loads the journal, runs `jbd2_journal_recover()`, records failed transactions, then releases/reset journal state.
- `e2fsck_run_ext3_journal()` refuses read-only recovery, flushes pending fs modifications, runs recovery, reopens the filesystem because recovery changed disk state, preserves write/error accounting, clears recovery flag, and rechecks journal consistency.

## Journal Inode / External Hint Maintenance
- `e2fsck_move_ext3_journal()` can move visible root-directory journal files such as `.journal` to reserved inode `EXT2_JOURNAL_INO`, after safety checks and user confirmation.
- `e2fsck_fix_ext3_journal_hint()` updates `s_journal_dev` if blkid finds the external journal UUID at a different device number.

## Integration
Central to ext3/ext4 recovery before full checking. Uses `problem.c` prompts, libext2fs I/O/bitmap/inode APIs, imported JBD2 recovery/revoke code, and extent helpers from `extents.c`.

## Risks / Notes
- Fast-commit replay intentionally bypasses normal full-check atomicity and temporarily marks filesystem error state during replay.
- External journal correctness depends on blkid lookup and UUID/device validation.
- The dentry replay path for symlinks deserves attention: the symlink branch returns `EXT2_FT_SYMLINK` directly rather than assigning `filetype`, which reads like a possible logic issue.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/logfile.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/logfile.c

## Purpose
Sets up e2fsck output and problem log files, including filename expansion and delayed writing when log directories are not yet writable.

## Filename Expansion
`expand_logfn()` expands `%` expressions including:
- date/time fields,
- hostname,
- device basename,
- PID,
- epoch seconds,
- username,
- UTC switch `%U`,
- literal `%`.

## Log Opening
`set_up_log_file()`:
- Reads profile options for log filename, log directory, fallback directory, and wait behavior.
- Expands dynamic filename.
- Tries direct path, configured log directory, fallback directory.
- If enabled and directories are unavailable, uses `save_output()`.

## Delayed Output
`save_output()`:
- Creates a pipe and forks.
- Child daemonizes, buffers all parent output in memory, then repeatedly tries target paths until one opens, writes buffered output, and exits.
- Parent receives a `FILE *` to the pipe.

## Integration
`set_up_logging()` populates `ctx->logf` and `ctx->problem_logf`. The behavior is documented in `e2fsck.conf.5.in`.

## Risks / Notes
Delayed logging can buffer unbounded output in memory until a log path becomes writable.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/logfile.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/message.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/message.c

## Purpose
Formats e2fsck diagnostic/problem messages with abbreviation compression, pathname expansion, inode/dirent fields, safe string printing, and localization hooks.

## Expansion Types
Supports:
- `%` expressions for block numbers, inode numbers, groups, errors, paths, times, quotas, checksums, strings, backup superblock, and numeric formatting.
- `%I*` inode field expressions for size, blocks, links, mode, mtime, file ACL, UID/GID, type, etc.
- `%D*` directory entry expressions for inode, name, rec_len, name_len, and file type.
- `@` abbreviation expressions such as inode, block, filesystem, journal, directory, quota, extent, lost+found, and composite phrases.

## Main Behavior
- `safe_print()` escapes non-printable and high-bit characters.
- `print_pathname()` maps special inode numbers to friendly names or calls `ext2fs_get_pathname()`.
- `print_time()` formats local/GMT time.
- `expand_at_expression()` recursively expands abbreviations with recursion limit.
- `print_e2fsck_message()` walks a template, clears progress UI, and emits fully expanded text.

## Integration
Used by problem reporting (`problem.c`) and general diagnostics. It consumes `struct problem_context` fields.

## Risks / Notes
The template language is compact but highly coupled to `problem_context`; missing context values fall back to literal `%` expressions.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/message.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/mtrace.awk -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/mtrace.awk

## Purpose
AWK post-processor for allocation traces emitted by `mtrace.c`.

## Main Behavior
- `+ addr size`: records allocation, reports duplicate allocation at same address.
- `- addr`: clears allocation, reports freeing an address that was never allocated.
- `< addr`: old pointer side of realloc, clears prior allocation or reports missing prior allocation.
- `> addr size`: new pointer side of realloc, records allocation or reports duplicate.
- Ignores start markers `=` and failed realloc markers `!`.
- At `END`, prints allocations still outstanding.

## Integration
Used only with optional `MTRACE` debugging support.

## Risks / Notes
The script sets array entries to empty strings instead of deleting them, then filters nonempty entries at end.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/mtrace.awk -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/mtrace.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/mtrace.c

## Purpose
Legacy malloc tracing hooks adapted from GNU malloc debugging support.

## Main Behavior
- Reads `MALLOC_TRACE` environment variable.
- Opens trace stream or `/dev/null` if only `mallwatch` is set.
- Installs `__malloc_hook`, `__free_hook`, and `__realloc_hook`.
- Emits trace records:
  - `+ ptr size` on malloc,
  - `- ptr` on free,
  - `< old` and `> new size` on successful realloc,
  - `! old size` on failed realloc.
- `mallwatch` can trigger `tr_break()` when a watched pointer is allocated/reallocated/freed.
- `malloc_get_mallstream()` exposes the trace stream.

## Integration
Optional debugging module controlled by `MTRACE` settings in `Makefile.in`; paired with `mtrace.awk`.

## Risks / Notes
Uses old GNU malloc hook APIs, which are obsolete/removed in newer libc environments. This is debugging-only code and not part of normal builds unless enabled.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/mtrace.c -->