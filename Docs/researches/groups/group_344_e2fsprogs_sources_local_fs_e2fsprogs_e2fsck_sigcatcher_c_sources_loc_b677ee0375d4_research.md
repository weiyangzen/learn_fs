# Group Research: group_344_e2fsprogs_sources_local_fs_e2fsprogs_e2fsck_sigcatcher_c_sources_loc_b677ee0375d4

Scope: `Docs/research_subset_a.md` includes `sources/local-fs/e2fsprogs`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/sigcatcher.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/sigcatcher.c

## Purpose
Implements e2fsck fatal signal diagnostics. It installs handlers for crash-like signals and prints signal names, `si_code` decoding, fault addresses, and optional backtraces before exiting with `FSCK_ERROR`.

## Main Elements
- `struct str_table`: maps numeric signal or `si_code` values to symbolic names.
- Signal/code tables: conditionally include platform-defined signal constants and signal-specific codes for `SIGILL`, `SIGFPE`, `SIGSEGV`, `SIGBUS`, and `SIGCHLD`.
- `lookup_table()` / `lookup_table_fallback()`: convert numeric values to names, falling back to decimal formatting.
- `die_signal_handler()`: `SA_SIGINFO` handler that reports signal metadata, optional `backtrace_symbols_fd()`, then exits.
- `sigcatcher_setup()`: registers the fatal handler for `SIGFPE`, `SIGILL`, `SIGBUS`, `SIGSEGV`, and `SIGABRT`.
- `DEBUG` test main: exercises abort, divide-by-zero, kill, null write, and sleep paths.

## Dependencies And Integration
Includes `e2fsck.h` for exit codes and attributes. Uses optional `<execinfo.h>` and `HAVE_BACKTRACE` for diagnostic stack output. Called early from `unix.c` main before parsing and filesystem work.

## Behavioral Notes
The handler uses stdio from a signal handler, which is diagnostic rather than async-signal-safe. It exits directly instead of trying to unwind e2fsck state, making it suitable for unexpected process faults rather than normal cancellation.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/sigcatcher.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/super.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/super.c

## Purpose
Performs e2fsck pass-0 style superblock, group descriptor, orphan, resize-inode, quota, timestamp, feature, and backup-superblock checks before or around the main filesystem passes.

## Main Elements
- `check_super_value()` / `check_super_value64()`: validate scalar superblock fields against min, max, and power-of-two constraints; corrupt values set abort.
- Orphan cleanup:
  - `release_inode_block()` frees or truncates blocks for orphaned inodes and updates quota/accounting.
  - `release_inode_blocks()` iterates direct/indirect inode blocks and extended attribute block references.
  - `e2fsck_read_all_quotas()` / `e2fsck_write_all_quotas()` load and persist quota state around orphan cleanup.
  - `release_orphan_inode()` clears or truncates a single inode from the orphan list.
  - `process_orphan_block()` and `process_orphan_file()` validate orphan-file blocks, checksums, and listed inodes.
  - `release_orphan_inodes()` processes legacy orphan list and ext4 orphan file when safe.
- Orphan file reinitialization:
  - `reinit_orphan_block()` rewrites clean orphan-file block templates and updates checksums.
  - `check_init_orphan_file()` verifies, clears, or reports corrupted orphan-file state.
- `check_resize_inode()`: validates the resize inode, reserved GDT block layout, and incompatible feature combinations.
- `e2fsck_fix_dirhash_hint()`: sets signed/unsigned hash hint for indexed directories.
- `check_super_block()`: core superblock and descriptor validation routine.
- `check_backup_super_block()`: compares selected primary fields against the first valid backup superblock, ignoring known kernel-mutated flags.

## Control Flow
`check_super_block()` allocates invalid bitmap/table flag arrays, validates superblock geometry, checks feature compatibility rules, validates every group descriptor’s metadata block locations and checksums, recomputes free counters, optionally adds UUID/testfs/revision fixes, clears or processes orphan structures, adjusts tolerated time skew, validates quotas, journal hints, dirhash hints, and hidden quota inodes.

