# Group Research: group_458_gfs2_utils_sources_local_fs_gfs2_utils_gfs2_fsck_pass2_c_sources_loc_7bab75631df6

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/pass2.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/pass2.c

This file implements `fsck.gfs2` pass 2, the pathname and directory-content validation pass. It walks system directories and all discovered directory inodes, validates directory entries, repairs malformed entries when permitted, builds parent/dotdot relationship state, and increments the in-memory link-count accounting consumed by later passes.

Key control flow centers on `pass2()`, which checks `jindex`, `per_node`, `master`, and `root` via `check_system_dir()`, then iterates `cx->dirtree` and calls `pass2_check_dir()` for non-system directories. Directory walking is delegated through `struct metawalk_fxns pass2_fxns`, especially `check_dentry()` and `check_hash_tbl()`.

Important behaviors:
- Validates dentry target block range, record/name length, hash value, bitmap type, file type, and formal inode number.
- Handles `.` and `..` specially, recording `dotdot_parent` and `treewalk_parent` in `struct dir_info`.
- Detects and optionally clears duplicate `.`/`..`, stale file-type entries, hard links to directories, entries pointing to invalid/non-inode blocks, and bad formal inode references.
- Repairs exhash directory hash table/leaf corruption using `check_hash_tbl()`, `fix_hashtable()`, `wrong_leaf()`, `lost_leaf()`, `pad_with_leafblks()`, and `write_new_leaf()`.
- Validates per-node system files `inum_rangeN`, `statfs_changeN`, and `quota_changeN`, rebuilding missing or malformed files through libgfs2 builders.
- Relocates entries from misplaced leaves into `lost+found` when recovery cannot safely preserve their original leaf placement.

Dependencies include `libgfs2`, `metawalk`, `link`, `lost_n_found`, inode/directory trees, fsck bitmap helpers, and recovery/build functions. The file is mutation-heavy: repairs mark buffers modified, update bitmaps, allocate leaves, delete dentries, and adjust link counts.

Risks and notes:
- Recovery paths rely on interactive `query()` decisions, so behavior differs under yes/no modes.
- Hash-table repair is complex and can reprocess indices after mutations; incorrect leaf-depth or pointer-count assumptions would affect directory lookup semantics.
- `lost_leaf()` uses fixed buffers and has a suspicious filename-length check against `sizeof(filename)` where `filename` is a pointer, which could prematurely stop processing long names.
- This pass establishes state needed by pass3/pass4, so missed link increments or parent recording errors cascade into connectivity and nlink repair.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/pass2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/pass3.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/pass3.c

This file implements `fsck.gfs2` pass 3, the directory connectivity pass. It verifies that every directory discovered earlier is connected to the root/master tree, reconciles disagreements between a directory’s `..` entry and the parent observed during tree walking, and offers to reconnect or clear orphaned directories.

The main entry point is `pass3(struct fsck_cx *cx)`. It marks the root and master directory as connected, then iterates `cx->dirtree`. For each unchecked directory, it repeatedly calls `mark_and_return_parent()` to climb toward an already checked parent. If no valid parent chain can be found, it handles the directory as unlinked.

`mark_and_return_parent()` compares `di->dotdot_parent` and `di->treewalk_parent`. If they match and point at a dinode, the directory is considered connected through that parent. If they disagree, it checks bitmap state and `dirtree` membership for both candidates. It can repair `..` by calling `attach_dotdot_to()`, remove bad treewalk dentries via `remove_dentry_from_dir()`, or signal that the directory should be treated as orphaned.

Orphan handling loads the inode, checks bitmap type, clears invalid or zero-size orphaned directories when permitted, or calls `add_inode_to_lf()` to relink valid unlinked directories into `lost+found`.

Dependencies include `libgfs2`, `lost_n_found`, `link`, `metawalk`, `util`, and the pass2-populated `dir_info` tree. This pass depends strongly on pass2’s `treewalk_parent` and `dotdot_parent` bookkeeping.

