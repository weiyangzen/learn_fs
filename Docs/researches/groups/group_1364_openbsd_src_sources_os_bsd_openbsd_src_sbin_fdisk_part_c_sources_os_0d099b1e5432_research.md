# Group Research: group_1364_openbsd_src_sources_os_bsd_openbsd_src_sbin_fdisk_part_c_sources_os_0d099b1e5432

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/part.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/part.c

Implements fdisk partition type lookup, display, and conversion helpers for both MBR and GPT partition tables.

Major contents:
- Defines known MBR partition type IDs and descriptions, with OpenBSD, BSD, DOS/FAT, Linux, EFI, Solaris, macOS, Plan 9, and many legacy IDs.
- Defines known GPT partition type GUID constants and `gpt_types`, including OpenBSD, EFI system, Microsoft basic data, Linux, BSD, macOS/APFS, ChromeOS kernel, and protected platform/firmware partitions.
- Defines the user-facing partition type menu table shared by MBR and GPT prompts.
- Provides menu filtering/printing for MBR-only and GPT-capable partition types.
- Maps between MBR IDs, GPT GUIDs, menu names, and short hexadecimal menu IDs.

Conversion and validation behavior:
- `PRT_dp_to_prt` converts on-disk DOS partition entries into internal `struct prt`, including extended-MBR offset rules and EFI protective size handling.
- `PRT_prt_to_dp` converts internal partitions back to MBR disk entries, calculating CHS fields and LBA start/size fields.
- `PRT_lba_to_chs` converts LBA ranges into CHS tuples using current disk geometry.
- `chs_to_dp` clamps out-of-range CHS values to force LBA-style interpretation.
- `PRT_print_part` prints one MBR partition and warns if it starts or extends beyond disk size.
- `PRT_uuid_to_desc` and `PRT_desc_to_guid` translate GPT UUIDs to display/menu identifiers and parse names, GUID strings, or menu IDs back to GUIDs.
- `PRT_protected_uuid` protects selected GPT partition types from modification, with extra EFI system protection when protected EFI-dependent GPT types are present.

This file is the central fdisk partition-type knowledge base and the bridge between on-disk MBR/GPT identifiers and interactive user-facing names.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/part.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/part.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/part.h

Declares fdisk’s partition geometry and internal partition records.

Key structures:
- `struct chs` stores cylinder/head/sector coordinates.
- `struct prt` stores internal partition state: base sector, sector count, boot flag, and partition ID.

Exports:
- MBR/GPT partition type menu printers.
- DOS partition to internal partition conversion, and reverse conversion.
- Partition table header and row printers.
- GPT UUID description and parser helpers.
- GPT protected-type check.
- LBA-to-CHS conversion.

