# subset-b-007811 Research

Grouped research for the listed OpenAFS `vfsck` and `viced` build files. Each section preserves its source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/bcheckrc -->
# sources/distributed-fs/openafs/src/vfsck/bcheckrc

## Purpose
Boot-time HP-UX AFS filesystem check wrapper installed as `/sbin/fs/afs/bcheckrc`. It is intended to be called by the generic `/sbin/bcheckrc` path before AFS server partitions are mounted. Its job is to discover `/etc/fstab` entries whose filesystem type is `afs`, run the host HFS fsck in metadata-check mode, and invoke the AFS-specific fsck when a server partition is not clean.

## Important APIs, Types, And Functions
The script is a Bourne shell program with one local function, `afs_partitions_clean`. It uses `/sbin/awk` to parse `/etc/fstab`, `/sbin/fs/hfs/fsck -m -P` to test partition cleanliness, `/sbin/fs/afs/fsck -P -f` to repair AFS server partitions, `/sbin/stty` to establish a sane interactive terminal mode, and `ROOTSHELL=/sbin/sh` for manual repair fallback.

## Control Flow
Startup sets terminal modes, defines `ROOTSHELL`, then calls `afs_partitions_clean`. The function iterates over un-commented fstab records with field 3 equal to `afs`. For each matching device, it probes the partition with HFS fsck. A nonzero probe result triggers `fsck -P -f` through the AFS wrapper; success prints a fixed message, and any other result drops root into an interactive shell, then resumes the boot script after EOF. A flag records whether any AFS partitions were seen, and the script always exits 0 after the scan.

## State And Persistence
The script reads `/etc/fstab`, may repair on-disk AFS/HFS server partition metadata through the fsck binary, and may leave repair side effects on the checked devices. It does not persist its own state. The shell fallback can perform arbitrary manual changes because it runs as root during boot.

## Dependencies And Integration Points
This file integrates HP-UX boot sequencing, `/sbin/fs/afs/fsck`, the host HFS fsck, and OpenAFS server partition conventions. It assumes AFS partitions are listed in `/etc/fstab` with type `afs` but are physically compatible with HFS fsck probing.

## Risks And Test Signals
Risks include brittle whitespace parsing of fstab, unconditional final exit 0 even after manual repair failures, boot blocking on a root shell, and the hard-coded line break inside the warning text. Useful tests are boot-script dry runs with no AFS partitions, clean partitions, dirty partitions fixed automatically, and fsck failures that require manual mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/bcheckrc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/bcheckrc-hp_ux110 -->
# sources/distributed-fs/openafs/src/vfsck/bcheckrc-hp_ux110

## Purpose
HP-UX 11.0 variant of the AFS boot check wrapper. It performs the same `/etc/fstab` AFS partition discovery and repair orchestration as `bcheckrc`, but uses the HP-UX 11.0 HFS fsck invocation shape for its initial cleanliness probe.

## Important APIs, Types, And Functions
The only local function is `afs_partitions_clean`. It uses `/sbin/awk`, `/sbin/fs/hfs/fsck -m`, `/sbin/fs/afs/fsck -P -f`, `/sbin/stty`, and the interactive `ROOTSHELL` fallback. The significant delta from `bcheckrc` is that the probe command omits `-P` when calling `/sbin/fs/hfs/fsck -m`.

## Control Flow
The script initializes terminal settings, scans fstab for `afs` entries, and checks each partition with HFS fsck. Dirty or unclean partitions are repaired with AFS fsck in preen/force mode. If automatic repair returns nonzero, it prints an audible warning and opens `/sbin/sh` for root to run manual fsck, then continues.

## State And Persistence
Persistent effects are limited to filesystem repairs made by the invoked fsck command or by the manual root shell. The script’s own state is transient shell variables such as `serverPartition` and `name`.

## Dependencies And Integration Points
It is tied to HP-UX 11.0 boot scripts and HFS command behavior. The AFS fsck binary is expected at `/sbin/fs/afs/fsck`, and the generic boot script is expected to call this file as the filesystem-type-specific pre-mount hook.

## Risks And Test Signals
The main compatibility risk is command-line drift between HP-UX releases, which this variant addresses by changing the HFS probe. The same operational risks as `bcheckrc` remain: manual boot interruption, hard-coded paths, and always returning success to the caller. Test signals should compare HP-UX 11.0 clean/dirty fstab entries with the non-11.0 script behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/bcheckrc-hp_ux110 -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/dir.c -->
# sources/distributed-fs/openafs/src/vfsck/dir.c

## Purpose
Implements directory traversal and repair operations for OpenAFS’s UFS/HFS-derived `vfsck`. It validates directory entries, descends from root, repairs `.` and `..` relationships indirectly through pass callbacks, reconnects orphaned files and directories into `lost+found`, and can allocate, expand, and free directories during repair.

## Important APIs, Types, And Functions
Core entry points are `descend`, `dirscan`, `fsck_readdir`, `dircheck`, `direrror`, `adjust`, `mkentry`, `chgino`, `linkup`, `makeentry`, `expanddir`, `allocdir`, `freedir`, `lftempname`, and `getdirblk`. It defines `MINDIRSIZE`, `emptydir`, `dirhead`, `lfname`, `lfmode`, and the path buffer endpoints used for diagnostics. It relies on `struct inodesc`, `struct direct`, `struct dinode`, and global maps from `fsck.h`.