Risks and notes:
- Several comments identify missing interactive policy refinement around choosing parents.
- Parent choice defaults to treewalk when both parents look like directories.
- Some recovery paths remove the dentry from a bad parent and leave the directory unlinked for later lost+found handling.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/pass3.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/pass4.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/pass4.c

This file implements `fsck.gfs2` pass 4, which reconciles inode reference counts after directory traversal. It compares counted links accumulated during earlier passes against on-disk `i_nlink`, repairs mismatches, and handles unlinked inodes by clearing them or moving them into `lost+found`.

The entry point `pass4()` runs three scans:
- `scan_inode_list()` for normal inodes in `cx->inodetree`.
- `scan_dir_list()` for directories in `cx->dirtree`.
- `scan_nlink1_list()` for single-link inodes tracked only in `nlink1map`/`clink1map`.

`handle_unlinked()` covers unreferenced dinodes. If the bitmap says the block is free/bad, it can delete metadata and extended attributes using `pass4_fxns_delete`. If the block is not a dinode, it can clear it. Valid unlinked zero-size inodes can be freed; otherwise the inode can be added to `lost+found`, with link counts adjusted. `handle_inconsist()` fixes mismatched link counts by loading the inode and calling `fix_link_count()`.

Dependencies include `libgfs2`, `link`, `lost_n_found`, `inode_hash`, `metawalk`, `util`, and pass2/pass3 accounting state.

Risks and notes:
- The file mutates metadata trees, eattrs, bitmap state, and link counts; user choices heavily determine outcome.
- `adjust_lf_links()` is needed because adding items to `lost+found` changes its own counted link total.
- `scan_nlink1_list()` linearly scans `0..last_fs_block`, which may be expensive on large filesystems.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/pass4.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/pass5.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/pass5.c

This file implements `fsck.gfs2` pass 5, resource-group bitmap reconciliation. It compares fsck’s reconstructed block map against each on-disk resource group bitmap, optionally fixes mismatched bitmap states, and updates resource-group free/dinode counters.

`pass5(struct fsck_cx *cx, struct bmap *bl)` iterates `sdp->rgtree`, calling `update_rgrp()` for each resource group. `update_rgrp()` walks all bitmap buffers in the resource group and invokes `check_block_status()`, then compares counted free/dinode totals with `rt_free` and `rt_dinodes`.

`check_block_status()` decodes two-bit GFS2 bitmap entries, maps each block to fsck’s `block_type(bl, block)`, increments count buckets, and handles discrepancies. Blocks seen as `GFS2_BLKST_UNLINKED` are treated specially: they can be reclaimed to free, but are not automatically considered corruption because cluster deletion/open races can leave such blocks temporarily.

Dependencies include `libgfs2`, fsck context, bitmap helpers from `util.h`, resource-group structures, and interactive query handling.

Risks and notes:
- `count[5]` preserves room for legacy `GFS1_BLKST_USEDMETA`.
- If resource-group total data count does not equal the sum of counted states, the code treats it as an internal fsck error and exits.
- Counter updates mark the first bitmap buffer modified through `lgfs2_rgrp_out()`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/pass5.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/rgrepair.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/rgrepair.c

This file repairs damaged GFS2 resource-group indexes and resource-group headers/bitmap blocks. It supports multiple trust levels for the existing rindex: accept it, sanity-copy it, calculate an expected mkfs-style layout, or rebuild by scanning the device.

The public entry point is `rindex_repair(struct fsck_cx *cx, int trust_lvl, int *ok)`. Depending on `trust_lvl`, it calls:
- `expect_rindex_sanity()` when the rindex seems sane.
- `rindex_calculate()` to compute expected RG layout from device geometry and rindex count.
- `rindex_rebuild()` to scan for RGs, including uneven layouts from converted/grown GFS filesystems.

Important helper paths:
- `find_journaled_rgs()` scans journal contents and records RG-looking false positives so journaled RG copies are ignored during rebuild.
- `find_shortest_rgdist()` samples RG spacing and detects grow segments.
- `find_next_rgrp_dist()` and `hunt_and_peck()` infer uneven or damaged next-RG distances.
- `compute_rgrp_layout()` and `calc_rgrps()` build expected `lgfs2_rgrp_tree` entries.
- `rewrite_rg_block()` reconstructs missing/corrupt RG or RB headers after user approval.