The header is consumed by fdisk modules that need partition display, editing, conversion, and type lookup without embedding the large tables from `part.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/part.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/user.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/user.c

Implements fdisk’s interactive command loop and top-level disk printing.

Core behavior:
- Defines the interactive command table: `help`, `manual`, `reinit`, `setpid`, `edit`, `flag`, `update`, `select`, `swap`, `print`, `write`, `exit`, `quit`, and `abort`.
- Tracks whether the current edit level has uncommitted changes with global `modified`.
- `USER_edit` reads the current MBR, loads GPT state on the outer edit level, prompts as `<disk>[*]: <level>`, dispatches commands, and handles clean/dirty/exit/quit status returns.
- Recursive edit levels are used for extended MBRs; GPT reinitialization unwinds nested MBR editing.
- `USER_print_disk` prints primary/secondary GPT state when present, then walks the MBR and any extended MBR chain.
- `USER_help` filters commands by partition table validity and GPT context.
- `ask_cmd` parses one command line, supports `?` as `help`, accepts command prefixes, and rejects unavailable or ambiguous context-inappropriate commands.

This is the user interaction layer that connects parsed commands to the lower-level MBR/GPT editing functions.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/user.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/user.h

Small fdisk user-interface header declaring:
- `USER_edit` for entering the interactive editor at a given MBR LBA context.
- `USER_print_disk` for noninteractive disk table display.
- `USER_help` for context-sensitive command help.

It depends on `struct mbr` being visible to callers that use `USER_help`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fdisk/user.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck/Makefile

Builds the generic `fsck` dispatcher program from `fsck.c`, `fsutil.c`, and `preen.c`.

Notable build settings:
- Installs `fsck.8`.
- Links against `libutil`.
- Uses the standard OpenBSD `bsd.prog.mk` program build rules.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck/fsck.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck/fsck.c

Implements the generic `fsck` front-end that selects filesystems and execs filesystem-specific helpers such as `fsck_ffs` or `fsck_ext2fs`.

Main flow:
- Raises data-size limits, initializes root-device state, unveils `/dev`, `/etc/fstab`, and fsck helper directories, then pledges restricted capabilities.
- Parses global flags such as debug, verbose, preen, no/yes answers, alternate superblock, type selection, network filtering, parallel limit, and per-filesystem `-T type:options`.
- If no operands are given, scans `/etc/fstab` through `checkfstab`.
- If operands are given, resolves device names, DUIDs, mount points, and fstab entries, then checks each requested target.

Selection and dispatch:
- `isok` filters fstab entries by pass number, rw/ro/rq type, network option, and selected filesystem type list.
- `checkfs` normalizes `ufs` to `MOUNT_UFS`, constructs `fsck_<vfstype>` argv, combines global/per-type options, forks, and execs helper binaries from `/sbin` or `/usr/sbin`.
- `maketypelist` supports include and `no...` exclude type lists.
- `mangle` converts comma-separated options into helper argv, splitting `-x=value` into separate option/value arguments.
- `addoption` stores per-filesystem option strings in a TAILQ.

The file does not repair filesystems itself; it is an option parser, fstab selector, and subprocess launcher for concrete fsck implementations.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck/fsck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck/fsutil.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck/fsutil.c

Provides shared utility routines for generic `fsck` and filesystem-specific checkers.

Important behavior:
- `checkroot` records `stat("/")` for root-device comparisons.
- `setcdevname`, `cdevname`, and `hotroot` manage current device name and root-filesystem detection state.
- `pfatal`, `pwarn`, `panic`, `errexit`, and `xperror` centralize formatted diagnostics, including preen-mode prefixes and fatal “run manually” behavior.
- `rawname` maps a block device path to a raw character device path by inserting `r` after the final slash.
- `unrawname` reverses raw character device names when possible.
- `blockcheck` resolves block, character, and fstab mountpoint names into raw device names, detects hot root, and validates character devices.
- `emalloc`, `ereallocarray`, and `estrdup` are fail-fast allocation wrappers.

This file is the common device-name and error-reporting substrate shared by the dispatcher and fsck helpers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck/fsutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck/fsutil.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck/fsutil.h

Declares shared fsck utility functions and status flags.

Exports:
- Error and warning reporting helpers.
- Raw/block device name conversion.
- Root/device setup and hot-root detection.
- Checked allocation wrappers.
- `checkfstab`, the preen/fstab scheduling entry point.

Defines dispatcher flags:
- `CHECK_PREEN`
- `CHECK_VERBOSE`
- `CHECK_DEBUG`

This header is included by the generic fsck front-end and by filesystem-specific checkers for consistent diagnostics, device handling, and fstab orchestration.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck/fsutil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck/pathnames.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck/pathnames.h

Defines fsck helper search directories:
- `_PATH_SBIN` as `/sbin`
- `_PATH_USRSBIN` as `/usr/sbin`

`fsck.c` uses these paths when locating and execing filesystem-specific helper programs named `fsck_<fstype>`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck/pathnames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck/preen.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck/preen.c

Implements `/etc/fstab` traversal and preen-mode scheduling for the generic `fsck` front-end.

Core model:
- Builds per-disk queues of partitions to check, using a disk base name derived by trimming trailing partition digits.
- Runs pass 1 filesystems immediately and serially.
- In preen mode, queues later-pass filesystems by disk and runs checks in parallel across disks, never concurrently checking multiple partitions on the same disk.
- Honors `-l maxparallel`, defaulting to the number of disks.

Important structures:
- `partentry` stores filesystem type, device name, mount point, and caller auxiliary data.
- `diskentry` stores one disk base name, its partition queue, and the active child pid.
- `badh` accumulates failed filesystems for final reporting.

Important functions:
- `checkfstab` loops pass numbers, applies the caller’s fstab filter, normalizes device names with `blockcheck`, runs or queues checks, waits for children, and reports aggregate failures.
- `finddisk` groups device names into disk queues.
- `addpart` appends a filesystem to a disk queue and warns about duplicate fstab devices.
- `startdisk` starts the next queued filesystem check for a disk and records its pid.

This file is responsible for safe preen parallelism and pass-order handling, not filesystem-specific repair logic.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck/preen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/Makefile

Builds the `fsck_ext2fs` checker.

Sources:
- Ext2-specific fsck passes and helpers: `dir.c`, `inode.c`, `main.c`, `pass1.c`, `pass1b.c`, `pass2.c`, `pass3.c`, `pass4.c`, `pass5.c`, `setup.c`, `utilities.c`.
- Shared generic fsck utility source: `fsutil.c`.
- Kernel ext2 byte-swap support: `ext2fs_bswap.c`.

Build details:
- Adds search paths for kernel ext2fs sources and shared fsck sources.
- Adds `../fsck` to include path.
- Links with `libutil`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/dir.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/dir.c

Implements ext2 directory scanning, validation, entry repair, orphan reconnection, and lost+found handling.

Directory traversal:
- `dirscan` walks directory blocks and applies the caller-provided `inodesc` callback to each entry.
- `fsck_readdir` validates and returns the next `ext2fs_direct` entry, salvaging corrupted directory blocks by creating empty records when allowed.
- `dircheck` enforces ext2 directory entry invariants: valid inode number, nonzero aligned record length, record fitting inside the block, valid name length, no embedded NUL or slash, and optional ext2 file-type rules.

Connectivity and repairs:
- `propagate` builds child/sibling links from cached directory inodes and marks directories reachable from root as `DFOUND`.
- `fileerror` and `direrror` print inode and pathname diagnostics.
- `adjust` corrects inode link counts or clears unreferenced objects.
- `makeentry`, `changeino`, `mkentry`, and `chgino` insert or modify directory entries.
- `expanddir` attempts to grow a directory by allocating a new block and splitting existing content.
- `allocdir` creates a new directory inode with `.` and `..`, initializes link counts, and updates parent accounting.
- `linkup` reconnects unreferenced files/directories into `lost+found`, creating or reallocating `lost+found` when necessary.
- `freedir` and `lftempname` support rollback and generated `#<ino>` names.

