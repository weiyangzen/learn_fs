# Group Research: group_366_freebsd_src_sources_os_bsd_freebsd_src_sbin_fsck_preen_c_sources_os__3ed389a5637f

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck/preen.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck/preen.c

This file implements `checkfstab()`, the generic `/etc/fstab` traversal and preen-mode scheduling helper used by filesystem checkers. It is not UFS-specific; it receives callbacks that decide whether an fstab entry should be checked and how to launch the concrete checker.

Key behavior:
- Iterates fstab entries by increasing `fs_passno`, using `setfsent()` / `getfsent()`.
- In non-preen mode, pass 1, or background mode, checks filesystems serially through `checkit`.
- In preen mode for later passes, groups partitions by disk and runs checks for different disks in parallel while serializing partitions on the same disk.
- Tracks failed partitions in `badh` and prints the final “unexpected inconsistency” summary.
- Honors the fstab `failok` option by ignoring a checker error for that filesystem.
- Uses `finddisk()` to derive a disk base name by trimming after the unit-number portion, then queues partitions under that disk.

Important interactions:
- `docheck(struct fstab *)` filters entries.
- `checkit(type, dev, mountpoint, auxarg, pidp)` either runs synchronously or starts a child and returns its pid through `pidp`.
- Uses `wait()` to collect parallel checker children and starts the next partition on a disk after the previous one finishes.

Edge cases:
- Duplicate fstab devices are warned and skipped per disk queue.
- Unknown child pids are ignored with a warning.
- Signal exits force an error return.
- `name == NULL` is fatal in preen paths but skipped in manual mode.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck/preen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/Makefile

This is the FreeBSD build definition for the UFS/FFS filesystem checker.

Key behavior:
- Builds program `fsck_ffs` in package `ufs`.
- Installs hard links or command aliases for `fsck_ufs` and `fsck_4.2bsd`.
- Installs `fsck_ffs.8` with manpage links for the aliases.
- Builds the checker from directory, inode, pass, setup, soft-updates journal, gjournal, utility, and globals source files.
- Links against `libufs` and `libutil`.
- Adds the current directory to include search path and imports FFS kernel path sources through `.PATH: ${SRCTOP}/sys/ufs/ffs`.

Important interactions:
- The listed `SRCS` include files outside this research group, notably `suj.c` and `utilities.c`, which provide soft updates journal recovery and block device name handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/dir.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/dir.c

This file contains directory-tree repair machinery: directory entry scanning, validation, link-count adjustment, lost+found reconnection, directory allocation, and directory expansion.

Key behavior:
- `propagate()` marks directories reachable from root as `DFOUND`.
- `check_dirdepth()` verifies and repairs UFS directory depth metadata, either by directly editing inodes or by background-fsck sysctl adjustment.
- `dirscan()` walks directory entries for a directory inode and applies an `inodesc` callback.
- `fsck_readdir()` validates current and next entries, can zero corrupt directory-block remainder, and can coalesce a bad following entry into the current record.
- `dircheck()` validates `d_reclen`, `d_namlen`, type range, name termination, slash/NUL rules, and optionally clears unused directory padding with `-z`.
- `adjust()` fixes inode link counts, clears soft-update orphan files, or reconnects unreferenced objects.
- `linkup()` reconnects orphan files/directories into `lost+found`, creating or reallocating `lost+found` when necessary.
- `changeino()` and `makeentry()` mutate or create directory entries.
- `expanddir()` allocates more directory space, including direct or single-indirect growth, and initializes empty directory records.
- `allocdir()` creates a directory inode with `.` and `..`, updates parent link counts, caches inode info, and records directory depth.
- `freedirino()` and `freeino()` unwind failed directory creation.
- `lftempname()` generates lost+found names like `#<ino>`.

Important interactions:
- Relies heavily on `ckinode()` from `inode.c` for walking directory blocks.
- Uses `inoinfo()` / `getinoinfo()` state from pass 1.
- Uses `sysctl` operations in background mode for live filesystem updates.
- Calls `allocino()`, `allocblk()`, `freeblock()`, `ginode()`, `inodirty()`, and `cgdirty()` for persistent metadata repair.