After building expected data in `rgcalc`, `rindex_repair()` rereads the on-disk rindex, handles invalid rindex size, compares actual and expected entries, writes fixed entries through `lgfs2_writei()`, recomputes bitmap structures, then reads actual resource groups and repairs damaged RG/RB blocks.

Dependencies include libgfs2 geometry/rgrp APIs, journal initialization/recovery helpers, special-block tracking, direct `pread`/`pwrite`, and fsck query/logging.

Risks and notes:
- Rebuild logic assumes maximum RG size constraints and uses heuristics/tolerances; too many discrepancies abort the chosen repair level.
- It frees and rebuilds `sdp->rgtree` in several modes, so callers must expect rgrp state invalidation.
- Repairs occur before normal pass allocation is available, so the code cannot grow the rindex beyond existing file space.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/rgrepair.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/util.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/util.c

This file provides shared fsck utilities for progress display, interactive prompts, duplicate-block tracking, directory tree tracking, bitmap scans, and cleanup helpers.

Major functions:
- `big_file_comfort()` and `display_progress()` throttle progress output by time and percentage.
- `fsck_getch()`, `generic_interrupt()`, and `fsck_query()` implement interactive yes/no handling, Ctrl-C handling, and global error counters.
- `add_duplicate_ref()`, `find_dup_ref_inode()`, `count_dup_meta_refs()`, `get_ref_type()`, `dup_listent_delete()`, `dup_delete()`, and `delete_all_dups()` maintain duplicate-reference state in rbtrees and lists.
- `dirtree_insert()`, `dirtree_find()`, and `dirtree_delete()` maintain the directory-info rbtree.
- `find_free_blk()` scans resource-group bitmaps for a free block.
- `get_dir_hash()` reads an exhash directory hash table.
- `print_pass_duration()` formats pass runtime.

Dependencies include `libgfs2`, `metawalk`, `logging`, `osi_tree`, and `osi_list` structures through fsck data types.

Risks and notes:
- Several globals are updated or consulted: `errors_found`, `errors_corrected`, `fsck_abort`, `last_fs_block`, progress markers, and duplicate counters.
- `fsck_query()` returns auto-yes/auto-no based on options, so every repair caller inherits noninteractive behavior.
- Duplicate-reference tracking carefully separates invalid-inode references from valid/system references to guide pass1b repair decisions.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/util.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/util.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/util.h

This header declares shared fsck utility APIs and defines small inline bitmap/type helpers used across passes.

It exposes progress, query/input, duplicate-reference, directory hash, free-block, and pass-duration functions implemented in `util.c`. It also exports `reftypes[]` and duplicate-reference helpers used by duplicate-block resolution code.

Important inline helpers:
- `block_type()` decodes a two-bit fsck block-state map.
- `link1_type()` decodes a one-bit link bitmap.
- `link1_destroy()` frees one-bit bitmap storage.
- `bitmap_type()` reads the on-disk GFS2 resource-group bitmap state for a block.
- `block_type_string()` maps GFS2 block states to display strings.
- `is_dir()` wraps `S_ISDIR()` on `i_mode`.

The header depends on `fsck.h`, `libgfs2.h`, and system `stat` mode macros. It also defines `INODE_VALID`, `INODE_INVALID`, and a `stack` debugging macro that logs the current function.

Risks and notes:
- The inline bitmap helpers assume valid block indexes and initialized maps.
- `block_type()`/`link1_type()` use static locals, so they are not thread-safe, though fsck is effectively single-threaded.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/util.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/glocktop/Makefile.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/glocktop/Makefile.am

This Automake fragment builds the `glocktop` utility as an sbin program from `glocktop.c`.

Build configuration:
- `sbin_PROGRAMS = glocktop`
- `glocktop_SOURCES = glocktop.c`
- Adds ncurses flags through `glocktop_CFLAGS`.
- Defines `_GNU_SOURCE` via `glocktop_CPPFLAGS`.
- Links against `gfs2/libgfs2/libgfs2.la`, ncurses libraries, and uuid libraries.