The implementation is ext2-aware: it handles little-endian fields, ext2 directory file-type feature bits, ext2 block size, ext2 root inode numbering, and ext2 inode mode/type conversion.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/extern.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/extern.h

Declares cross-file interfaces for `fsck_ext2fs`.

The prototypes cover:
- Directory repair and link-count adjustment.
- Block/inode allocation and freeing.
- Buffered device I/O.
- Inode cache and traversal.
- Directory entry scanning and validation.
- Pathname reconstruction and inode diagnostics.
- The five fsck passes and their block callbacks.
- Setup/cleanup and signal handlers.

This header is the internal linkage contract among ext2fs checker modules.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/fsck.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/fsck.h

Defines shared data structures, constants, state maps, and globals for `fsck_ext2fs`.

Important definitions:
- Limits for duplicate/bad blocks and buffer sizes.
- Inode state values: `USTATE`, `FSTATE`, `DSTATE`, `DFOUND`, `DCLEAR`, `FCLEAR`.
- `bufarea`, the checker’s small block buffer cache record.
- `inodesc`, the generic descriptor passed through block and directory scans.
- Duplicate block list and zero-link-count inode list structures.
- Directory inode cache structure `inoinfo`.
- Global ext2 superblock state, file descriptors, maps, counters, and flags.

Important macros:
- `dirty`, `initbarea`, and `sbdirty` for buffer/superblock dirty tracking.
- Block map operations `setbmap`, `testbmap`, `clrbmap`.
- Callback return flags `STOP`, `SKIP`, `KEEPON`, `ALTERED`, `FOUND`.