Edge cases:
- Directories with wrong depth can be silently left unresolved in no-write/read-only mode because clean state does not depend on depth.
- Orphans inside snapshots cannot be linked up.
- Directory expansion is deliberately limited to direct blocks plus one single-indirect block.
- Broken `lost+found` can be replaced, with old inode reference accounting repaired.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/ea.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/ea.c

This file is intended to scan UFS2 external attribute blocks, but the actual scanner is compiled out.

Key behavior:
- `eascan(struct inodesc *, struct ufs2_dinode *)` currently returns `0` immediately.
- Disabled code would print external attribute block contents by reading `di_extb[0]` with `getdatablk()` and dumping bytes.

Important interactions:
- Called by pass 1 for UFS2 inodes with external attributes.
- Because the active implementation is a stub, this checker currently does not validate or repair EA payload structure here.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/ea.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/fsck.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/fsck.h

This is the central internal header for `fsck_ffs`. It defines shared data structures, global checker state, repair state constants, buffer cache metadata, inode state tracking, and function prototypes.

Key definitions:
- `DIP()` and `DIP_SET()` abstract UFS1 vs UFS2 dinode fields.
- `struct inostat` records inode state, type, descriptor type, and remaining link count.
- Inode states include `USTATE`, `FSTATE`, `FZLINK`, `DSTATE`, `DZLINK`, `DFOUND`, `DCLEAR`, and `FCLEAR`.
- `struct bufarea` represents cached filesystem blocks, with block number, size, errors, dirty flag, type, refcount, index, and typed union accessors.
- Buffer types distinguish superblock, cylinder group, indirect levels, external attributes, inode blocks, directory data, and user data.
- `struct inodesc` is the generic traversal descriptor used by inode and directory scanners.
- `struct dups` stores duplicate block lists.
- `struct inoinfo` caches directory parentage, `..`, depth, flags, size, and direct/indirect block addresses.

Global state:
- Device and mode flags: `cdevname`, `preen`, `nflag`, `yflag`, `bkgrdflag`, `ckclean`, `skipclean`, `surrender`, `wantrestart`.
- Filesystem descriptors and metadata: `fsreadfd`, `fswritefd`, `sblk`, `sblock`, `blockmap`, `maxino`, `maxfsblock`.
- Repair accounting: `n_blks`, `n_files`, `duplist`, `muldup`, `inostathead`, `inphash`, `inpsort`.
- Background fsck sysctl MIBs for link counts, block counts, sizes, maps, and summaries.
- Snapshot state: `snapcnt`, `snaplist`, `cursnapshot`, `copybuf`.

Important interactions:
- Provides prototypes for all phase functions, setup, inode traversal, directory repair, buffer I/O, snapshot COW, gjournal and SUJ entry points.
- Inline `Malloc`, `Balloc`, and `Calloc` retry after flushing cylinder-group cache entries.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/fsck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/fsutil.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/fsutil.c

This file provides the checker’s utility layer: prompt handling, inode-state lookup, buffer cache, block I/O, cylinder group validation/rebuild helpers, allocation helpers, final cleanup, I/O stats, and fatal/warning output.

Key behavior:
- `fsutilinit()` resets per-run I/O and slow-I/O counters.
- `ftypeok()` validates legal UFS inode file types.
- `reply()` implements interactive yes/no policy, including `-n`, `-y`, read-only, and preen restrictions.
- `inoinfo()` returns per-inode state from cylinder-group-indexed `inostathead`.
- `bufinit()`, `getdatablk()`, `getblk()`, `brelse()`, `binval()`, and `flush()` implement a typed LRU buffer cache.
- `cglookup()`, `cgdirty()`, and `flushentry()` manage cached cylinder group blocks and hashes.
- `flush()` handles type-specific writeback: superblocks through `sbput`, cylinder groups through `cgput`, inode hash repair, snapshot copy-on-write, and raw block writes.
- `snapflush()` forces pending snapshot copies before cylinder-group rebuilds.
- `cg_write()` recomputes SUJ cylinder-group fragment/cluster summaries before writing.
- `rwerror()`, `pfatal()`, `pwarn()`, and `panic()` centralize error policy.
- `ckfini()` performs final writeback, clean/dirty marking, resource cleanup, and descriptor close.
- `blread()`, `blwrite()`, `blerase()`, and `blzero()` implement raw device I/O and optional delete/zero of free space.
- `check_cgmagic()` validates cylinder group magic, index, sizes, offsets, initialized inode counts, and CRC when enabled.
- `rebuild_cg()` reconstructs a cylinder group header so later passes can rebuild maps.
- `allocblk()` and `std_checkblkavail()` allocate free fragments, updating block maps and cylinder group summaries.
- `chkfilesize()` enforces UFS1/UFS2/kernel maximum file size and `MAXDIRSIZE`.
- `slowio_start()` / `slowio_end()` throttle background fsck I/O.
- `getpathname()` reconstructs a path by walking `..` and parent directories.
- `dofix()` encapsulates salvage/fix decision state for an `inodesc`.