The file is narrow build glue. Its main integration point is ensuring `glocktop` has libgfs2 and ncurses support available at link time.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/glocktop/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/glocktop/glocktop.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/glocktop/glocktop.c

This file implements `glocktop`, a GFS2 glock monitor that reads kernel debugfs and procfs state, correlates GFS2 glocks with DLM locks and mounted filesystems, and displays contention interactively with curses or as plain terminal output.

Main behavior is in `main()`: parse options, discover GFS2 mounts and debugfs, initialize curses if requested, allocate large read buffers, then repeatedly scan `debugfs/gfs2/*/glocks` and related `debugfs/dlm/*_{waiters,locks}` files. It supports filtering by glock id, delay/iteration control, held-lock display suppression, DLM display suppression, summary interval, reservation display, help pages, and directory path tracing.

Important components:
- `parse_mounts()` reads `/proc/mounts`, opens GFS2 devices, reads superblocks, and identifies debugfs.
- `parse_dlm_waiters()` and `parse_dlm_grants()` parse DLM debugfs state into fixed arrays.
- `glock_details()` parses glock records, computes summary counts by lock type/state, and decides which glocks to display.
- `show_glock()` prints detailed and friendly views, including lock type, inode type, DLM grants/waiters, holder/waiter pids, and call traces from `/proc/<pid>/stack`.
- `show_details()` maps debugfs fs names to mount devices and can call `show_inode()`/`display_filename()` to classify or trace inode locks.
- Curses helpers handle colors, screen resizing, prompts, title lines, and help.

Dependencies include libgfs2 inode/superblock APIs, curses/termcap, debugfs, DLM configfs/debugfs files, `/proc`, mount table parsing, and Linux block-device ioctls.

Risks and notes:
- The parser relies on fixed kernel debugfs text formats and fixed-width buffers.
- Several arrays are fixed-size (`MAX_LINES`, `MAX_FILES`, glock line width), and not every producer has a clear bounds guard.
- Running may require root privileges, mounted debugfs, readable GFS2 devices, and kernel support for GFS2/DLM debug outputs.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/glocktop/glocktop.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/include/Makefile.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/include/Makefile.am

This Automake fragment declares private headers for the GFS2 userspace build.

It marks `Makefile.in` as maintainer-clean and lists `noinst_HEADERS`:
- `osi_list.h`
- `osi_tree.h`
- `linux/gfs2_ondisk.h`
- `linux/types.h`
- `logging.h`

These headers are not installed as public system headers by this target; they are internal build inputs for the gfs2-utils source tree.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/include/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/include/linux/gfs2_ondisk.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/include/linux/gfs2_ondisk.h

This header defines the GFS2 on-disk ABI structures, constants, metadata formats, flags, and block-state values used by userspace tools. It mirrors kernel-facing layout definitions with big-endian fixed-width fields.

Major contents:
- Global magic/basic-block constants and superblock address/lock constants.
- Metadata format and metatype values for superblocks, resource groups, dinodes, indirect blocks, leaves, journals, log descriptors, eattrs, and quota changes.
- Core packed-on-disk structures: `gfs2_inum`, `gfs2_meta_header`, `gfs2_sb`, `gfs2_rindex`, `gfs2_rgrp`, `gfs2_quota`, `gfs2_dinode`, `gfs2_dirent`, `gfs2_leaf`, `gfs2_ea_header`, `gfs2_log_header`, `gfs2_log_descriptor`, `gfs2_inum_range`, `gfs2_statfs_change`, `gfs2_quota_change`, and quota/resource LVB structures.
- Bitmap encoding definitions: `GFS2_NBBY`, `GFS2_BIT_SIZE`, `GFS2_BIT_MASK`, `GFS2_BLKST_*`.
- Dinode flags and directory entry conversion macros `DT2IF()`/`IF2DT()`.

Dependencies include local userspace `linux/types.h` for `__be*`/`__u*` style types and standard mode bits used by macros.