The header binds all ext2 fsck phases to shared mutable state: allocation maps, inode state, link counts, directory caches, duplicate block tracking, and superblock metadata.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/fsck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/inode.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/inode.c

Implements ext2 inode traversal, inode cache management, inode allocation/freeing, and inode diagnostics.

Block traversal:
- `ckinode` walks direct and indirect block pointers for an inode, dispatching either block-address callbacks or directory scans.
- `iblock` recursively handles single/double/triple indirect blocks and clears partially truncated indirect entries when repairing.
- Empty directory blocks can trigger directory length adjustment and request a rerun.

Size and range handling:
- `inosize` reads 64-bit regular-file sizes using `e2di_size_hi`.
- `inossize` writes sizes and ensures large-file feature bits are set for large regular files.
- `setlarge` repairs the ext2 large-file rocompat feature when needed.
- `chkrange` validates block numbers against filesystem bounds and per-group metadata/data regions.

Inode access:
- `ginode` reads the inode block containing a requested inode.
- `getnextinode`, `resetinodebuf`, and `freeinodebuf` implement sequential buffered inode reading for pass 1.
- `cacheino`, `getinoinfo`, and `inocleanup` maintain the directory inode cache used by later passes.

Repair helpers:
- `clri` clears an inode and releases its blocks.
- `findname` and `findino` support pathname construction and directory lookup.
- `pinode` prints owner, mode, size, and mtime.
- `blkerror` marks file/directory state for duplicate or bad blocks.
- `allocino` creates a new inode and first block.
- `freeino` releases an inode through pass4 block cleanup.

This file is the core metadata traversal layer beneath ext2 fsck’s pass logic.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/main.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/main.c

Implements the `fsck_ext2fs` command entry point and phase driver.

Main behavior:
- Parses options for alternate superblock, debug, force check, lost+found mode, assume-no, preen, and assume-yes.
- Calls shared root/device setup, syncs before checking, installs interrupt/quit handlers, and checks exactly one filesystem operand.
- Maintains all major global fsck state: buffers, ext2 superblock, duplicate lists, inode caches, maps, counters, flags, and file descriptors.

`checkfilesys` flow:
1. Runs `setup` and skips clean filesystems when allowed.
2. Phase 1: scans inodes, block usage, sizes, and initial state.
3. Phase 1b: rescans for duplicate block owners if duplicates were found.
4. Phase 2: checks pathnames and directory contents.
5. Phase 3: checks directory connectivity.
6. Phase 4: checks reference counts and clears/reconnects unreferenced objects.
7. Phase 5: verifies group bitmaps and summary counts.
8. Prints file/block summary, updates fsck timestamps when modified, cleans up, and marks the filesystem clean when appropriate.

Root handling:
- If the root filesystem was modified and mounted read-only, attempts a mount update/reload.
- Otherwise requests reboot semantics via exit code when needed.

This file coordinates the ext2 checker lifecycle; the pass files contain the detailed checks.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass1.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass1.c

Implements ext2 fsck phase 1: block and inode size checking.

Major work:
- Marks reserved filesystem metadata blocks as used in `blockmap`: inode tables, block bitmaps, inode bitmaps, superblock/group descriptor copies, and pre-first-data blocks.
- Sequentially reads all inodes with the optimized inode buffer.
- Classifies each inode into unused, file, directory, duplicate/bad clear states, or unknown.
- Tracks file count, link counts, zero-link allocated inodes, last used inode, inode types, and cached directory inode metadata.
- Detects and optionally clears partially allocated or unknown-type inodes.
- Validates deleted-time fields on allocated inodes and can clear stale deletion times.
- Checks for impossible sizes, garbage block pointers after file end, bad file types, and incorrect block counts.

`pass1check` validates each block reference:
- Flags out-of-range blocks as bad.
- Adds new blocks to the allocation bitmap.
- Records duplicate blocks in the duplicate list.
- Enforces per-inode limits on reported bad and duplicate blocks.
- Counts visited blocks for later comparison with inode `e2di_nblock`.