## Control Flow
`descend` marks a directory as found, verifies minimum size and block alignment, and calls `ckinode` with a data descriptor so `dirscan` walks directory blocks. `dirscan` iterates entries returned by `fsck_readdir`, copies each entry into a scratch buffer for the pass-specific callback, and writes altered entries back to the cached directory block. `fsck_readdir` enforces directory-block boundaries and can collapse corrupt records into empty entries. `dircheck` validates inode range, record length, alignment, name length, and name termination.

Repair helpers are callback-driven. `mkentry` splits free record space to insert a name, `chgino` retargets an existing entry, and `makeentry` scans a parent before expanding the directory if needed. `linkup` creates or validates `lost+found`, reconnects orphans, fixes an orphaned directory’s `..`, and adjusts link counts. `allocdir` creates a new directory inode with initialized `.` and `..`; `expanddir` inserts a new block before the last block and initializes empty directory blocks.

## State And Persistence
This file mutates directory data blocks, inode sizes, direct block pointers, link counts, `statemap`, `lncntp`, `lfdir`, `pathname`, `pathp`, and buffer dirty flags. Durable changes are written later through the buffer cache. HP-UX ACL continuation inode flags are preserved in state transitions where applicable.

## Dependencies And Integration Points
Directory repair is used by pass 2 path traversal, pass 3 orphan reconnection, pass 4 link adjustment, and inode allocation/free logic. It depends on `ginode`, `ckinode`, `allocino`, `freeino`, `allocblk`, `freeblk`, `getdatablk`, `inodirty`, `dofix`, and diagnostic helpers from sibling files. The code conditionally uses old HP-UX directory headers and Sun UFS headers.

## Risks And Test Signals
Risks include legacy K&R prototypes, fixed `BUFSIZ` path handling, direct mutation of global traversal state, platform-specific directory layouts, and directory expansion that only supports direct blocks before the last direct slot. Test signals include corrupt `d_reclen` repair, missing or bad `.`/`..`, out-of-range entries, duplicate directory links, lost+found creation/reallocation, orphan reconnection, and full lost+found expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/dirutils.c -->
# sources/distributed-fs/openafs/src/vfsck/dirutils.c

## Purpose
Provides a small OpenAFS partition utility used by `vfsck` to canonicalize a filesystem argument into the corresponding device node when the caller passes a mount point or regular path.

## Important APIs, Types, And Functions
The single exported function is `EnsureDevice(char *abuffer)`. It uses `stat`, `opendir`, `readdir`, and `closedir`, plus OpenAFS constants from `afs/partition.h` such as `AFS_DSKDEV`.

## Control Flow
`EnsureDevice` first stats the input path. If it is already a block or character device, it returns success. Otherwise it records the path’s `st_dev`, scans `AFS_DSKDEV` for block devices, and replaces `abuffer` with the first device whose `st_rdev` matches the original `st_dev`. Failure to stat the input or find a matching block device returns nonzero.

## State And Persistence
The function mutates the caller-supplied buffer in place. It does not write to disk or maintain process-global state.

## Dependencies And Integration Points
`main.c` calls this before `setup` so a mount point or file path can be converted into the raw device checked by fsck. It depends on the local `/dev` naming convention encoded by `AFS_DSKDEV` and assumes the caller’s buffer is large enough for the replacement path.

## Risks And Test Signals
Risks include unchecked `strcpy`/`strcat` into 128-byte buffers, no explicit handling when `opendir` fails, and use of `short dev` for `st_dev`. Tests should cover existing block/char devices, mount points backed by a matching `/dev` entry, missing `/dev`, long device names, and no matching block device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/dirutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/fsck.h -->
# sources/distributed-fs/openafs/src/vfsck/fsck.h

## Purpose
Central shared header for the OpenAFS UFS/HFS fsck implementation. It defines inode state values, traversal descriptors, buffer-cache structures, duplicate-block and zero-link lists, repair flags, global process state, and platform-specific filesystem compatibility macros.

## Important APIs, Types, And Functions
Important types are `struct bufarea`, `struct inodesc`, `struct dups`, and `struct zlncnt`. Key constants include inode states `USTATE`, `FSTATE`, `DSTATE`, `DFOUND`, `DCLEAR`, `FCLEAR`, OpenAFS `VSTATE`, HP-UX ACL states `CSTATE` and `CRSTATE`, descriptor types `DATA`/`ADDR`, callback return bits `STOP`, `SKIP`, `KEEPON`, `ALTERED`, and `FOUND`, plus `MAXDUP`, `MAXBAD`, and `MAXBUFSPACE`. It declares shared functions such as `getdatablk`, `getblk`, `ginode`, `allocino`, `findino`, `setup`, `bread`, and `bwrite`.

## Control Flow
The header does not execute control flow itself, but it defines the callback contract used throughout the fsck passes. `ckinode` walks an inode and invokes an `inodesc.id_func`; callbacks return bitmasks to stop, continue, skip, or mark data altered. Macros such as `dirty`, `sbdirty`, `cgdirty`, and `zapino` centralize how files mark buffered filesystem structures for later flush.

## State And Persistence
Most global state is declared here: device names, file descriptors, flags (`preen`, `nflag`, `yflag`, `debug`, `cvtflag`, `fflag`, `mflag`), superblock/cylinder group buffers, block and inode maps, link count table, path buffers, lost+found inode, file/block counters, AFS Vice file counters, Sun clean-state tracking, and HP-UX continuation inode counters. These globals drive all persistent disk modifications made by the passes.