Risks and notes:
- This file is layout-critical; field order, sizes, and endian annotations must stay compatible with the filesystem format.
- Many fields preserve historical GFS1 padding/semantics, so apparent unused fields are ABI-relevant.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/include/linux/gfs2_ondisk.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/include/linux/types.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/include/linux/types.h

This header supplies userspace definitions needed by `gfs2_ondisk.h` for Linux-style integer and endian-annotated types.

It includes `<asm/types.h>` and `<stdint.h>`, defines sparse-style `__bitwise` and `__force` annotations when `__CHECKER__` is active, and typedefs:
- `__le16`, `__be16`
- `__le32`, `__be32`
- `__le64`, `__be64`

The file is a compatibility shim so userspace gfs2-utils code can share kernel-like on-disk structure declarations without depending directly on the full kernel header environment.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/include/linux/types.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/include/logging.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/include/logging.h

This header defines simple logging macros gated by a global `print_level`.

It declares verbosity controls and message levels from debug through critical:
- `increase_verbosity()`, `decrease_verbosity()`
- `MSG_DEBUG`, `MSG_INFO`, `MSG_NOTICE`, `MSG_WARN`, `MSG_ERROR`, `MSG_CRITICAL`, `MSG_NULL`
- `log_debug`, `log_info`, `log_notice`, `log_warn`, `log_err`, `log_crit`

`log_debug()` prefixes messages with function name and line number. Info/notice/warn write to stdout, while error/critical write to stderr.

Risks and notes:
- The macros rely on GNU variadic macro syntax.
- There is no synchronization or structured logging; output ordering is suitable for single-process CLI tools.
- Callers must define `print_level` exactly once elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/include/logging.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/include/osi_list.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/include/osi_list.h

This header provides a minimal intrusive doubly linked list implementation.

It defines `struct osi_list`, `osi_list_t`, and macros for:
- Static declaration and initialization.
- Empty checks.
- Container lookup via `osi_list_entry`.
- Adding after or before a list head.
- Deleting, deleting with reinitialization.
- Forward iteration and safe forward iteration while deleting.

The API is modeled after kernel-style intrusive lists and is used by fsck duplicate-reference lists and other gfs2-utils structures.

Risks and notes:
- The macros do no membership validation.
- `osi_list_entry` uses pointer arithmetic on a null typed pointer, a common but low-level C container pattern.
- Safe iteration assumes the list is not concurrently modified outside the current loop.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/include/osi_list.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/include/osi_tree.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/include/osi_tree.h

This header implements an intrusive red-black tree adapted from Linux kernel rbtree code. It is used for ordered fsck/libgfs2 structures such as directory trees, duplicate-block trees, and resource-group trees.

It defines:
- `struct osi_node` with parent/color packed into `osi_parent_color`.
- `struct osi_root`.
- Color/parent accessors and mutators.
- `osi_link_node()` for attaching a new node before rebalancing.
- Insert rebalancing via `osi_insert_color()`.
- Erase rebalancing via `osi_erase()` and `__osi_erase_color()`.
- Ordered traversal helpers `osi_first()`, `osi_last()`, `osi_next()`, `osi_prev()`.
- `osi_replace_node()`.

The implementation is entirely inline in the header. Callers are responsible for key comparisons and embedding `struct osi_node` in their own container types.

Risks and notes:
- The tree API assumes caller-managed ordering and node lifetime.
- `__osi_erase_color()` expects sibling pointers in typical rbtree erase cases; corrupt tree state would crash.
- Parent/color bit packing assumes pointer alignment leaves low bits available.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/include/osi_tree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/init.d/gfs2 -->
# File Research: sources/local-fs/gfs2-utils/gfs2/init.d/gfs2

This shell script is a SysV init helper for mounting and unmounting GFS2 filesystems configured in `/etc/fstab`.

It supports `start`, `stop`, `status`, `restart`, `reload`, `force-reload`, `condrestart`, and `try-restart`. It sources distro-specific configuration from `/etc/sysconfig/*` or `/etc/default/*`, selects a lock file path, requires `/proc/mounts`, and computes:
- `GFS2FSTAB`: non-`noauto` GFS2 mountpoints from `/etc/fstab`.
- `GFS2MTAB`: active GFS2 mountpoints from `/proc/mounts`, excluding `/`.