Important invariants:
- `ckfini()` flushes in a strict order: cylinder groups, indirect/directory/EA/data blocks, inode blocks, then superblock. This preserves metadata reachability during partial truncation repair.
- SUJ recovery avoids recycling dirty buffers when doing so would force premature writes.
- Dirty writes in read-only mode are treated as internal fatal errors.
- Background mode uses sysctls for live metadata adjustment and marks `FS_NEEDSFSCK` when background repair cannot proceed.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/fsutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/gjournal.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/gjournal.c

This file implements the fast cleanup path for GEOM journaled UFS filesystems.

Key behavior:
- `gjournal_check(const char *filesys)` clears unreferenced inodes tracked by `fs_unrefs` and per-cylinder-group `cg_unrefs`.
- If no unreferenced inodes exist, it marks the superblock dirty and finishes clean immediately.
- Iterates cylinder groups, validates each with `check_cgmagic()`, and scans allocated inodes from `cg_inosused()`.
- Clears allocated regular files or directories with `di_nlink == 0`.
- Uses `clri()` and `freeblock()` to deallocate contents, clears the inode-used bitmap, decrements unref counters, updates `cg_irotor`, zeroes the dinode, and dirties inode/cylinder-group/superblock metadata.
- On cylinder group corruption, requests rerun and exits without marking clean.

Important interactions:
- Called from `main.c` when `FS_GJOURNAL` is set and a full fsck is not required.
- Uses normal fsck buffer, inode, and cylinder-group update routines, then finishes through `ckfini(1)`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/gjournal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/globs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/globs.c

This file defines most global storage declared in `fsck.h` and initializes per-filesystem checker state.

Key behavior:
- Defines read counters/timers, superblock buffer `sblk`, current directory buffer `pdirbp`, directory cache counters, sysctl MIB arrays, global command structure, device/mode flags, block/inode counters, signal flags, duplicate lists, inode state lists, and zero inode `zino`.
- `fsckinit()` resets these globals before checking each filesystem.
- Initializes file descriptors to `-1`, `lfname` to `lost+found`, `lfmode` to `0700`, `resolved`/`havesb`/`fsmodified` state, counters, and zero dinodes.

Important interactions:
- `main.c` calls `fsckinit()` for each target filesystem.
- The globals are shared by all passes, directory repair, inode traversal, setup, and fsutil code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/globs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/inode.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/inode.c

This file implements inode traversal, block reachability lookup, inode cache reads, block/inode freeing, snapshot copy-on-write preservation, directory inode cache management, and inode diagnostic helpers.