## Dependencies And Integration
Uses e2fsck problem handling (`fix_problem`, `problem_context`), libext2fs bitmap/group descriptor APIs, quota support, journal helpers, orphan-file helpers, and UUID support. It is invoked from `unix.c` after filesystem open, feature checks, and MMP/journal setup.

## Risk Notes
This file makes destructive repairs: orphan cleanup frees blocks/inodes, group descriptor fixes clear metadata locations, and resize/orphan-file repairs can rewrite special inodes. Many paths are guarded by read-only checks and `fix_problem()` policy, but correctness depends on trustworthy bitmaps and descriptor checksums.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/unix.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/unix.c

## Purpose
Unix command-line front end and main driver for e2fsck. It parses options, opens the device, enforces mount/MMP/journal safety, runs the checker, handles retries/restarts, writes repairs, and returns fsck-compatible exit codes.

## Main Elements
- Globals/options: `cflag`, `verbose`, bad-block mode flags, `e2fsck_global_ctx`, optional JBD debug.
- `usage()`: prints supported options and exits with `FSCK_USAGE`.
- `show_stats()`: emits compact or verbose filesystem usage, fragmentation, extent depth, and file-type counts.
- `check_mount()`: prevents unsafe writable checks of mounted or busy filesystems unless read-only/interactive policy permits.
- `is_on_batt()` and `check_if_skip()`: decide whether a clean filesystem can skip full checking based on state, mount count, intervals, battery, backup-super mismatch, and free count fixes.
- Progress support:
  - `calc_percent()`, `e2fsck_clear_progbar()`, `e2fsck_simple_progress()`, `e2fsck_update_progress()`.
  - `SIGUSR1` enables progress, `SIGUSR2` disables it, `SIGINT`/`SIGTERM` request cancellation.
- `parse_extended_opts()`: handles `-E` options including `ea_ver`, readahead, journal-only, discard, extent optimization, full inode count maps, logging, bmap-to-extent, fixes-only, unshare, and encoding checks.
- `PRS()`: allocates context, parses CLI/config, validates mutually exclusive modes, resolves devices, sets signals, logging/profiles, read-only behavior, readahead, badblocks PATH, and debug options.
- `try_open_fs()`: opens ext filesystems, trying block sizes for explicit superblocks and setting bitmap defaults.
- `e2fsck_check_mmp()`: validates multiple-mount-protection state and reports or clears invalid MMP conditions.
- `e2fsck_setup_tdb()`: configures undo I/O backing via explicit undo file or configured undo directory.
- `main()`: complete lifecycle from diagnostics and NLS setup through open/retry/recovery/check/final flush/cleanup.

## Control Flow
`main()` installs crash handling, initializes locale and error tables, parses arguments, verifies mount safety, opens the filesystem with proper flags, optionally tries backup superblocks or relaxed open flags, checks device size, handles MMP restart, validates/replays journal, rejects unsupported features, runs `check_super_block()`, optional bad block scan/import, reads bad block inode, initializes quotas, runs `e2fsck_run()`, recreates journal/orphan file if needed, updates quotas, handles checker restart requests, writes bitmaps and superblock changes, prints stats/resources, and exits with fsck status bits.

## Dependencies And Integration
This is the top-level e2fsck executable entry point. It integrates libext2fs I/O managers, undo I/O, blkid/devname resolution, profiles, problem handling, quota code, journal recovery, badblocks support, resource tracking, NLS, MMP, and the pass engine `e2fsck_run()`.

## Risk Notes
The file contains most safety gates for mounted filesystems, read-only mode, exclusive opens, MMP, and journal recovery. Bugs here can cause either dangerous checks on active devices or refusal to repair valid cases. Restart paths are complex because journal replay, MMP enabling, floppy-style exclusive opens, backup superblocks, and checker-requested restarts all loop through `restart`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/unix.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/util.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/util.c