`start` runs `mount -a -t gfs2`, touches the lock file, and reports status. `stop` runs `umount -a -t gfs2`, attempts `modprobe -r gfs2`, removes the lock file, and reports status. `status` detects stale lock files and prints configured/active mountpoints.

Risks and notes:
- It assumes legacy cluster stack dependencies (`cman`, `gfs_controld`).
- Some variable expansions are unquoted, matching older init-script style but potentially fragile for unusual paths.
- It exits `6` when no GFS2 fstab entries are configured.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/init.d/gfs2 -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/Makefile.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/Makefile.am

This Automake fragment builds the internal `libgfs2.la` library and the `gfs2l` helper program.

Key build declarations:
- Generated parser/lexer files are cleaned and partially treated as built sources.
- `_GNU_SOURCE` and uuid CFLAGS are added globally.
- Internal headers include `libgfs2.h`, `crc32c.h`, `lang.h`, and `rgrp.h`.
- `libgfs2_la_SOURCES` include core filesystem logic: CRC, bitmap, misc, rgrp, superblock, buffers, disk hash, ondisk conversion, geometry, fs ops, recovery, structures, and metadata.
- `gfs2l` is built from language/parser sources and links `libgfs2.la` plus uuid.
- `lexer.h` is generated manually from `lexer.l`.
- `checks.am` is included only when `HAVE_CHECK` is enabled.

This file controls the library surface consumed by fsck, mkfs, glocktop, and tests.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/buf.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/buf.c

This file implements simple block buffer allocation, reading, writing, release, discard-free, and metadata-type detection for libgfs2.

Functions:
- `lgfs2_bget()` allocates a `struct lgfs2_buffer_head` plus one block-sized data buffer and initializes block number, superblock pointer, and data pointer.
- `__lgfs2_bread()` allocates a buffer and reads one filesystem block with `pread()`, reporting caller/line on failure.
- `lgfs2_bwrite()` writes a modified buffer to its block offset with `pwrite()` and clears `b_modified`.
- `lgfs2_brelse()` writes modified buffers, removes them from `b_altlist` if linked, marks the block number invalid, and frees memory.
- `lgfs2_bfree()` frees without writing and nulls the caller’s pointer.
- `lgfs2_get_block_type()` reads a `gfs2_meta_header` and returns its metatype if the magic matches.

Dependencies include `libgfs2.h`, POSIX I/O, and GFS2 endian helpers.

Risks and notes:
- `lgfs2_brelse()` auto-writes modified buffers, so callers must use `lgfs2_bfree()` when they need discard semantics.
- Partial I/O is treated as failure.
- There is only a debug print for double-free detection via block number `-1`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/buf.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_fs_ops.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_fs_ops.c

This file contains Check unit tests for selected `fs_ops.c` behaviors and allocation APIs.

It builds mock filesystem fixtures using a temporary unlinked file as a block device. `mockup_fs()` creates an `lgfs2_sbd`, sizes the mock device, sets block size, and computes constants. `mockup_rgs()` plans and appends resource groups, allocates bit buffers, and attaches them to the mock superblock.

Test cases:
- `test_lookupi_bad_name_size()` verifies zero-length and too-long names fail with `ENAMETOOLONG`.
- `test_lookupi_dot()` verifies `"."` lookup returns the input directory inode.
- `test_lookupi_dotdot()` constructs a stuffed directory block containing `.` and `..` and verifies lookup returns a separate parent inode.
- `test_dinode_alloc()` verifies failed oversized dinode allocation does not change counters, then checks successful allocation updates counters and bitmap state.
- `test_meta_alloc()` verifies metadata allocation updates block counters and bitmap state.

`suite_fs_ops()` organizes tests into Check test cases with appropriate fixtures.

Risks and notes:
- Tests use fixed mock sizes and block size.
- The dotdot test hand-builds on-disk dirents, so it validates exact dirent layout assumptions.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_fs_ops.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_libgfs2.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_libgfs2.c