## Dependencies And Integration Points
Every `vfsck` C file includes this header after platform filesystem headers. It bridges OpenAFS Vice inode recognition (`VICEINODE`, `OLDVICEINODE`) with host UFS/HFS structures and exposes platform-specific compatibility shims for Sun and HP-UX.

## Risks And Test Signals
Risks are broad global mutable state, platform macro drift, duplicate global definitions across translation units, K&R-era declarations that hide type mismatches, and subtle differences in `zapino` behavior for Vice versus non-Vice builds. Compile coverage across supported platforms and full fsck pass tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/fsck.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/inode.c -->
# sources/distributed-fs/openafs/src/vfsck/inode.c

## Purpose
Provides inode block traversal, inode caching, inode clearing, block range validation, pathname lookup callbacks, diagnostics, and inode allocation/free helpers for the fsck passes.

## Important APIs, Types, And Functions
Important functions are `ckinode`, `iblock`, `chkrange`, `ginode`, `inodirty`, `clri`, `findname`, `findino`, `pinode`, `blkerror`, `allocino`, and `freeino`. `pbp` caches the current inode block. The code uses OpenAFS inode magic helpers from `afs/osi_inode.h` and global maps from `fsck.h`.

## Control Flow
`ckinode` walks direct and indirect block pointers for an inode, skipping special device files and HP-UX fast symlinks, and delegates each data or address range to either `dirscan`, `iblock`, or the supplied callback. `iblock` recursively processes single, double, and triple indirect blocks, truncating pointers beyond file size when pass 1 is checking addresses. `chkrange` rejects block ranges outside filesystem and cylinder-group data bounds. `ginode` loads and caches the block containing a requested inode.

Clearing and allocation helpers are pass-aware. `clri` prompts or preens before clearing a bad inode and its blocks, preserving HP-UX continuation inode cleanup. `blkerror` marks files or directories for clearing after bad or duplicate blocks. `allocino` finds a free inode, allocates an initial block, initializes times, size, and mode, and updates maps. `freeino` releases blocks through `pass4check`, zaps the inode, and updates counters.

## State And Persistence
The file updates cached inode blocks, block maps, link maps, inode state maps, file/block counters, duplicate/bad state, and dirty flags. Durable effects include cleared inodes, adjusted block pointers, newly allocated inodes, and freed blocks written later by `ckfini`.

## Dependencies And Integration Points
It is central to passes 1, 1b, 2, 3, and 4. `dir.c` depends on `ginode`, `allocino`, `freeino`, and `inodirty`; pass callbacks depend on `ckinode` traversal semantics. Platform branches handle Sun large offsets, HP-UX ACL continuation inodes, fast symlinks, and user-name printing.

## Risks And Test Signals
Risks include integer overflow in size-to-block calculations on older platforms, recursive indirect traversal errors, in-place partial truncation of indirect blocks, global inode-block cache invalidation, and K&R prototypes. Tests should cover direct and indirect block traversal, bad block marking, duplicate block marking, partial truncation, HP-UX fast symlink sizes, continuation inode clearing, allocation failure, and owner/mode diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/libfs.h -->
# sources/distributed-fs/openafs/src/vfsck/libfs.h

## Purpose
Defines return codes for HP-UX block-seek support used by the special `AFS_HPUX101_ENV` I/O path in `utilities.c`.

## Important APIs, Types, And Functions
The header includes `<sys/fs.h>` for UFS macros and defines `BLKSEEK_PROCESSING_ERROR`, `BLKSEEK_FILE_WRITEONLY`, `BLKSEEK_NOT_ENABLED`, and `BLKSEEK_ENABLED`.

## Control Flow
There is no runtime control flow. The constants classify `setup_block_seek_2` outcomes so `bread` and `bwrite` know whether `lseek` offsets are in DEV_BSIZE blocks or byte offsets.

## State And Persistence
No state is stored here. The constants influence persistent disk I/O behavior indirectly through global `seek_options`.

## Dependencies And Integration Points
`utilities.c` includes this file only under HP-UX 10.1-style builds. It ties OpenAFS fsck to the HP-UX `O_BLKSEEK` device flag.

## Risks And Test Signals
Risk is limited to mismatched constant meanings with `utilities.c`. Test by verifying HP-UX device and regular-file fsck reads/writes seek to the expected offsets, including write-only device descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/libfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/main.c -->
# sources/distributed-fs/openafs/src/vfsck/main.c

## Purpose
Top-level driver for the OpenAFS-modified UFS/HFS fsck. It parses command-line options, selects filesystems from arguments or fstab/vfstab, schedules parallel preen checks by disk, invokes setup and passes 1 through 5, reports summaries, updates clean state, and triggers AFS salvager recovery when repaired partitions contain Vice inodes.

## Important APIs, Types, And Functions
The main entry points are `main`, `finddisk`, `addpart`, `startdisk`, `checkfilesys`, `blockcheck`, platform-specific `check_sanity`, `numbers`, `unrawname`, and `rawname`. Internal scheduling types are `struct disk` and `struct part`. Important globals include `tryForce`, `returntosingle`, `nrun`, `ndisks`, `maxrun`, `wflag`, HP-UX `ge_danger`/`fixed`, and Sun `exitstat`.

## Control Flow
`main` syncs disks, parses legacy BSD, Sun, and HP-UX options, installs signal handlers, and either checks explicitly named devices or walks filesystem tables. In preen mode it groups partitions by disk, forks workers up to `maxrun`, collects exit statuses, and reports unexpected inconsistencies. `checkfilesys` canonicalizes the device with `EnsureDevice`, calls `setup`, optionally performs sanity-only mode, then runs `pass1`, optional `pass1b`, `pass2`, `pass3`, `pass4`, and `pass5`. It prints summary statistics and updates clean-state flags.