## Purpose
Provides miscellaneous e2fsck utilities: fatal exit handling, logging, allocation wrappers, interactive prompting, bitmap I/O wrappers, resource tracking, inode I/O wrappers, backup-superblock discovery, filesystem/module detection, reliable writes, MMP diagnostics, bitmap type selection, and memory-size detection.

## Main Elements
- `fatal_error()`: flushes/stops MMP, reports modification/error state, sets abort flag, longjmps if safe, otherwise exits with fsck status.
- `log_out()` / `log_err()`: mirror stdout/stderr messages to optional log file.
- `e2fsck_allocate_memory()` and `string_copy()`: common allocation helpers.
- `ask_yn()` / `ask()`: interactive yes/no prompting with raw terminal mode, translated shortcuts, “yes to all”, and cancellation handling.
- `e2fsck_read_bitmaps()` / `e2fsck_write_bitmaps()`: controlled bitmap read/write with e2fsck bitmap type selection and checksum-error handling.
- `preenhalt()`: stops automatic preen mode on unexpected inconsistency.
- `RESOURCE_TRACK` helpers: track memory, CPU time, elapsed time, and I/O deltas.
- Inode wrappers: fatal-on-error read/write helpers for normal and full inode sizes.
- `get_backup_sb()`: scans likely backup superblocks across block sizes and backup group sequence.
- `ext2_file_type()`: maps Linux inode mode to ext2 directory entry file type.
- `fs_proc_check()` / `check_for_modules()`: detect kernel filesystem support via `/proc/filesystems` or modules.
- `write_all()`: retries partial/EINTR/EAGAIN writes.
- `dump_mmp_msg()` / `e2fsck_mmp_update()`: report MMP conflicts and update failures.
- `e2fsck_set_bitmap_type()` plus allocation wrappers: profile-driven bitmap backend selection.
- `get_memory_size()`: returns physical memory size via `sysconf`.

## Dependencies And Integration
Used broadly by e2fsck passes and `unix.c`. Depends on libext2fs memory, bitmap, I/O, inode, MMP, profile, and problem conventions. Reads host `/proc` and `/lib/modules` only for feature/module checks.

## Risk Notes
`fatal_error()` determines final fsck status and whether modifications require reboot/non-destructive flags. Prompt handling changes terminal mode and relies on restoration on normal prompt exit. Bitmap reads intentionally ignore checksum errors during retry, which is useful for repair but shifts validation responsibility to later passes.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/util.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/Makefile.in -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/Makefile.in

## Purpose
Autoconf makefile template for building, testing, installing, and cleaning `libext2fs` and related debug/test utilities.

## Main Elements
- Build variables: source/build roots, `my_dir`, install tools, debugfs-specific flags, generated tool commands `mk_cmds` and `compile_et`.
- Object lists:
  - Optional debugfs/resizer/e2image/test I/O/TDB objects.
  - Core `OBJS` for libext2fs, including allocation, bitmaps, block mapping, directory, extent, inode, journal, metadata checksum, I/O, undo, sparse, and rbtree modules.
  - `SRCS` mirrors the source files and generated/test sources.
- Library metadata: static, ELF shared, BSD library image/version/install settings.
- Compile rules: normal, static/profile/shared/PIC object generation plus static analysis hooks.
- Generated files: `ext2_err.et`, `ext2_err.c/.h`, `ext2fs.pc`, `ext2_types.h`, `crc32c_table.h`, `utf8data.h`.
- Test targets: build and run `tst_badblocks`, `tst_bitops`, `tst_icount`, `tst_bitmaps`, checksum/hash tests, inline-data tests, and `tst_libext2fs`.
- Install/uninstall/clean/distclean targets.
- Manually maintained dependency section for all lib objects and debugfs-linked utilities.