This is the Check test runner for libgfs2.

It declares suite factories for metadata, on-disk conversion, resource groups, and filesystem operations:
- `suite_meta()`
- `suite_ondisk()`
- `suite_rgrp()`
- `suite_fs_ops()`

`main()` creates an `SRunner` from the metadata suite, adds the other suites, runs all tests using `CK_ENV`, returns `1` if any tests failed, and `0` otherwise.

The file is narrow orchestration glue for the unit-test binary configured in `checks.am`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_libgfs2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_meta.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_meta.c

This file contains Check unit tests for libgfs2 metadata description tables.

Test cases:
- `check_metadata_sizes()` walks every `lgfs2_metadata` entry, verifies each field offset is contiguous from zero, and verifies final offset equals metadata size.
- `check_symtab()` verifies fields marked as mask/enum have a symbol table, and fields with symbol tables carry mask/enum flags.
- `check_flag_sym_value()` verifies `lgfs2_flag_sym_value()` returns zero for null/empty/invalid names and returns exact constants for all known `GFS2_DIF_*` dinode flags.
- `check_ptrs()` verifies fields marked as pointers have nonzero `points_to`, and non-pointer fields do not.

`suite_meta()` groups these tests under “Metadata description checks”.

The file depends on `libgfs2.h` metadata descriptors and the Check framework. It validates internal metadata introspection consistency rather than on-disk I/O.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_meta.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_ondisk.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_ondisk.c

This file contains Check unit tests for superblock on-disk conversion functions.

`check_sb_in()` fills a `struct gfs2_sb` buffer with `0x5a`, calls `lgfs2_sb_in()`, and verifies each relevant `lgfs2_sbd` field individually, including formats, block size, master/root inums, lock protocol/table, and uuid.

`check_sb2_out()` populates an `lgfs2_sbd` with distinct values, calls `lgfs2_sb_out()`, and verifies the resulting `struct gfs2_sb` contains the expected big-endian values and copied fixed-size string/uuid fields.

`suite_ondisk()` groups both tests under “On-disk structure parsing checks”.

The file validates endian conversion and field mapping for the GFS2 superblock. It depends on `libgfs2.h`, GFS2 on-disk structures, and Check.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_ondisk.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_rgrp.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_rgrp.c

This file contains Check unit tests for resource-group planning, bitmap search, and final RG write behavior.

The fixture `mockup_rgrps()` creates a 1 GiB temporary mock device, initializes an `lgfs2_sbd`, plans resource groups, creates the first rindex entry, appends a resource group, allocates bitmap buffers, and stores it in `tc_rgrps`. `teardown_rgrps()` closes/free resources and bitmap buffers.

Test cases:
- `test_rbm_find_good()` verifies `lgfs2_rbm_find()` can find free extents from size 1 through the whole RG.
- `test_rbm_find_bad()` verifies requesting an extent larger than the RG data area fails.
- `test_rbm_find_lastblock()` marks all blocks allocated except the final block and verifies the search finds that last free block.
- `test_rgrps_write_final()` verifies `lgfs2_rgrps_write_final()` writes a valid final RG header with `rg_skip == 0`, and returns `-1` on an invalid fd.

`suite_rgrp()` groups rbm search tests and final-write tests with fixtures.

Risks and notes:
- `test_rbm_find_good()` disables timeout because it can iterate many extent sizes.
- The tests validate both in-memory bitmap manipulation and actual pwrite/pread behavior against a temporary file.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_rgrp.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/checks.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/checks.am

This Automake fragment defines the libgfs2 Check test program.

It sets:
- `TESTS = check_libgfs2`
- `check_PROGRAMS = $(TESTS)`

`check_libgfs2_SOURCES` combines the test runner and test files with the libgfs2 implementation files needed for a standalone test binary, including metadata, rgrp, CRC, disk hash, ondisk, buffer, geometry, fs ops, structures, bitmaps, misc, recovery, and superblock code.

It adds Check and uuid CFLAGS, and links against Check and uuid libraries.

This file is included from `Makefile.am` only when `HAVE_CHECK` is true.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/libgfs2/checks.am -->