After a modification, `checkfilesys` closes device descriptors and, if Vice inodes were found or `/TRYFORCE` exists, temporarily mounts the block device on `/etc/vfsck.<device>` or the parent mount point fallback, creates `FORCESALVAGE`, unmounts it, and removes the temporary directory. This is the OpenAFS integration point that forces a full fileserver salvager pass after low-level repairs.

## State And Persistence
The driver coordinates all persistent filesystem changes made by the pass files. It also changes superblock clean state, may create and remove temporary mount directories under `/etc`, and may create a durable `FORCESALVAGE` marker in a repaired AFS partition. Process state includes fstab-derived queues, child process IDs, global flags, and per-check maps freed after each filesystem.

## Dependencies And Integration Points
It depends on HP-UX/Sun/BSD filesystem tables, mount APIs, device naming conventions, generated `AFS_component_version_number.c`, `EnsureDevice`, `setup`, pass functions, buffer finalization, and logging through `vfscklogprintf`. The `FORCESALVAGE` marker integrates this UFS-level checker with the OpenAFS volume salvager and fileserver startup behavior.

## Risks And Test Signals
Risks include destructive operation on mounted/root/swap devices when force flags are misused, legacy option parsing, possible compile hazards in disabled/conditional branches, hard-coded `/etc/vfsck.*`, temporary mounting during boot, and close ordering around `ckfini`. Tests should cover explicit-device checks, fstab preen scheduling, `-n/-y/-p/-P/-m/-F` combinations, dirty Vice partition salvage marker creation, clean filesystem early exits, root filesystem modified exits, and failed temporary mount handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/mount -->
# sources/distributed-fs/openafs/src/vfsck/mount

## Purpose
Filesystem-type wrapper installed as `/sbin/fs/afs/mount` for HP-UX mountall integration. It strips the generic `-Fafs` selector and delegates the real mount operation to the HFS mount implementation.

## Important APIs, Types, And Functions
There are no functions; the script executes `/sbin/fs/hfs/mount $2 $3 $4 $5 $6 $7 $8 $9` and exits with that command’s status.

## Control Flow
The generic mount framework calls this script with the filesystem type as `$1`. The script ignores `$1`, forwards up to eight remaining positional arguments to HFS mount, and exits with the delegated status.

## State And Persistence
All persistent effects are produced by `/sbin/fs/hfs/mount`, which mounts the underlying server partition. The wrapper stores no state.

## Dependencies And Integration Points
This relies on AFS server partitions being HFS-compatible on the target HP-UX platform, while the boot framework refers to them as type `afs`.

## Risks And Test Signals
Risks include loss of arguments beyond `$9`, word-splitting of arguments with spaces, and hard-coded HFS path. Tests should verify mountall invocation with typical AFS fstab records and failure propagation from HFS mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/mount -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass1.c -->
# sources/distributed-fs/openafs/src/vfsck/pass1.c

## Purpose
Implements fsck pass 1: scan all inodes, classify inode state, validate block and size consistency, build the used-block bitmap, record duplicate and bad blocks, initialize link-count tracking, and identify OpenAFS Vice inodes.

## Important APIs, Types, And Functions
Main functions are `pass1` and `pass1check`. Static counters `badblk`, `dupblk`, and `oldreported` limit diagnostics. The pass uses `ginode`, `ckinode`, `ftypeok`, `blkerror`, `setbmap`, `testbmap`, `inodirty`, `zapino`, and OpenAFS macros `VICEINODE`/`OLDVICEINODE`.

## Control Flow
`pass1` first marks filesystem-reserved metadata blocks as used. It then loops over every inode in every cylinder group. Unallocated but partially nonzero inodes can be cleared. Allocated inodes are checked for valid size, platform-specific FIFO and fast-symlink consistency, stray direct and indirect block pointers past EOF, valid file type, and link count. Zero-link inodes are queued, Vice inodes are classified as `VSTATE`, and normal directories/files become `DSTATE` or `FSTATE`. The inode’s blocks are then traversed by `ckinode` using `pass1check`.

`pass1check` validates each fragment range, records bad blocks, detects duplicates against `blockmap`, appends duplicate block records to `duplist`, advances `muldup` for unique duplicate blocks, increments used-block counts, and stops after excessive bad or duplicate blocks.

## State And Persistence
Pass 1 populates `blockmap`, `statemap`, `lncntp`, `zlnhead`, `duplist`, `muldup`, `lastino`, `n_files`, `n_blks`, and `nViceFiles`. It may clear or rewrite inodes, fix FIFO counters, fix fast symlink size, clear Solaris migration flags, and correct block counts.

## Dependencies And Integration Points
Later passes rely on pass 1’s state maps and duplicate lists. Pass 1 depends on inode traversal from `inode.c`, global filesystem geometry from `setup.c`, and platform inode formats from Sun/HP-UX headers. Vice inode classification affects directory validation and salvage forcing later in `main.c`.

## Risks And Test Signals
Risks include false positives from platform inode-layout differences, duplicate list exhaustion, offset overflows, and automatic clearing of unknown file types. Tests should cover sparse files, indirect blocks beyond EOF, duplicate blocks, bad block ranges, zero-link files, Vice inode detection, old Solaris Vice inode detection, HP-UX FIFOs, and fast symlink repair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass1b.c -->
# sources/distributed-fs/openafs/src/vfsck/pass1b.c