## Dependencies And Integration
Pulls in makefile fragments via `@MAKEFILE_LIBRARY@`, `@MAKEFILE_ELF@`, `@MAKEFILE_BSDLIB@`, and `@MAKEFILE_PROFILE@`. Bridges `lib/ext2fs`, `debugfs`, `e2fsck`, `misc`, `lib/support`, `lib/et`, `lib/ss`, e2p, uuid, blkid, archive, and OS-specific I/O.

## Risk Notes
The dependency block is explicitly manually maintained, including Windows I/O caveats. Any source/header addition must update both object/source lists and dependency rules or parallel/incremental builds can become stale. The debugfs build intentionally reaches into e2fsck journal recovery sources due to shared journal code.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/alloc.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/alloc.c

## Purpose
Implements core libext2fs allocation helpers for new inodes, single blocks, block ranges, allocation callbacks, and allocation goals.

## Main Elements
- `ext2fs_clear_block_uninit()`: clears group block-uninitialized flag, updates checksum and dirty flags.
- `check_inode_uninit()`: initializes uninitialized inode bitmap groups before searching.
- `ext2fs_new_inode()`: finds the next free inode starting near parent directory’s group, wrapping around.
- `ext2fs_new_block3()` / `ext2fs_new_block2()` / `ext2fs_new_block()`: find a free block/cluster from a goal, with callback support and recursion avoidance.
- `ext2fs_alloc_block3()` / wrappers: allocate, zero, write, and account for a block.
- `ext2fs_get_free_blocks2()` / wrapper: find a free contiguous block run with bitmap granularity alignment.
- Callback setters: `ext2fs_set_alloc_block_callback()`, `ext2fs_set_new_range_callback()`.
- `ext2fs_find_inode_goal()`: derives an allocation goal from an inode’s extent, first block, or flex group.
- `ext2fs_new_range()`: finds free ranges with fixed-goal, min-length, and zeroing flags.
- `ext2fs_alloc_range()`: allocates and accounts a minimum-length range.

## Dependencies And Integration
Uses bitmap search/test APIs, group descriptor checksum helpers, extent APIs, zeroing/I/O helpers, and allocation stats from `alloc_stats.c`. Consumers include mke2fs, e2fsck repairs, inode expansion, bad-block inode updates, and other libext2fs mutators.

## Risk Notes
This code returns free locations but does not always mark them; callers must account allocations correctly. Bigalloc cluster granularity and uninitialized bitmap flags are central correctness concerns.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/alloc_sb.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/alloc_sb.c

## Purpose
Reserves superblock and group descriptor blocks for newly initialized filesystems, primarily for mke2fs.

## Main Elements
- `ext2fs_reserve_super_and_bgd()`: computes superblock/old descriptor/new descriptor locations for a group, marks those blocks in a bitmap, handles 1K blocksize bigalloc block zero, and returns an estimated free block count.
- `ext2fs_reserve_super_and_bgd2()`: calls the first routine then counts used blocks in the group to return descriptor/super usage.

## Dependencies And Integration
Uses `ext2fs_super_and_bgd_loc2()`, group descriptor sizing, feature checks for `meta_bg`, bitmap marking, and used-block counting. It is part of filesystem initialization/allocation table setup.

## Risk Notes
The comment warns the original return value assumes inode tables and bitmaps live in the group, which is not necessarily true with `flex_bg`; callers must not overinterpret the free-block estimate.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/alloc_sb.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/alloc_stats.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/alloc_stats.c

## Purpose
Updates allocation bitmaps, group descriptor counters, superblock counters, checksums, dirty flags, and optional callbacks when inodes or blocks are allocated or freed.

## Main Elements
- `ext2fs_inode_alloc_stats2()` / wrapper: marks/unmarks inode bitmap, adjusts free inode and directory counts, clears inode-uninit flag, adjusts unused-inode hint, updates checksum, and marks metadata dirty.
- `ext2fs_block_alloc_stats2()` / wrapper: marks/unmarks block bitmap, adjusts free block counters with cluster ratio, clears block-uninit flag, updates checksum, marks dirty, and invokes callback.
- `ext2fs_set_block_alloc_stats_callback()`: installs single-block stats callback.
- `ext2fs_block_alloc_stats_range()`: marks/unmarks a block range, splits accounting across groups, adjusts free counters and checksums, and invokes range callback.
- `ext2fs_set_block_alloc_stats_range_callback()`: installs range stats callback.