This pass establishes the allocation and inode-state facts used by all later ext2 checks.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass1b.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass1b.c

Implements ext2 fsck phase 1b: duplicate-block owner discovery.

Behavior:
- Runs only when phase 1 found duplicate blocks.
- Rescans all allocated inodes with `pass1bcheck`.
- For every block reference matching the duplicate list, reports a duplicate block error for that inode.
- Reorders/removes duplicate-list entries as duplicates are accounted for.
- Stops when all unique duplicate blocks through `muldup` have been found.

This phase identifies the first and later inode owners of duplicate blocks before phase 4 decides what to clear or free.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass1b.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass2.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass2.c

Implements ext2 fsck phase 2: pathname and directory entry checking.

Top-level flow:
- Ensures the root inode exists and is a directory, reallocating or fixing it when approved.
- Sorts cached directories by first block for efficient disk access.
- Checks each directory’s size, block alignment, and contents through `pass2check`.
- Performs a second pass over cached directories to verify or repair `..` parent links.
- Calls `propagate` to mark directories reachable from root.

Directory entry checks:
- Verifies and repairs `.` inode number and file type.
- Verifies, creates, or repairs `..` entries.
- Removes extra `.` and `..` entries after the first two slots.
- Removes entries pointing outside the inode range, unallocated inodes, or clear-pending inodes when approved.
- Detects extraneous hard links to directories.
- Records parent directory relationships.
- Decrements link-count accounting for every valid observed directory entry.
- Repairs ext2 directory file-type fields when the filesystem supports them.

This phase turns the raw directory cache from phase 1 into a connected directory graph and accurate observed link counts.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass3.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass3.c

Implements ext2 fsck phase 3: directory connectivity repair.

Behavior:
- Walks cached directory inodes in reverse order.
- Finds directories not reachable from root, directories without parents, and directory loops.
- Selects an orphan directory to reconnect.
- Calls `linkup` to attach it to `lost+found`.
- Updates cached parent/dotdot state, adjusts `lost+found` link count accounting, marks the orphan as found, and reruns connectivity propagation.

This pass specifically handles disconnected directory subtrees after pathname validation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass4.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass4.c

Implements ext2 fsck phase 4: reference count and unresolved inode cleanup.

Top-level behavior:
- Iterates allocated inodes through `lastino`.
- For regular files and connected directories, adjusts nonzero remaining link-count deltas or clears zero-link inodes tracked in `zlnhead`.
- Clears unreferenced directories still in `DSTATE`.
- Clears zero-length directories marked `DCLEAR`.
- Clears bad/duplicate files and directories marked `FCLEAR` or `DCLEAR`.

`pass4check` is the block-release callback:
- Skips out-of-range blocks.
- For allocated blocks, removes duplicate-list records when present.
- If a block is not still duplicated, clears it from the block map and decrements used block count.

This pass reconciles inode link counts and releases blocks from inodes that earlier phases decided cannot remain allocated.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass5.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass5.c

Implements ext2 fsck phase 5: bitmap and summary information verification.

For each block group:
- Reconstructs an inode bitmap from `statemap`.
- Reconstructs a block bitmap from `blockmap` and filesystem size bounds.
- Counts free blocks, free inodes, and directories.
- Marks reserved/invalid inode slots used in the reconstructed inode map.
- Compares reconstructed counts with group descriptor counts.
- Compares reconstructed block and inode bitmaps with on-disk bitmaps.
- Repairs mismatched group summaries and bitmaps when `dofix` approves.

After all groups:
- Accumulates global free block and inode counts.
- Compares them with superblock summary fields.
- Repairs superblock free block/inode totals when approved.

Includes `print_bmap` for debug dumping bitmap byte arrays.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/setup.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/setup.c

Initializes an ext2 filesystem check: device opening, superblock validation, feature checks, map allocation, and buffer setup.