## Purpose
Implements pass 1b, a duplicate-block rescan. When pass 1 found duplicate blocks, this pass walks all allocated inodes again to locate the first and additional references so later repair decisions can clear the right owners.

## Important APIs, Types, And Functions
The exported functions are `pass1b` and `pass1bcheck`. It uses static `duphead` as the current duplicate-list cursor and depends on global `duplist`/`muldup`.

## Control Flow
`pass1b` initializes an address descriptor with `pass1bcheck` and scans all non-unallocated inodes with `ckinode`. `pass1bcheck` compares every fragment in the current inode range against the duplicate list. On a match, it reports the duplicate with `blkerror`, swaps the matched block to the duplicate-list head, and advances `duphead`. The pass stops once all unique duplicate entries have been located.

## State And Persistence
This pass mostly mutates duplicate-list ordering and inode state through `blkerror`; it does not directly write blocks. State changes inform pass 4 cleanup.

## Dependencies And Integration Points
It runs only when `duplist` is non-empty after pass 1. It depends on `ckinode`, `chkrange`, and `blkerror`, and its output is consumed by pass 4’s duplicate block release logic.

## Risks And Test Signals
Risks include duplicate-list pointer manipulation, early stop conditions around `muldup`, and skipped HP-UX continuation inode state. Tests should build files sharing the same block and verify all owning inodes are reported before pass 4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass1b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass2.c -->
# sources/distributed-fs/openafs/src/vfsck/pass2.c

## Purpose
Implements fsck pass 2: verify the directory tree starting at the root inode, repair root inode problems, validate `.` and `..`, remove invalid directory entries, decrement link counts for reachable entries, and prevent directories from referencing internal AFS Vice inodes.

## Important APIs, Types, And Functions
Main functions are `pass2` and `pass2check`. It uses `descend`, `allocdir`, `freeino`, `ginode`, `inodirty`, `direrror`, `getpathname`, `lncntp`, and `statemap`.

## Control Flow
`pass2` handles root inode state first: allocate it if missing, reallocate if bad/duplicate, convert file root to directory if requested, then call `descend`. `pass2check` is invoked for each directory entry. It verifies or synthesizes `.` and `..`, removes extra dot entries, builds the current pathname, rejects out-of-range or unallocated targets, resolves `DCLEAR`/`FCLEAR`, descends into unvisited directories, identifies hard links to already found directories, and decrements expected link counts for files and directories. If a directory references a `VSTATE` Vice inode, it can clear the Vice magic and convert it to a regular file.

## State And Persistence
Pass 2 mutates directory entries, root inode mode, inode state transitions, pathname globals, link count expectations, and possibly Vice inode magic. Its directory changes are persisted through buffer dirty flags.

## Dependencies And Integration Points
It is the main consumer of `dir.c` traversal callbacks and relies on pass 1 classification. Pass 3 expects directories not reached by pass 2 to remain `DSTATE`, and pass 4 expects `lncntp` to hold remaining unmatched link counts.

## Risks And Test Signals
Risks include pathname buffer overflow exits, incorrect repair of dot entries when record space is tight, conversion of Vice inodes referenced by directories, and hard-link-to-directory handling. Tests should cover bad root inode states, missing `.`/`..`, extra dot entries, out-of-range inode numbers, duplicate/bad referenced inodes, directory loops, Vice inode directory references, and nested path traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass3.c -->
# sources/distributed-fs/openafs/src/vfsck/pass3.c

## Purpose
Implements fsck pass 3: find directories that were allocated but not connected to the root tree, validate HP-UX continuation inode references, and reconnect orphaned directories through `lost+found`.

## Important APIs, Types, And Functions
The main function is `pass3`. It uses `findino` to walk `..` chains, `linkup` to reconnect orphan directories, `descend` with `pass2check` to revalidate newly connected trees, and HP-UX continuation inode states `HASCINODE`, `CSTATE`, and `CRSTATE`.

## Control Flow
For each inode from root to `lastino`, HP-UX builds validate continuation inode references and mark referenced continuation inodes. For directories still in `DSTATE`, pass 3 follows their `..` chain until it reaches a connected ancestor, an invalid parent, or a loop count bounded by the number of directories. It then calls `linkup` on the orphan. If reconnection succeeds, it descends from `lost+found` into that orphan to apply pass 2 directory checks and link-count updates.

## State And Persistence
Pass 3 changes continuation inode state, directory connectivity state, `lost+found` contents, orphan directory `..` entries, parent link counts, and path globals. Persistent changes are made through `linkup`, `makeentry`, and directory dirty buffers.

## Dependencies And Integration Points
It relies on pass 2 leaving disconnected directories as `DSTATE` and on `dir.c` repair helpers. Pass 4 later clears directories that could not be reconnected and adjusts link counts.

## Risks And Test Signals
Risks include loops in `..` chains, failure to create or expand `lost+found`, continuation inode mismatches on HP-UX, and incorrect parent link-count updates. Tests should include orphan directories, directory cycles, missing `lost+found`, `lost+found` as non-directory, and bad continuation inode numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass4.c -->
# sources/distributed-fs/openafs/src/vfsck/pass4.c

## Purpose
Implements fsck pass 4: reconcile remaining link counts, clear unreferenced files/directories and bad/duplicate inodes, count Vice inodes, and release block-map ownership for cleared inodes.