## Dependencies And Integration
Called by allocation/freeing paths across libext2fs and e2fsck, including bad-block inode updates and orphan cleanup. Depends on valid loaded bitmaps and group descriptors.

## Risk Notes
The `inuse` parameter is signed and used directly in counter arithmetic. Incorrect sign or cluster-alignment assumptions can corrupt free counts. Range accounting normalizes `inuse` to +/-1 and divides group counts by cluster ratio.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/alloc_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/alloc_tables.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/alloc_tables.c

## Purpose
Allocates block bitmaps, inode bitmaps, and inode tables for each block group during filesystem creation.

## Main Elements
- `flexbg_offset()`: chooses a free start block for metadata across flex_bg groups, preferring contiguous placement and falling back to smaller searches.
- `ext2fs_allocate_group_table()`: allocates missing block bitmap, inode bitmap, and inode table locations for one group, with special handling for stride and flex_bg layouts.
- `ext2fs_allocate_tables()`: iterates all groups, reports progress, and allocates each group’s tables.

## Dependencies And Integration
Uses allocation search from `alloc.c`, bitmap marking, group descriptor setters, free-block counter updates, group descriptor checksums, and progress callbacks. Used by mke2fs/new filesystem initialization.

## Risk Notes
Flex_bg accounting updates may charge metadata blocks to groups different from the logical group being initialized. The code has FIXME notes about backup group descriptor overlap when flex_bg allocations grow into backup descriptor regions.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/alloc_tables.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/atexit.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/atexit.c

## Purpose
Provides libext2fs-managed normal-exit cleanup callbacks.

## Main Elements
- `struct exit_data`: callback plus opaque data.
- Static `items` and `nr_items`: process-global callback list.
- `handle_exit()`: registered with libc `atexit()`, calls callbacks in reverse registration order, skips null entries, frees storage.
- `ext2fs_add_exit_fn()`: adds a unique callback/data pair, reuses null slots, registers `handle_exit()` on first use, and resizes storage.
- `ext2fs_remove_exit_fn()`: removes matching callback/data by shifting entries and clearing the tail.

## Dependencies And Integration
Uses libext2fs memory resize/free helpers. Intended for normal process termination cleanup; comments state signal exits must call `exit()` themselves if these callbacks are required.

## Risk Notes
The callback list is process-global and not synchronized. `handle_exit()` computes `items + nr_items - 1`; with `nr_items == 0` it is only reached after registration, but direct misuse would be unsafe.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/atexit.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/badblocks.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/badblocks.c

## Purpose
Implements sorted 32-bit list primitives used for bad block lists and similar u32 tracking lists.

## Main Elements
- `make_u32_list()`: allocates and initializes list storage.
- Creation/copy wrappers: `ext2fs_u32_list_create()`, `ext2fs_badblocks_list_create()`, `ext2fs_u32_copy()`, `ext2fs_badblocks_copy()`.
- `ext2fs_u32_list_add()` / badblocks wrapper: inserts unique values in sorted order, growing by 100 entries when full.
- `ext2fs_u32_list_find()` and test wrappers: binary search for values.
- `ext2fs_u32_list_del()` and badblocks delete wrapper: remove a value and compact the list.
- Iterator API: begin, next, end for u32 and badblocks aliases.
- Equality/count helpers: compare list contents and return count.

## Dependencies And Integration
Defines the core in-memory list used by bad block import, bad block inode creation, and compatibility wrappers. Uses libext2fs memory helpers and magic checks.