Setup flow:
- Opens the target via `opendev`, canonicalizes raw device names, validates character-device access, and opens a write fd unless running no-write.
- Reads disklabel sector size when available.
- Pledges down after device setup when not checking hot root.
- Reads the primary superblock, or searches alternates when requested and possible.
- Skips clean filesystems when preening/skip-clean is enabled.
- Computes dynamic ext2 in-memory fields such as block size, group count, group descriptor blocks, inodes per block, and inode-table blocks per group.
- Checks selected superblock invariants, including magic, log block size, blocks per group, reserved block count, blocks/fragments per group agreement, and unsupported feature bits.
- Reads group descriptors.
- Allocates `blockmap`, `statemap`, `typemap`, `lncntp`, and directory inode cache tables.
- Initializes the checker buffer cache.

Supporting routines:
- `readsb` loads and validates superblock state and compares primary vs alternate superblock after normalizing fields allowed to differ.
- `copyback_sb` writes in-memory ext2 superblock fields back to an on-disk buffer.
- `badsb` reports superblock failures.
- `calcsb` builds a prototype ext2 layout from disklabel data to search alternate superblocks.
- `getdisklabel` reads the OpenBSD disklabel.
- `cgoverhead` computes per-block-group metadata overhead, honoring sparse-superblock groups.

This file decides whether an ext2 filesystem is checkable and prepares all global structures for the pass pipeline.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/setup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/utilities.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/utilities.c

Provides ext2 fsck utility functions for prompting, buffer cache management, I/O, allocation, pathname reconstruction, signals, and generic fix decisions.

Key utilities:
- `ftypeok` validates supported inode file types.
- `reply` implements interactive yes/no/force-yes prompting; preen mode treats reaching `reply` as an internal error.
- `bufinit`, `getdatablk`, `getblk`, and `flush` implement a small LRU-style metadata buffer cache.
- `bread` and `bwrite` perform sector-aligned reads/writes with detailed per-sector error reporting.
- `ckfini` flushes buffers, optionally updates standard superblocks, marks clean filesystems, prints cache stats, and closes fds.
- `allocblk` and `freeblk` manage block allocation map changes.
- `getpathname` reconstructs a pathname by walking parent directories and names.
- `catch`, `catchquit`, and `voidquit` handle interrupts and preen-mode quit behavior.
- `dofix` centralizes the decision to salvage/correct a detected inconsistency, with automatic salvage in preen mode.

This file supplies the operational machinery used throughout the ext2 checker’s pass code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/utilities.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/Makefile

Builds the `fsck_ffs` checker.

Sources:
- FFS-specific checker files: `dir.c`, `inode.c`, `main.c`, `pass1.c`, `pass1b.c`, `pass2.c`, `pass3.c`, `pass4.c`, `pass5.c`, `setup.c`, `utilities.c`.
- Shared generic `fsutil.c`.
- Kernel FFS support sources: `ffs_subr.c`, `ffs_tables.c`.

Build details:
- Adds kernel FFS and shared fsck source paths.
- Adds `../fsck` to include path.
- Links with `libutil`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/SMM.doc/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/SMM.doc/Makefile

Builds the fsck_ffs SMM documentation.

Details:
- Documentation destination is `smm/03.fsck_ffs`.
- Source troff files are `0.t` through `4.t`.
- Uses `-ms` macros.
- Generates `paper.txt` by running `${ROFF} -Tascii` over the source files.
- Includes standard OpenBSD `bsd.doc.mk` rules.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/SMM.doc/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/dir.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/dir.c

Implements FFS/UFS directory scanning, validation, insertion, expansion, lost+found handling, and directory connectivity propagation.

Directory scanning:
- `dirscan` walks UFS directory entries in filesystem blocks/fragments and applies an `inodesc` callback.
- `fsck_readdir` returns the next valid `struct direct` or repairs a corrupted directory block into an empty record when allowed.
- `dircheck` validates inode range, record length, alignment, record fit, name length, file type range, no embedded NUL/slash, and required terminating NUL.

Repair behavior:
- `propagate` marks a connected directory subtree with the state of a starting inode.
- `fileerror`/`direrror` print path and inode diagnostics.
- `adjust` fixes link counts or clears unreferenced objects.
- `makeentry` and `changeino` add or rewrite directory entries.
- `expanddir` allocates a new directory block, moves existing content, fills empty directory blocks, and rolls back on failure.
- `allocdir` creates a new directory with `.` and `..`, initializes link counts, caches it, inherits parent uid/gid, and updates parent counts.
- `linkup` reconnects orphan files/directories to `lost+found`, creates/reallocates `lost+found` if needed, updates `..`, and adjusts link-count accounting.
- `freedir`, `lftempname`, and `getdirblk` support rollback, generated orphan names, and held directory-block access.