Key behavior:
- `ckinode()` walks an inode’s direct and indirect block tree and applies the descriptor callback, or `dirscan()` for directory data.
- `iblock()` recursively walks indirect blocks, detects partially truncated inodes, and clears invalid excess indirect pointers when allowed.
- `ino_blkatoff()` and `indir_blkatoff()` resolve logical block numbers, including negative lbn forms for extattrs and indirect blocks.
- `chkrange()` validates fragment ranges against filesystem size and cylinder group metadata/data boundaries.
- `ginode()` loads a specific inode, using the sequential pass-1 buffer or cached inode block, verifies UFS2 inode hashes, and performs old-format compatibility updates.
- `getnextinode()` is the optimized sequential reader used by pass 1 and pass 1b; it also helps detect valid inode extent during cylinder group rebuild.
- `setinodebuf()` configures sequential inode scanning for a cylinder group.
- `freeblock()` releases blocks, updates duplicate-block tracking, block map, counters, and cylinder group summaries.
- `snapremove()`, `snapclean()`, `snapblkfree()`, `copyonwrite()`, and `chkcopyonwrite()` preserve snapshot semantics when blocks are freed or overwritten.
- `check_blkcnt()` recomputes and repairs inode `di_blocks`.
- `cacheino()`, `getinoinfo()`, `removecachedino()`, and `inocleanup()` maintain directory metadata caches for passes 2 and 3.
- `inodirty()` updates UFS2 inode check hashes before marking inode buffers dirty.
- `clri()` clears an inode and frees its blocks, with special handling for snapshots and background sysctl adjustment.
- `findname()`, `findino()`, and `clearentry()` are directory-scan callbacks.
- `prtinode()` prints owner, mode, size, and mtime.
- `blkerror()` marks inodes for clearing after bad or duplicate block discovery.
- `allocino()` and `freeino()` allocate/deallocate inodes and their initial block.

Important invariants:
- Snapshot blocks must be claimed or copied before a live block is freed/overwritten.
- Direct blocks in snapshots are assumed pre-copied.
- UFS2 inode check hashes are updated on dirtying and repaired on read when accepted.
- `ckinode()` treats embedded symlinks and special devices as not having normal data blocks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/main.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/main.c

This file is the `fsck_ffs` entry point and top-level orchestration layer.

Key behavior:
- Parses flags for alternate superblock, background check, conversion, debug, erase/zero free blocks, force, background feasibility check, lost+found mode, assume no/yes, preen, restart, inode trimming, surrender on reads, and directory-space zeroing.
- Sets signal handlers for interruption, `SIGINFO`, and background progress alarms.
- Raises data-size rlimit to support large filesystems.
- `checkfilesys()` performs one filesystem check from device resolution through final status.
- Handles mounted-filesystem lookup, block-device canonicalization, superblock open/read, and `-F` background feasibility exits.
- Runs fast gjournal cleanup when possible.
- Sets up background snapshot checking through `setup_bkgrdchk()`.
- Runs SUJ recovery when enabled and safe; falls back to full fsck if journal recovery fails or is disallowed.
- Offers to add supported metadata check hashes in manual writable UFS2 mode.
- Executes phases: pass1, optional pass1b, pass2, pass3, pass4, snapflush, pass5.
- Prints final allocation/free summary and duplicate residuals in debug mode.
- Marks clean/dirty through `ckfini()`, requests rerun/restart when needed, and asks mount reload logic via `chkdoreload()`.

Background setup:
- Requires mounted read-write soft-updates filesystem with kernel support.
- Creates `.snap` if necessary, creates `.snap/fsck_snapshot` via `nmount(..., snapshot)`, opens it, unlinks it immediately, rereads the snapshot superblock, and stores the fd handle for sysctl commands.
- Verifies sysctl support for reference count, block count, size, free file/dir/block operations, and optionally summary adjustments.

Important interactions:
- Calls `setup()`, `pass1()` through `pass5()`, `suj_check()`, `gjournal_check()`, and many utility routines.
- Uses exit/status values including `EEXIT`, `ERERUN`, and `ERESTART`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass1.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass1.c

This file implements phase 1: block and inode size validation.

Key behavior:
- Initializes reserved filesystem metadata blocks in `blockmap`.
- Iterates every cylinder group, validates or optionally rebuilds cylinder group headers.
- Determines initialized inode range, with a soft-updates optimization to trim scanning to the highest used inode bitmap bit.
- Allocates `inostathead[c].il_stat` entries for inode state.
- Scans allocated inodes with `getnextinode()` and `checkinode()`.
- Optionally trims UFS2 `cg_initediblk` when `-r` is used.
- Shrinks in-memory inode-state arrays to the actually found inode count when possible.