## Important APIs, Types, And Functions
The main functions are `pass4` and `pass4check`. It uses `adjust`, `clri`, `ckinode`, `lncntp`, `zlnhead`, `duplist`, `n_blks`, and block map macros.

## Control Flow
`pass4` iterates all allocated inode states. Reachable files and found directories have remaining link counts adjusted or are cleared if they were originally zero-link. Unfound directories are cleared as unreferenced. Bad or duplicate files/directories are cleared. Vice inodes are counted but not link-adjusted as regular directory-visible files. HP-UX continuation inodes are either cleared if unreferenced or forced to link count 1 if referenced.

`pass4check` is used while clearing an inode. It walks each block range, removes non-duplicate blocks from `blockmap`, decrements `n_blks`, and consumes duplicate-list entries for blocks still shared.

## State And Persistence
This pass mutates inode contents, link counts, block allocation map, duplicate and zero-link lists, `n_blks`, `n_files`, and `nViceFiles`. Persistent effects are inode clears and link-count corrections.

## Dependencies And Integration Points
It consumes state generated by passes 1 through 3. `freeino` and `clri` rely on `pass4check` for block release. The Vice inode count is used by `main.c` to decide whether to force full salvage after modifications.

## Risks And Test Signals
Risks include incorrect duplicate-list consumption, undercounted block release, clearing reachable objects after earlier state mistakes, and special handling of Vice inodes. Tests should cover zero-link allocated files, bad/duplicate inode clearing, duplicate block ownership resolution, link-count corrections, unreferenced directories, and Vice inode counting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass5.c -->
# sources/distributed-fs/openafs/src/vfsck/pass5.c

## Purpose
Implements fsck pass 5: rebuild and verify cylinder group and superblock allocation summaries from the block and inode maps built by earlier passes.

## Important APIs, Types, And Functions
The main function is `pass5`; `sbfine` clears `fs_fmod` when superblock summary repair occurs. The pass uses `fragacct`, `cg_chkmagic` or `CG_MAGIC`, `cg_inosused`, `cg_blksfree`, `cg_blktot`, `cg_blks`, `blkmap`, and summary structures `struct csum`, `struct cg`, and old/new cylinder group formats.

## Control Flow
Pass 5 initializes a synthetic cylinder-group image, rounds filesystem-size tail fragments as used, then loops over each cylinder group. It reads the current group, rebuilds inode-used maps from `statemap`, rebuilds free block and fragment accounting from `blockmap`, recomputes per-cylinder block totals and fragment summaries, accumulates `fs_cstotal`, and compares each rebuilt component with on-disk values. `dofix` controls whether mismatches update the superblock or cylinder-group buffers. At the end it compares and fixes total free counts in the superblock.

## State And Persistence
The pass writes cylinder group maps, summary counts, rotors, free fragment summaries, superblock `fs_cstotal`, `fs_ronly`, and `fs_fmod` when repairs are accepted. It does not discover new file data; it persists accounting consistency derived from previous passes.

## Dependencies And Integration Points
It depends on accurate `blockmap`/`statemap` from previous passes and UFS fragment helpers in `ufs_subr.c`/`ufs_tables.c`. It handles Sun dynamic postbl formats when `AFS_NEWCG_ENV` is enabled and old format otherwise.

## Risks And Test Signals
Risks include format-specific layout drift, incorrect `mapsize` comparisons, old-to-new conversion behavior, and summary repairs based on earlier corrupted maps. Tests should cover wrong inode maps, wrong free block maps, wrong cylinder group summaries, wrong superblock totals, dynamic versus 4.2 cylinder group formats, and fragment accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/setup.c -->
# sources/distributed-fs/openafs/src/vfsck/setup.c

## Purpose
Prepares a filesystem device for checking. It validates device safety, opens read/write descriptors, reads and verifies the superblock and alternate superblock, handles clean-state early exits and format conversion, reads summary information, allocates fsck maps, and initializes the buffer cache.

## Important APIs, Types, And Functions
Key functions are `setup`, `readsb`, `badsb`, `calcsb`, `is_mounted`, `is_swap`, `is_pre_init`, `is_roroot`, `is_hotroot`, `is_root`, `vfsck_getline`, `freply`, and HP-UX 11 `UpdateAlternateSuper`. Important local structures are `asblk`, `pbp`, and the `CGSIZE` macro for dynamic cylinder group sizing.

## Control Flow
`setup` resets per-run globals, stats and canonicalizes the target, resolves Solaris directory mount points through vfstab, checks mounted/root/swap safety unless `-n` or force modes apply, opens the device read-only and optionally write-only, allocates superblock buffers, and calls `readsb`. If the primary superblock is bad and no alternate was specified, it may search alternate superblocks. It validates optimization and minfree fields, honors HP-UX preen-clean early exits, can convert old/new Sun cylinder-group formats, flushes an alternate superblock when needed, reads summary info, optionally skips clean Sun filesystems in preen mode, allocates `blockmap`, `statemap`, and `lncntp`, then calls `bufinit`.

`readsb` reads the selected superblock, validates magic and geometry, computes `dev_bsize`, reads the first alternate superblock, copies dynamic fields into it, and compares static fields. Helper functions identify mounted, root, read-only root, and swap devices to protect live filesystems.

## State And Persistence
Setup initializes or mutates global device descriptors, `hotroot`, `mountedfs`, `havesb`, `dev_bsize`, superblock buffers, summary pointers, clean/conversion flags, and allocation maps. It may persist repaired superblock fields or converted format metadata before the main passes.