## Risk Notes
The list stores `__u32`/`blk_t` style values, so it represents legacy 32-bit block lists. Copy creation copies `bb->size` entries, not just `num`, assuming full allocation is initialized.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/badblocks.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bb_compat.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bb_compat.c

## Purpose
Provides legacy `badblocks_*` API names as thin wrappers around the `ext2fs_badblocks_*` API.

## Main Elements
- `badblocks_list_create()`, `badblocks_list_free()`, `badblocks_list_add()`, `badblocks_list_test()`.
- Iterator wrappers: `badblocks_list_iterate_begin()`, `badblocks_list_iterate()`, `badblocks_list_iterate_end()`.

## Dependencies And Integration
Includes `ext2fsP.h` and forwards directly to the modern libext2fs badblocks functions. This preserves older caller/source compatibility.

## Risk Notes
No independent logic; behavior and limitations are inherited from `badblocks.c` and list-free implementation elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bb_compat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bb_inode.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bb_inode.c

## Purpose
Updates the ext bad block inode (`EXT2_BAD_INO`) to match a bad block list.

## Main Elements
- `struct set_badblock_record`: state for iterating old/new bad block inode blocks, saved indirect blocks, buffer, and error propagation.
- `ext2fs_update_bb_inode()`: clears old bad block inode blocks, appends new bad blocks, updates inode timestamps, block count, size, and writes the inode.
- `clear_bad_block_proc()`: block iterator callback that validates old block numbers, saves indirect blocks, frees existing blocks from allocation stats, and clears block pointers.
- `set_bad_block_proc()`: block iterator append callback that consumes bad block list entries for data blocks, reuses or allocates indirect blocks, zeroes indirect blocks, marks allocations, and installs block pointers.

## Dependencies And Integration
Uses badblocks iterators, block iteration, block allocation/free stats, inode read/write, time helpers, zeroed block buffer, and I/O channel writes. It is called when mke2fs/e2fsck need to persist bad block information into the filesystem.

## Risk Notes
The file header warns that errors can leave the bad block inode inconsistent. The algorithm temporarily frees old bad-block inode blocks before fully installing the new list; error handling preserves process return status but not transactional rollback.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bb_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bitmaps.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bitmaps.c

## Purpose
Allocates, frees, copies, clears, resizes, compares, and accesses ext2fs inode/block bitmaps, including 64-bit and subcluster variants.

## Main Elements
- Free/copy/padding wrappers: `ext2fs_free_inode_bitmap()`, `ext2fs_free_block_bitmap()`, `ext2fs_copy_bitmap()`, `ext2fs_set_bitmap_padding()`.
- `ext2fs_allocate_inode_bitmap()`: allocates inode bitmap over inode range, using 64-bit backend when enabled or legacy bitmap when possible.
- `ext2fs_allocate_block_bitmap()`: allocates per-cluster block bitmap for normal block allocation, respecting bigalloc cluster conversion.
- `ext2fs_allocate_subcluster_bitmap()`: allocates true per-block bitmap for metadata tracking on bigalloc filesystems.
- `ext2fs_get_bitmap_granularity()`: reports cluster bits for 64-bit bitmaps.
- Fudge/clear/resize wrappers: adjust bitmap end ranges, clear maps, resize legacy and 64-bit maps.
- Compare wrappers: block and inode bitmap equality checks with specific error codes.
- Range access wrappers: set/get inode and block bitmap ranges for legacy and 64-bit APIs.

## Dependencies And Integration
Wraps generic bitmap and generic 64-bit bitmap implementations (`gen_bitmap`, `gen_bitmap64`, `bmap64`). Called by e2fsck, mke2fs, allocation code, bitmap I/O, and metadata repair logic.

## Risk Notes
`ext2fs_allocate_block_bitmap()` is per-cluster for backward compatibility, while `ext2fs_allocate_subcluster_bitmap()` is per-block. Callers must choose correctly, especially with bigalloc, or metadata block tracking and allocation accounting can diverge.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/bitmaps.c -->