`checkinode()`:
- Detects partially allocated zero-mode inodes.
- Validates file size, special-file size and rdev, file type, stale direct/indirect pointers beyond file size, and block count.
- Classifies inodes into `USTATE`, `FSTATE`, `FZLINK`, `DSTATE`, `DZLINK`, `DCLEAR`, or `FCLEAR`.
- Caches directories for later passes.
- Scans normal and external-attribute blocks.
- Corrects `di_blocks`.
- Detects file sizes extending beyond the last allocated block and shortens when approved.

`pass1check()`:
- Validates each fragment range.
- Marks bad blocks and duplicate blocks.
- Builds the duplicate list split between unique duplicates and repeated duplicate occurrences.
- Counts allocated blocks and tracks last allocated logical block.
- Enforces `MAXBAD` and `MAXDUP` thresholds.

Important interactions:
- Supplies the authoritative block allocation map used by pass 5.
- Supplies inode state and directory caches used by passes 2 through 4.
- Snapshot descriptors alter handling of `BLK_NOCOPY` and `BLK_SNAP`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass1b.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass1b.c

This file implements phase 1b, the duplicate-block owner rescan.

Key behavior:
- Runs only when pass 1 found duplicate blocks.
- Rescans allocated inodes in cylinder-group order.
- Uses `pass1bcheck()` to compare each referenced fragment against the duplicate list.
- Emits `blkerror(..., "DUP", ...)` for inodes owning duplicate blocks.
- Advances `duphead` until all unique duplicate blocks have been found, then stops and requests rerun.

Important interactions:
- Uses pass-1 inode state, `duplist`, and `muldup`.
- Uses `ckinode()` traversal and the sequential inode buffer.
- Sets `rerun` when duplicate discovery is complete or traversal stops early.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass1b.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass2.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass2.c

This file implements phase 2: pathname and directory structure validation.

Key behavior:
- Ensures the root inode exists and is a directory, reallocating or fixing mode when approved.
- Marks root as `DFOUND` and whiteout inode `UFS_WINO` as a whiteout file state.
- Sorts directory cache entries by first disk block to improve scanning locality.
- Validates every cached directory with `pass2check()`.
- Repairs directory length too short or not a multiple of `DIRBLKSIZ`.
- Builds temporary directory dinodes from cached block lists to scan directory data.
- After scanning entries, verifies and repairs each directory’s `..` against discovered parent.
- Propagates root reachability through the directory tree.

`pass2check()`:
- Checks and repairs `.` entry inode/type.
- Checks, adds, replaces, or defers `..`.
- Removes extra `.` or `..` entries.
- Removes out-of-range or unallocated directory entries.
- Repairs whiteout entries and bad type values.
- Handles entries pointing to `DCLEAR`/`FCLEAR` objects.
- Tracks parent relationships and decrements link counts for observed references.
- Detects and fixes extraneous hard links to directories.

`fix_extraneous()`:
- Determines whether a duplicate directory name or old parent name should be removed based on `..`.
- In snapshot/background paths, uses sysctls plus `unlink`.
- In foreground paths, edits directory entries directly.

Important interactions:
- Consumes directory cache from pass 1 and produces parent/dotdot/depth state for pass 3.
- Updates link-count residuals used by pass 4.
- Uses live sysctl operations when checking snapshots/background filesystems.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass3.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass3.c

This file implements phase 3: directory connectivity repair.

Key behavior:
- Walks cached directories in reverse sorted order.
- Skips root and already-connected directories.
- Leaves unreferenced soft-updates directories for pass 4 clearing when preen/background state is otherwise resolved.
- Follows parent chains to find the top orphan in a disconnected chain.
- Reconnects orphan directories into `lost+found` with `linkup()`.
- Detects orphaned directory loops and offers reconnection.
- For loops, finds the directory name in its parent, links the orphan, clears the old entry, and adjusts link counts.
- Calls `check_dirdepth()` and `propagate()` after reconnecting.