## Dependencies And Integration Points
It is called by `checkfilesys` before any pass. It depends on platform mount tables, `ustat`, HP-UX `pstat`, Sun vfstab/mnttab APIs, UFS headers, `bread`/`bwrite` from `utilities.c`, and `bufinit`. Its clean-state decisions affect whether main returns without running passes.

## Risks And Test Signals
Risks include device safety false negatives, alternate superblock comparison drift, hard-coded platform assumptions, memory allocation failures on huge filesystems, and writes during format conversion. Tests should cover bad primary superblock with alternate recovery, clean preen early exit, mounted/root/swap prompts, read-only/no-write mode, summary read failures, Sun format conversion, HP-UX clean-state returns, and map allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/ufs_subr.c -->
# sources/distributed-fs/openafs/src/vfsck/ufs_subr.c

## Purpose
Provides user-space copies of UFS fragment and block bitmap helper routines needed by pass 5 and allocation logic.

## Important APIs, Types, And Functions
Functions are `fragacct`, `isblock`, `clrblock`, `setblock`, `scanc`, `skpc`, and `locc`. It uses tables `around`, `inside`, and `fragtbl` declared in `ufs_tables.c`.

## Control Flow
`fragacct` decodes a free-fragment bit pattern and increments or decrements fragment summary counts for each fragment size. `isblock`, `clrblock`, and `setblock` specialize bitmap operations for filesystems with 1, 2, 4, or 8 fragments per block. `scanc`, `skpc`, and `locc` are C implementations of legacy byte-scanning helpers.

## State And Persistence
The functions mutate caller-supplied cylinder group maps and fragment summary arrays. They do not maintain global state beyond reading the static tables.

## Dependencies And Integration Points
Pass 5 uses `fragacct` while rebuilding free fragment summaries. Filesystem allocation helpers can use `isblock`/`setblock`/`clrblock` semantics. The routines depend on UFS `struct fs` geometry and `panic` from `utilities.c` for impossible fragment sizes.

## Risks And Test Signals
Risks include unsupported `fs_frag` values, signedness assumptions in bitmap indexing, and table mismatch with UFS layout. Tests should verify fragment accounting for fragment sizes 1, 2, 4, and 8 and ensure pass 5 summary output matches known-good UFS images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/ufs_subr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/ufs_tables.c -->
# sources/distributed-fs/openafs/src/vfsck/ufs_tables.c

## Purpose
Defines static lookup tables used by UFS fragment accounting and allocation bitmap scans.

## Important APIs, Types, And Functions
Exports `around[9]`, `inside[9]`, `fragtbl124[256]`, `fragtbl8[256]`, and `fragtbl[MAXFRAG + 1]`. There are no functions.

## Control Flow
No runtime control flow is present. `fragacct` indexes these tables to determine which fragment sizes are available in a byte-sized free-fragment map.

## State And Persistence
All state is static read-only table data. It influences how pass 5 rebuilds on-disk fragment summaries but does not itself write.

## Dependencies And Integration Points
`ufs_subr.c` imports these arrays. The tables are inherited from BSD UFS code and must match filesystem bit ordering for supported fragment counts.

## Risks And Test Signals
Risks are accidental table corruption, wrong `MAXFRAG` assumptions, or platform `u_char` differences. Test signals are pass 5 fragment summary consistency across filesystem fragment sizes and allocation bitmap unit tests comparing table-driven results to brute-force fragment scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/ufs_tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/umount -->
# sources/distributed-fs/openafs/src/vfsck/umount

## Purpose
Filesystem-type unmount wrapper installed as `/sbin/fs/afs/umount`. It represents AFS as not dynamically unmountable in this HP-UX integration path.

## Important APIs, Types, And Functions
There are no functions or external command calls. The script exits with status 1.

## Control Flow
When generic `umountall` invokes the script for `AFS /afs`, it performs no operation and immediately exits 1. The comments state reboot is the only supported way to unmount AFS.

## State And Persistence
No state is changed. The mounted AFS client filesystem remains mounted.

## Dependencies And Integration Points
This integrates with HP-UX `umountall` as the filesystem-specific handler for AFS. It intentionally does not call HFS unmount or detach the AFS client.

## Risks And Test Signals
Risks include callers treating exit 1 as an unexpected failure during shutdown and the spelling/comment drift indicating this path may be obsolete. Test signals are shutdown scripts tolerating this status and verifying no accidental unmount attempt occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/umount -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/utilities.c -->
# sources/distributed-fs/openafs/src/vfsck/utilities.c

## Purpose
Provides shared fsck utility behavior: file-type validation, user prompting, buffer-cache management, raw disk read/write, block allocation/free, pathname reconstruction, signal handling, fix policy, diagnostics, clean-state updates, mount/writable checks, and HP-UX block-seek support.

## Important APIs, Types, And Functions
Important functions include `ftypeok`, `reply`, `bufinit`, `getdatablk`, `getblk`, `flush`, `rwerror`, `ckfini`, `bread`, `bwrite`, `allocblk`, `freeblk`, `getpathname`, `catch`, `catchquit`, `voidquit`, `dofix`, `errexit`, `pfatal`, `pwarn`, `pinfo`, `panic`, Sun helpers `debugclean`, `updateclean`, `printclean`, `hasvfsopt`, `writable`, `mounted`, and HP-UX helpers `setup_block_seek`, `setup_block_seek_2`, and `setup_all_block_seek`.