Compared with ext2’s directory code, this version uses UFS `struct direct`, `DIRBLKSIZ`, fragment-aware directory sizing, UFS inode state macros, and FFS allocation helpers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/extern.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/extern.h

Declares internal interfaces shared by `fsck_ffs` modules.

The prototypes cover:
- Directory repair and link-count adjustment.
- Block/inode allocation and freeing.
- Buffered device and cylinder group I/O.
- Inode traversal and cache management.
- Directory scanning and validation.
- Pathname lookup and inode diagnostics.
- Pass entry points and pass block callbacks.
- Setup, cleanup, signal, and info handlers.

This is the FFS checker’s internal cross-module API.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/fsck.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/fsck.h

Defines shared structures, macros, state, and globals for `fsck_ffs`.

Important definitions:
- `union dinode` abstracts UFS1 and UFS2 inode layouts.
- `DIP` and `DIP_SET` read/write the active inode format.
- Per-inode states and `struct inostat` store allocation state, directory entry type, and unresolved link count.
- `inostathead` stores inode state arrays per cylinder group.
- Macros `GET_ISTATE`, `GET_ITYPE`, `SET_ISTATE`, `SET_ITYPE`, and `ILNCOUNT` access inode state.
- `bufarea` is the metadata buffer cache record, with UFS1/UFS2 indirect and inode views.
- `IBLK` and `IBLK_SET` abstract UFS1 32-bit vs UFS2 64-bit indirect block entries.
- `inodesc` is the common descriptor for inode block and directory scans.
- Duplicate block, zero-link inode, and directory inode cache structures mirror classic fsck design.

Global state includes:
- Superblock buffers and `sblock`.
- File descriptors, flags, clean/resolved status, and alternate superblock setting.
- Allocation bitmap, max block/inode, file/block counters.
- Lost+found name/mode.
- Info callback support.

This header is the central shared state contract for the FFS checker and handles the UFS1/UFS2 split.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/fsck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/inode.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/inode.c

Implements FFS/UFS inode traversal, inode-buffered reads, directory inode caching, inode clearing, allocation, and diagnostics.

Traversal:
- `ckinode` walks direct and indirect block pointers for a UFS1/UFS2 inode.
- It skips device inodes and short symlinks that store data inline.
- It computes fragment counts for final direct blocks and dispatches either block callbacks or directory scans.
- It detects empty directory blocks and can adjust directory length while requesting a rerun.
- `iblock` recursively traverses indirect blocks, handles UFS1/UFS2 indirect entry widths, clears partially truncated entries when allowed, and descends through directory/data callbacks.

Validation and access:
- `chkrange` verifies positive block ranges, fragment alignment, fragment count, and cylinder group metadata/data bounds.
- `ginode` reads the inode block containing a specific inode.
- `getnextinode`, `setinodebuf`, and `freeinodebuf` implement sequential buffered inode reads for pass 1.

Directory inode cache:
- `cacheino` records directory inode size, parent/dotdot placeholders, and direct/indirect block addresses.
- `getinoinfo` looks cached directories up by hash.
- `inocleanup` frees directory cache structures.

Repair helpers:
- `clri` clears an inode and releases its blocks.
- `findname` and `findino` support pathname reconstruction and directory lookup.
- `pinode` prints owner, mode, size, and mtime.
- `blkerror` marks inodes for clearing after bad or duplicate block discovery.
- `allocino` allocates a free inode, extends per-cylinder-group state arrays if needed, updates cylinder group inode bitmap/counts, allocates an initial data block, initializes ownership/times/mode, and sets inode state/type.
- `freeino` releases blocks and clears inode state.

This file is the FFS checker’s core inode and block-walk layer, with explicit support for both UFS1 and UFS2 metadata formats.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/inode.c -->