Important interactions:
- Depends on parent/dotdot information collected in pass 2.
- Uses `linkup()` from `dir.c`, `findname()` / `clearentry()` callbacks from `inode.c`, and directory state from `inoinfo()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass4.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass4.c

This file implements phase 4: reference count checking and clearing of unresolved inodes.

Key behavior:
- Iterates all allocated inode-state entries by cylinder group.
- Clears zero-link files/directories when no references remain.
- For valid files and connected directories, calls `adjust()` when residual link count is nonzero.
- Clears disconnected directories left in `DSTATE`.
- Clears `DCLEAR` and `FCLEAR` inodes as zero-length, bad, or duplicate, except when already handled for snapshots.
- Leaves `USTATE` untouched.

Important interactions:
- Uses `freeblock` descriptor callbacks for inode clearing.
- Consumes link-count residuals built by pass 2 and connectivity state built by pass 3.
- Calls `clri()` and `adjust()` from shared repair code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass5.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass5.c

This file implements phase 5: cylinder group and summary reconstruction.

Key behavior:
- Builds a fresh `struct cg` image for each cylinder group from pass-derived inode/block state.
- Handles conversion-level updates for clustering maps.
- Optionally rewrites cylinder groups to add check hashes.
- Recomputes inode-used maps, block-free maps, fragment summaries, cluster maps, and cylinder group summaries.
- Optionally zeroes or deletes unallocated fragments when `-Z` or `-E` is used.
- Compares rebuilt per-cg summaries against superblock summaries and repairs when approved.
- Compares rebuilt cylinder-group headers/maps against on-disk versions and repairs when approved.
- Accumulates total filesystem summary and repairs `fs_cstotal`.
- In background/snapshot mode, adjusts live superblock summaries through sysctl operations instead of writing snapshot metadata.

`update_maps()` and `check_maps()`:
- Compare claimed allocation maps against computed maps.
- Report allocated resources marked free.
- Free resources marked used but determined unallocated, using sysctls in background mode.
- Separates directory and file inode freeing to account for directory count differences.

`clear_blocks()`:
- Performs zeroing through `blzero()` and delete/TRIM through `blerase()` for contiguous free fragment ranges.

Important interactions:
- Relies on `blockmap`, `inostathead`, and counters built by earlier passes.
- Uses `dofix()` to share preen/manual repair policy.
- Must run after `snapflush()` so snapshot COW allocations are reflected before rebuilding maps.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/setup.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/setup.c

This file opens the target filesystem, reads/validates the superblock, allocates core maps, loads snapshot metadata, and handles UFS2 recovery information.

Key behavior:
- `setup()` verifies an already-open read fd and loaded superblock, opens write fd when allowed, handles superblock check-hash correction, skips clean filesystems, validates basic superblock fields, and allocates block/inode/directory caches.
- Rejects very old UFS1 inode formats requiring pre-2002 conversion tooling.
- Offers to save UFS2 recovery data when no recovery information exists.
- Sets `usedsoftdep` from superblock flags.
- Loads valid active snapshot inodes from `fs_snapinum[]`, removing invalid entries from the snapshot list.
- Allocates `copybuf` when snapshots are active.

Snapshot validation:
- `checksnapinfo()` verifies that a snapshot block list contains required copied metadata blocks: superblock, cylinder groups, and summary blocks.
- `getlbnblkno()` finds the data block containing the snapshot block list.

Device/superblock handling:
- `openfilesys()` accepts character/block devices; in background mode also accepts snapshot files and records `cursnapshot`.
- `readsb()` reads an explicit alternate superblock when `-b` is used, otherwise tries standard superblock, then standard with hash failure ignored, then exhaustive alternate search.
- On successful superblock read, copies it into `sblock`, computes `dev_bsize`, records actual superblock location, and updates legacy UFS1 widened fields when needed.
- `sblock_init()` initializes descriptor state and allocates the superblock buffer.

Recovery handling:
- `chkrecovery()` checks whether UFS2 recovery material already exists before the UFS2 superblock area.
- `saverecovery()` writes `struct fsrecovery` data into the last bytes of the boot block region.

Important interactions:
- Provides the initialized `blockmap`, `inostathead`, `inphash`, and `inpsort` required by all passes.
- Snapshot loading is required by `inode.c` copy-on-write code.
- Calls `ckfini(0)` on allocation/setup failure after partial initialization.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/setup.c -->