## Control Flow
The buffer cache is an LRU list of `bufarea` objects. `getdatablk` finds or loads a block, moves it to the front, and marks it in use. `getblk` flushes a reusable buffer before reading another disk block. `flush` writes dirty buffers and, for the superblock, also writes summary information. `ckfini` flushes all cached buffers, optionally updates the standard superblock when an alternate was used, frees buffers, and closes descriptors.

`reply` centralizes interactive policy for `-n`, `-y`, preen, no-write, and HP-UX fixed-state tracking. `dofix` decides whether a detected corruption should be salvaged now and caches that decision in `inodesc.id_fix`. `bread` and `bwrite` implement raw block I/O with fallback sector-by-sector diagnostics. Sun clean-state helpers update `fs_clean`/`fs_state` consistently. HP-UX 10.1 code can enable `O_BLKSEEK` and switch seek units for block devices.

## State And Persistence
This file mutates the dirty buffer cache, `fsmodified`, clean-state fields, block maps, counters, signal-driven exit state, and HP-UX `seek_options`. Persistent writes happen through `bwrite`, `flush`, `ckfini`, and `updateclean`.

## Dependencies And Integration Points
All pass files depend on these helpers for prompting, diagnostics, block I/O, and buffer lifecycle. `setup.c` calls `bufinit` and may use `writable`/`mounted`; `main.c` relies on `ckfini` and signal handlers. The HP-UX path depends on `libfs.h` and `O_BLKSEEK`.

## Risks And Test Signals
Risks include old unbounded varargs declarations, fixed-size buffers, no-write mode silently suppressing writes after prompts, sector fallback behavior on partial I/O, possible resource leaks in early `updateclean` returns, and platform-specific seek semantics. Tests should cover `-n/-y` prompt policy, dirty buffer flush, alternate superblock update, read/write error fallback, block allocation/free, pathname reconstruction, SIGINT/SIGQUIT handling, Sun clean-state transitions, mounted/writable detection, and HP-UX block-seek mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/utilities.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/vprintf.c -->
# sources/distributed-fs/openafs/src/vfsck/vprintf.c

## Purpose
Adds OpenAFS-specific mirrored logging for fsck messages. It prints messages to stdout and, when configured, duplicates them into the vfsck log file for non-root AFS server partitions.

## Important APIs, Types, And Functions
The single function is `vfscklogprintf(char *s, long a1, ... long a10)`. It uses global `logfile` declared in `fsck.h` and standard `printf`, `fprintf`, and `fflush`.

## Control Flow
Each call prints the format string and up to ten K&R-style long arguments to stdout. If `logfile` is non-null, it writes the same formatted message to that file and flushes it immediately.

## State And Persistence
The function does not open or close the log; it writes to the already-open `logfile`. Persistent state is the appended log content, and stdout output is immediate process I/O.

## Dependencies And Integration Points
Several files define `msgprintf` as `vfscklogprintf` when `VICE` is enabled. `main.c` later fsyncs and closes `logfile` after modifications. The function depends on all callers matching its fixed ten-argument varargs convention.

## Risks And Test Signals
Risks include format/argument mismatches, truncation of non-`long` varargs on some ABIs, and logging being skipped when `logfile` setup is absent. Tests should verify mirrored output for normal, preen, and error messages and build on 32-bit/64-bit targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/vprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/Makefile.in -->
# sources/distributed-fs/openafs/src/viced/Makefile.in

## Purpose
Builds the OpenAFS fileserver and related diagnostic utilities from `src/viced`, while pulling in directory, volume, fsint, synchronization, crypto, Rx, and utility libraries.

## Important APIs, Types, And Functions
Important targets are `all`, `${TOP_INCDIR}/afs/fs_stats.h`, `check_sysid`, `fsprobe`, `cbd`, `fileserver`, `install`, `dest`, and `clean`. Object groups are `VICEDOBJS`, `DIROBJS`, `VOLOBJS`, `FSINTOBJS`, and aggregate `objects`. `MODULE_CFLAGS` enables `RXDEBUG`, `FSSYNC_BUILD_SERVER`, and `SALVSYNC_BUILD_CLIENT`.

## Control Flow
The makefile includes configured build rules and pthread settings, defines source directories for `../dir` and `../vol`, compiles local files plus selected directory and volume sources into local objects, generates/uses `AFS_component_version_number.c`, links helper tools (`check_sysid`, `fsprobe`, `cbd`), links the static `fileserver`, and installs it under server libexec/sbin or dest tree paths. The clean target removes libtool artifacts, objects, generated version file, tools, and `fileserver`.

## State And Persistence
Build outputs include object files, `fileserver`, `cbd`, `check_sysid`, `fsprobe`, generated component version source, and installed binaries/headers. The makefile does not manage runtime fileserver state.

## Dependencies And Integration Points
It integrates `viced` with `src/dir`, `src/vol`, `src/fsint`, VLDB, RxKAD, RxStat, LWP compatibility, ACL, cmd, opr, util, hcrypto, roken, pthread, and platform linker exports for AIX. It installs `fs_stats.h` into the top include directory for consumers.

## Risks And Test Signals
Risks include object list drift when source files change, mismatched compile flags for shared volume/dir sources, static link order sensitivity, generated version-file dependencies, and platform-specific linker flags. Test signals are clean rebuilds, `make install DESTDIR=...`, AIX link coverage, helper tool execution, and fileserver startup against fssync/salvsync-enabled volume code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/Makefile.in -->
