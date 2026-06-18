# Group Research: group_1365_openbsd_src_sources_os_bsd_openbsd_src_sbin_fsck_ffs_main_c_sources_e65000eab0bd

Subset scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/openbsd-src`, which is included in subset A. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/main.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/main.c

## Scope

Top-level driver and global state owner for OpenBSD `fsck_ffs`. It parses command-line options, initializes signal handling, invokes setup, runs the five FFS check phases, reports summary statistics, writes superblocks if needed, and handles root-filesystem post-repair behavior.

## Main APIs And State

- `main()` handles `-p`, `-b`, `-c`, `-d`, `-f`, `-m`, `-n`, `-y`, initializes `checkroot()`, `catchinfo()`, and dispatches one filesystem through `checkfilesys()`.
- `argtoi()` parses numeric options with strict trailing-character rejection.
- `checkfilesys()` is the main repair sequence.
- Defines central globals shared by `fsck_ffs`: buffer heads, superblock buffers, duplicate-block list, zero-link list, inode state tables, block map, file counters, file descriptors, flags, and lost+found inode.

## Control Flow

`checkfilesys()` calls `setup()`, skips clean filesystems when allowed, initializes `resolved`, then runs:

1. `pass1()` for inode/block scan.
2. `pass1b()` when duplicates were found.
3. `pass2()` for pathnames and directory validation.
4. `pass3()` for connectivity.
5. `pass4()` for reference counts and unreferenced objects.
6. `pass5()` for cylinder-group summaries and resource maps.

After phases it prints file/block/free-fragment summary, emits debug residue for missing files/blocks/duplicates/zero-link inodes, frees per-run structures, marks the superblock dirty when modified, writes duplicate superblocks for conversion mode, and calls `ckfini(resolved)` so unresolved answers or required reruns prevent marking the filesystem clean.

## Dependencies

- FFS/UFS metadata via `<ufs/ufs/dinode.h>` and `<ufs/ffs/fs.h>`.
- `fsck.h`, `extern.h`, and `fsutil.h` for phase APIs, block device handling, prompts, and buffer utilities.
- `setup.c` owns opening and validation; pass files own checks; `utilities.c` owns I/O finalization.

## Risks And Edge Cases

- `resolved` is deliberately cleared when a user refuses a fix or `rerun` is set; this prevents a dirty filesystem from being marked clean.
- Preen mode treats setup failure and duplicate blocks as fatal paths.
- Alternate superblock and conversion options disable clean-skip behavior.
- If the root filesystem is modified, the code attempts a read-only mount update/reload and otherwise requests reboot.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass1.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass1.c

## Scope

Phase 1 for `fsck_ffs`: scans allocated inodes, validates inode type/size/block layout, records file and block usage, builds per-inode state, detects bad and duplicate blocks, and records zero-link-count allocated inodes.

## Main APIs

- `pass1()` reserves filesystem metadata blocks in `blockmap`, allocates `inostathead` entries per cylinder group, iterates initialized inode ranges, and calls `checkinode()`.
- `checkinode()` validates one inode, sets inode state/type, caches directories, walks blocks through `ckinode()`, and repairs incorrect `di_blocks`.
- `pass1check()` is the block callback used by `ckinode()` to validate ranges, set allocation bits, count used blocks, and populate duplicate-block lists.

## Control Flow

The pass first marks reserved superblock/cylinder-summary areas used. It then walks cylinder groups, sizes inode-state allocation from `cg_initediblk` for UFS2 or `fs_ipg` for UFS1, and scans each inode at or above `ROOTINO`.

`checkinode()` treats mode zero with nonzero block/size data as a partially allocated inode and offers to clear it. Allocated inodes are rejected if file size exceeds kernel/filesystem limits, directories exceed `MAXDIRSIZE`, file type is invalid, direct block pointers exist beyond computed size, or indirect pointers exist beyond expected depth. Directories are cached for later phases; normal files are marked `FSTATE`; bad/unknown inodes can become `FCLEAR`.

`pass1check()` rejects out-of-range fragments, caps excessive bad and duplicate reports, inserts duplicates into `duplist`/`muldup`, and increments `id_entryno` so final block count can be compared to `di_blocks`.

## Dependencies

- Relies on inode access helpers `getnextinode()`, `ginode()`, `freeinodebuf()`, `cacheino()`, `ckinode()`, `clearinode()`, and `inodirty()`.
- Uses global block map helpers `setbmap()`, `testbmap()`, `chkrange()`.
- Uses `MAXBAD` and `MAXDUP` thresholds to prevent runaway diagnostics.

## Risks And Edge Cases

- Fast symlink handling fakes `ndb` so garbage block pointers after inline symlink contents are detected.
- Link counts less than or equal to zero are not immediately cleared; they are queued in `zlnhead` for pass 4.
- Duplicate tracking distinguishes first duplicate occurrences from later repeated reports using `muldup`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass1b.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass1b.c

## Scope

Phase 1b for `fsck_ffs`: rescans allocated inodes to identify all inode references to blocks already marked duplicate in phase 1.

## Main APIs

- `pass1b()` initializes an address descriptor with `pass1bcheck()` and walks all inodes in all cylinder groups.
- `pass1bcheck()` compares each fragment in an inode block extent against the duplicate list.

## Control Flow

`pass1b()` starts `duphead` at `duplist` and rescans every non-`USTATE` inode at or above `ROOTINO` using `ckinode()`. For each block fragment, `pass1bcheck()` checks range validity and walks duplicate entries until `muldup`. On a match it reports `DUP`, moves the current duplicate to the head position, and advances `duphead`. The pass stops once all known duplicates have been found.

## Dependencies

- Uses `duplist`/`muldup` populated by `pass1check()`.
- Uses `ginode()`, `ckinode()`, `GET_ISTATE()`, `chkrange()`, and `blkerror()` from shared fsck code.

## Risks And Edge Cases

- Only runs in interactive mode; `main.c` treats duplicates with `-p` as an internal fatal condition.
- The duplicate-list mutation is order-sensitive and uses `duphead` to avoid rescanning already resolved duplicate reports.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass1b.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass2.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass2.c

## Scope

Phase 2 for `fsck_ffs`: validates root inode state, checks all directory contents, repairs `.` and `..`, removes invalid directory entries, decrements expected link counts, records parent relationships, builds child lists, and marks directories reachable from root.

## Main APIs

- `pass2()` handles root inode repair, sorts cached directories by first block, runs directory scans, verifies `..`, builds child lists, and calls `propagate(ROOTINO)`.
- `pass2check()` is the directory-entry callback.
- `blksort()` orders directory inode info by disk block for better locality.

## Control Flow

The root inode is required to be a directory. If unallocated, bad, or a file, `pass2()` offers allocation, reallocation, or type correction. It marks root `DFOUND`, sorts `inpsort`, validates each directory size, creates a synthetic inode descriptor from cached block pointers, and scans entries through `ckinode()`.

`pass2check()` enforces first entry `.` and second entry `..`, including type fields. It removes extra `.`/`..`, out-of-range inode references, unallocated entries, and entries pointing to bad/duplicate inodes when approved. Directory hard links are diagnosed as extraneous and can be removed. Valid references decrement `ILNCOUNT()`, and directory entries update parent discovery.

A second pass fixes wrong or missing `..` after all parents are known. Finally children are linked under parents and reachability is propagated from root.

## Dependencies

- Directory and inode helpers: `ckinode()`, `makeentry()`, `changeino()`, `allocdir()`, `freeino()`, `getinoinfo()`, `getpathname()`, `propagate()`.
- Uses inode states `USTATE`, `DSTATE`, `DFOUND`, `DCLEAR`, `FSTATE`, `FCLEAR`.

## Risks And Edge Cases

- If a missing `.` or `..` cannot fit in existing record space, the code reports inability rather than reshaping the directory.
- Preen mode removes some bad directory entries automatically but leaves harder cases for interactive repair.
- The parent/child model assumes one real parent per directory and treats additional hard links to directories as extraneous.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass3.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass3.c

## Scope

Phase 3 for `fsck_ffs`: finds disconnected directories and attempts to reconnect orphaned directory subtrees through `lost+found`.

## Main APIs

- `pass3()` walks cached directories in reverse sorted order, detects directories not found from root, calls `linkup()`, updates parent/sibling relationships, and propagates reachability.

## Control Flow

For each directory except root, the pass skips already connected directories and clear-zero directories. For disconnected directories it walks up parent links until it finds an unparented directory, a parent not in `DSTATE`, or a loop guard exceeds `numdirs`. It then calls `linkup(orphan, inp->i_dotdot)`. On success, the reconnected directory’s parent and `..` are set to `lfdir`, `lost+found` link count is decremented, and the node is inserted into the `lost+found` child list. `propagate(orphan)` marks the recovered subtree.

## Dependencies

- Uses directory cache from pass 1 and parent data from pass 2.
- Depends on `linkup()` and `propagate()` from shared fsck directory code.
- Uses `lfdir` as the established lost+found inode.

## Risks And Edge Cases

- Loop detection is bounded by `numdirs`; malformed parent cycles beyond that are treated as orphan roots.
- Directories in `DCLEAR` are skipped because later cleanup handles them.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass4.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass4.c

## Scope

Phase 4 for `fsck_ffs`: resolves remaining inode reference-count problems, clears unreferenced files/directories, clears bad/duplicate inodes, and releases blocks no longer referenced.

## Main APIs

- `pass4()` iterates allocated inode-state tables and dispatches by inode state.
- `pass4check()` is an address callback that removes duplicate entries or clears block allocation bits.

## Control Flow

For `FSTATE` and `DFOUND`, nonzero remaining `ILNCOUNT()` values are corrected with `adjust()`. Zero-link inodes recorded in `zlnhead` are cleared as unreferenced. `DSTATE` directories are unreferenced and cleared. `DCLEAR` with zero size is cleared as zero-length; otherwise `DCLEAR` and `FCLEAR` are cleared as bad/duplicate. `USTATE` is ignored.

`pass4check()` walks each block fragment. Out-of-range blocks are skipped. Allocated blocks are compared against `duplist`; matching duplicate records are removed. If no duplicate record remains for a referenced block, the bit is cleared from `blockmap` and global used-block count decrements.

## Dependencies

- Uses `clri()`, `adjust()`, `ginode()`, `pass4check()` through `freeblk()`, and block-map helpers.
- Consumes `zlnhead` and `duplist` built in earlier phases.

## Risks And Edge Cases

- Duplicate list removal and block-map clearing happen per fragment, so partial fragments must stay consistent with `id_numfrags`.
- Zero-link processing mutates `zlnhead` by replacing found entries with the head value before freeing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass5.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass5.c

## Scope

Phase 5 for `fsck_ffs`: rebuilds cylinder-group summary information, inode/free-block bitmaps, fragment summaries, cluster summaries, and total free-count state from fsck’s computed inode/block maps.

## Main APIs

- `pass5()` is the only function. It constructs a fresh cylinder group image in `newcg`, compares it with each on-disk cylinder group, and repairs mismatches.

## Control Flow

The pass first handles conversion-level cluster-map creation/deletion when `cvtlevel >= 3`. It supports both `FS_42POSTBLFMT` and `FS_DYNAMICPOSTBLFMT`, calculating offsets for inode maps, block maps, and cluster summaries.

For each cylinder group, it initializes metadata fields, validates magic, recalculates inode usage from `inostathead`, marks pre-root inodes used in cg 0, then scans `blockmap` to rebuild free fragment/block maps and free counters. It updates fragment summaries via `ffs_fragacct()` and cluster run summaries when enabled. Per-cg summaries are accumulated into `cstotal`, compared to superblock summary slots, and repaired through `dofix()`.

At the end, the total superblock summary is compared and corrected, and `fs_ronly`/`fs_fmod` are cleared before marking the superblock dirty.

## Dependencies

- Uses FFS layout macros and bitmap helpers from `<ufs/ffs/fs.h>`.
- Consumes `blockmap` and `inostathead` built by prior phases.
- Uses `cglookup()`, `dirty()`, `sbdirty()`, `dofix()`.

## Risks And Edge Cases

- Old 4.2 rotational table format temporarily rewrites `fs_nrpos` to 8 and restores it after processing.
- Cluster-summary sizing can require superblock and cylinder-group layout changes.
- The repair messages are coarse-grained; bitmap mismatches are repaired by copying the computed map wholesale.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/setup.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/setup.c

## Scope

Filesystem setup and superblock validation for `fsck_ffs` and `fsdb`. It opens devices, reads disklabels, finds and validates primary or alternate superblocks, fixes derived superblock fields, reads summary information, and allocates fsck working maps.

## Main APIs

- `setup(dev, isfsdb)` prepares a filesystem for checking or editing.
- `readsb(listerr)` locates and validates a superblock.
- `badsb()` reports bad-superblock reasons.
- `calcsb()` derives a prototype FFS superblock from disklabel partition geometry to search alternates.
- `getdisklabel()` reads `DIOCGDINFO`.
- `cmpsb()` compares stable primary/alternate superblock fields.

## Control Flow

`setup()` opens the raw device read-only, resolves canonical device names, applies `unveil()`/`pledge()` depending on caller/root state, optionally opens for write, initializes superblock buffers, and determines sector size. It reads the superblock via `readsb()`. If primary lookup fails and interactive recovery is possible, it calculates prototype geometry and searches known alternate locations and per-cylinder-group backup superblocks for UFS1/UFS2.

After a usable superblock is found, clean filesystems can be skipped. Otherwise it calculates `maxfsblock`, `maxino`, and max file size, validates and optionally repairs superblock fields including optimization policy, minfree, sector counts, masks, shifts, inode format, maxfilesize, maxsymlinklen, q masks, cgsize, `INOPB`, and `NINDIR`. It then reads cylinder summary blocks and allocates `blockmap`, `inostathead`, directory sort tables, directory hash heads, and buffer caches.

`readsb()` validates magic, UFS1/UFS2 locations, ncg/cpg/ncyl bounds, superblock size, power-of-two block and fragment sizes, and primary-vs-last-alternate consistency.

## Dependencies

- Device helpers from `fsutil`: `opendev()`, `blockcheck()`, `unrawname()`, `setcdevname()`.
- FFS disklabel and geometry macros.
- Buffer and allocation helpers from `utilities.c`.

## Risks And Edge Cases

- Alternate superblock search only proceeds when not preening and a prototype can be calculated.
- `cmpsb()` intentionally ignores dynamic fields, comparing only structural fields expected to match backups.
- Fixing alternate superblock mirror fields marks `asblk` dirty and can flush it early.
- `isfsdb` changes pledge behavior and skips some normal fsck assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/setup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/utilities.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/utilities.c

## Scope

Shared `fsck_ffs` utility layer: prompts, inode state lookup, block/cylinder-group buffer caches, raw I/O, finalization, allocation/free helpers, pathname reconstruction, signal handlers, progress reporting, and memory wrappers.

## Main APIs

- Prompt/state: `reply()`, `dofix()`, `ftypeok()`, `inoinfo()`.
- Buffer and I/O: `bufinit()`, `cglookup()`, `getdatablk()`, `getblk()`, `flush()`, `bread()`, `bwrite()`, `ckfini()`.
- Allocation/path helpers: `allocblk()`, `freeblk()`, `getpathname()`.
- Signals/progress: `catch()`, `catchquit()`, `voidquit()`, `catchinfo()`.
- Memory wrappers: `Malloc()`, `Calloc()`, `Reallocarray()`.

## Control Flow

The buffer cache is a small LRU of filesystem block buffers plus a lazily allocated cylinder-group cache. `getblk()` flushes dirty contents before reading a new block, while `flush()` writes dirty data and, for the primary superblock buffer, also writes summary info. `bread()` and `bwrite()` fall back to sector-by-sector diagnostics after whole-buffer I/O fails.

`ckfini()` blocks SIGINT, writes pending buffers, optionally updates the standard superblock, frees caches, marks the filesystem clean if requested and approved, prints cache stats in debug mode, closes descriptors, and restores the signal mask.

`allocblk()` scans for free fragments, updates `blockmap` and cylinder-group free maps/counters, and returns the allocated fragment. `freeblk()` delegates to `pass4check()`. `getpathname()` recursively follows `..` and directory names to build a path for diagnostics.

## Dependencies

- Uses globals from `main.c` and state from `setup.c`.
- Calls directory search callbacks `findino()` and `findname()` through `ckinode()`.
- Uses OpenBSD `SIGINFO` and `_PATH_TTY` for progress reporting.

## Risks And Edge Cases

- `ckfini()` is called from a signal handler path with an explicit comment noting a race.
- `reply()` sets `resolved = 0` on negative answers and read-only/no-write default denials.
- Cylinder-group cache memory wrappers try to reclaim cache entries before failing allocation.
- Raw I/O offsets are computed in `DEV_BSIZE` units, while fallback sector diagnostics use actual `secsize`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_ffs/utilities.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/Makefile

## Scope

Build file for OpenBSD `fsck_msdos`.

## Build Role

- Builds `PROG=fsck_msdos` with manual page `fsck_msdos.8`.
- Sources: `main.c`, `check.c`, `boot.c`, `fat.c`, `dir.c`, plus shared `fsutil.c`.
- Adds `.PATH` to `../fsck`, includes that directory, and links `libutil`.

## Dependencies

This Makefile makes `fsck_msdos` share block-device and diagnostic support with the generic fsck code while keeping FAT-specific logic in its own directory.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/boot.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/boot.c

## Scope

Boot-sector and FAT32 FSInfo parser/writer for `fsck_msdos`. It decodes the BIOS parameter block into `struct bootblock`, validates filesystem geometry, checks FAT32 backup boot blocks, and can repair/write FSInfo counters.

## Main APIs

- `readboot(dosfs, boot)` reads and validates the boot sector and FAT32 metadata.
- `writefsinfo(dosfs, boot)` updates FAT32 FSInfo free-cluster and next-free fields.

## Control Flow

`readboot()` reads sector zero using the disklabel sector size and requires the 0x55aa signature. It decodes BPB fields, validates sector size, cluster size, FAT count, FAT sector count, and filesystem version. FAT32 is detected by zero root-directory entries; FAT32-specific fields include active FAT, root cluster, FSInfo sector, and backup boot sector.

For FAT32, it validates FSInfo signatures and offers to repair them. It reads and compares the backup boot block signature and BPB/extended FAT32 fields. It then computes cluster offset, sector count, cluster count, FAT type mask, number of FAT entries, and cluster size. It rejects non-FAT32 filesystems too large for FAT12/16 and FATs too small for the cluster count.

`writefsinfo()` rereads the FSInfo area, patches `FSFree` and `FSNext`, writes it back, and intentionally returns success rather than `FSBOOTMOD` because FSInfo is often stale.

## Dependencies

- Uses global `lab.d_secsize` from `check.c`.
- Uses `ask()`, `pfatal()`, `pwarn()`, and `xperror()` from shared fsck utilities.
- Defines values consumed by `fat.c` and `dir.c` through `struct bootblock`.

## Risks And Edge Cases

- FSInfo validation reads two sectors when needed to cover both signature areas.
- Backup boot comparison ignores boot code and compares only BPB/extended metadata plus signature.
- `ClusterOffset` is allowed to be a signed-style arithmetic result stored unsigned; invalid oversize is caught later.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/boot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/check.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/check.c

## Scope

Top-level filesystem check sequence for `fsck_msdos`.

## Main APIs

- `checkfilesys(fname)` opens the device, reads disklabel and boot metadata, reads/compares FATs, checks FAT chains, scans directories, handles lost chains, writes modifications, and returns fsck exit status.
- Defines global `struct disklabel lab`.

## Control Flow

The checker unveils `/dev`, opens read-write unless forced read-only by `alwaysno`, falls back to read-only if necessary, prints device identity, reads disklabel, pledges `stdio`, and calls `readboot()`.

It reads the selected FAT or FAT 0, compares other FATs when mirroring is active, validates cluster chains through `checkfat()`, writes FAT modifications when needed, initializes directory-scan state, scans directory trees, handles lost chains, writes final FAT changes, frees state, and reports file/free/bad cluster statistics.

Exit status is `8` for fatal/unrecovered errors, `4` when modified, and `0` when clean.

## Dependencies

- Uses `readboot()`, `readfat()`, `comparefat()`, `checkfat()`, `writefat()`, `resetDosDirSection()`, `handleDirTree()`, `checklost()`.
- Uses shared `fsutil` device helpers and prompt/error functions.

## Risks And Edge Cases

- Directory scan can modify FAT state, so the code writes FATs both before and after directory processing.
- `rdonly = alwaysno` forces no-write behavior for no-answer mode.
- FAT32 non-mirrored mode reads only `ValidFat`; mirrored mode compares all FAT copies.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/check.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/dir.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/dir.c

## Scope

Directory-tree scanner and repair logic for `fsck_msdos`. It validates short and long filename entries, directory structure, file sizes versus cluster chains, directory start clusters, and reconnects lost chains into `LOST.DIR`.

## Main APIs

- `resetDosDirSection()` allocates directory scan state and initializes the root directory object.
- `finishDosDirSection()` frees directory tree, pending todo list, and buffers.
- `handleDirTree()` scans root and pending subdirectories.
- `reconnect()` creates an entry in `LOST.DIR` for a lost FAT chain.
- `finishlf()` frees lost-file reconnect buffer.

## Control Flow

The scanner maintains a lightweight in-memory tree of `dosDirEntry` nodes and a stack of pending directories. `readDosDirSection()` reads either the fixed FAT12/16 root area or cluster-chain directory data. It parses 32-byte entries, handles `SLOT_EMPTY` and deleted slots, optionally truncates entries after end-of-directory, reconstructs Win95 long filenames, validates LFN checksum/order/cluster fields, and removes invalid LFN ranges when approved.

For normal entries it builds an 8.3 name, applies any valid long name, decodes start cluster and size, removes invalid volume-label LFNs, drops clusters from zero-size files, validates start clusters, fixes directory sizes to zero, repairs `.` and `..` start clusters, queues subdirectories, and checks ordinary file size against chain length. Superfluous clusters can be dropped via `clearchain()`.

`reconnect()` locates `LOST.DIR`, finds a free slot, writes a numeric short-name entry for the lost chain head, and marks the FAT chain used.

## Dependencies

- FAT state from `struct fatEntry`: `next`, `head`, `length`, `FAT_USED`.
- Boot geometry from `struct bootblock`.
- FAT helpers `clearchain()`, `writefat()`, and `rsrvdcltype()`.
- Prompt/error helpers from `ext.h`/`fsutil`.

## Risks And Edge Cases

- Long filename handling degrades non-ASCII UTF-16 bytes to `?`; it does not do full Unicode conversion.
- Directory tree linking inserts a new child at `dir->child`, replacing the previous head in the local copy path; this old code relies mainly on traversal stack and limited tree usage.
- `LOST.DIR` is not created or extended; reconnect fails if it is absent or full.
- Comments note unimplemented uniqueness checks for reconnected names and several `XXX` areas.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/dosfs.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/dosfs.h

## Scope

Core FAT/MS-DOS filesystem data model for `fsck_msdos`.

## Main Types And Constants

- `struct bootblock` stores decoded BPB fields, FAT32 FSInfo/backup fields, calculated geometry, FAT type mask, and scan statistics.
- `struct fatEntry` stores internal per-cluster state: `next`, chain `head`, chain `length`, and flags such as `FAT_USED`.
- `struct dosDirEntry` stores architecture-independent directory tree nodes with parent/next/child links, short name, long name, attributes, start cluster, size, and fsck flags.
- `struct dirTodoNode` is the pending-directory stack node.
- Defines cluster values and masks for FAT12/16/32, LFN sequence bits, directory-empty flags, and `DOSBOOTBLOCKSIZE`.

## Dependencies

Included by `ext.h`, which exposes these types to all `fsck_msdos` modules.

## Risks And Edge Cases

- `NumClusters` is described as FAT entries count but used as the upper cluster bound.
- FAT32 support is folded into `bootblock.flags` and `ClustMask`, so callers must consistently branch on both.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/dosfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/ext.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/ext.h

## Scope

Shared declarations, options, result flags, and module APIs for `fsck_msdos`.

## Main Contents

- Extern options: `alwaysno`, `alwaysyes`, `preen`, `rdonly`, and global disklabel `lab`.
- Result flags: `FSOK`, `FSBOOTMOD`, `FSDIRMOD`, `FSFATMOD`, `FSERROR`, `FSFATAL`.
- Public APIs for boot, FAT, directory, lost-chain, prompt, and helper operations.
- Defines `LOSTDIR` as `LOST.DIR`.

## Dependencies

Includes `dosfs.h` and shared `fsutil.h`.

## Risks And Edge Cases

The return flags are bitmasks that represent both fatality and modification categories; callers must preserve and test combinations carefully.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/ext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/fat.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/fat.c

## Scope

FAT table decoder, comparator, validator, writer, and lost-chain checker for `fsck_msdos`.

## Main APIs

- `readfat()` reads one FAT copy and decodes FAT12/16/32 entries into `struct fatEntry`.
- `comparefat()` merges differences between FAT copies.
- `checkfat()` builds chain ownership/length metadata and detects loops, invalid endings, and crosslinks.
- `writefat()` encodes internal FAT state to all FAT copies.
- `checklost()` finds chains not referenced by directories and reconnects or clears them.
- `clearchain()` clears a chain; `rsrvdcltype()` formats reserved/bad/free/EOF state.

## Control Flow

`readfat()` validates the initial media/EOF byte sequence, decodes entries according to `ClustMask`, normalizes reserved values, counts free/bad clusters, and repairs invalid continuations by truncating when approved.

`comparefat()` scans all clusters and calls `clustdiffer()` to resolve mismatched free/reserved/EOF/continuation values. `checkfat()` first marks each chain head and length, then follows each chain to detect non-EOF endings, loops, out-of-range links, reserved/free terminations, and crosslinked chains. `tryclear()` prompts to clear or truncate damaged chains.

`writefat()` re-encodes FAT12 packed entries, FAT16 words, or FAT32 low 28-bit entries to every FAT copy and recomputes free count. `checklost()` scans unreferenced chain heads, asks to reconnect through `reconnect()` or clear, and repairs FAT32 FSInfo free/next values.

## Dependencies

- Uses `struct bootblock` and `struct fatEntry` from `dosfs.h`.
- Calls directory reconnect code in `dir.c`.
- Uses prompt and warning helpers from `fsutil`.

## Risks And Edge Cases

- FAT12 packing advances two clusters per three bytes and must preserve odd/even nibble layout.
- Crosslink repair may require reassigning common-chain `head` values when one chain is cleared and another retained.
- FSInfo is repaired after lost-chain handling, using the recomputed `NumFree`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/fat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/main.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/main.c

## Scope

Command-line frontend and prompt implementation for `fsck_msdos`.

## Main APIs

- `main()` parses `-p`, `-y`, `-n`, and `-f`, validates a single filesystem argument, sets the canonical device name, and exits with `checkfilesys()`.
- `ask(def, fmt, ...)` implements interactive, preen, yes-to-all, no-to-all, and read-only prompt behavior.
- `usage()` reports syntax via `errexit()`.

## Control Flow

`-f` is accepted for consistency with `fsck_ffs` but ignored. `-n` enables `alwaysno`, `-y` enables `alwaysyes`, and `-p` enables preen. `ask()` auto-fixes default-yes repairs in preen mode unless read-only, prints yes/no for forced modes, and supports `F` to switch to yes-to-all during an interactive session.

## Dependencies

- Calls `checkroot()`, `setcdevname()`, `blockcheck()`, and `checkfilesys()`.
- Uses globals declared in `ext.h`.

## Risks And Edge Cases

- In read-only mode, `ask()` always answers no even when `alwaysyes` is set.
- Preen mode only performs repairs whose caller supplied `def=1`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsck_msdos/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsdb/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsdb/Makefile

## Scope

Build file for OpenBSD `fsdb`, the interactive FFS filesystem debugger.

## Build Role

- Builds `PROG=fsdb` with manual page `fsdb.8`.
- Local sources: `fsdb.c`, `fsdbutil.c`.
- Reuses many modules from `../../sbin/fsck` and `../../sbin/fsck_ffs`, including directory, inode, pass, setup, utility, and FFS subr/table code.
- Includes fsck and fsck_ffs headers, links `libedit`, `libcurses`, and `libutil`.

## Dependencies

The Makefile intentionally composes `fsdb` from fsck internals so the debugger can use the same inode/block access and mutation logic as `fsck_ffs`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsdb/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsdb/fsdb.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsdb/fsdb.c

## Scope

Interactive FFS debugger shell. It opens an FFS filesystem using fsck setup code, exposes inode and directory mutation commands, and marks the filesystem dirty on exit.

## Main APIs And Commands

- `main()` parses `-f fsname` and `-d`, calls `setup(fsys, 1)`, enters `cmdloop()`, marks the superblock dirty, and finalizes.
- `cmdloop()` uses `libedit`/history and dispatches command table entries.
- Commands include `inode`, `lookup`/`cd`, `back`, `active`/`print`, `clri`, `uplink`, `downlink`, `linkcount`, `ls`, `rm`, `ln`, `chinum`, `chname`, `chtype`, `chmod`, `chown`, `chgrp`, `chlen`, `chflags`, `chgen`, `mtime`, `ctime`, `atime`, and quit aliases.

## Control Flow

The shell starts focused on `ROOTINO`. Command input is split by `crack()`, first offered to `el_parse()`, then matched against `cmds`. Inode focus commands load `curinode` through `ginode()`. Directory commands use `ckinode()` callbacks to list names, find components, change a slot inode, or change a slot name. Link/name commands delegate to fsck helpers `makeentry()` and `changeino()`.

Metadata mutators parse and validate values, update fields through `DIP_SET()`, call `inodirty()`, and print the updated inode. `dotime()` parses `YYYYMMDDHHMMSS[.nsec]` and uses `mktime()`.

## Dependencies

- Reuses `setup()`, `ckfini()`, `ginode()`, `clearinode()`, `ckinode()`, `findino()`, `makeentry()`, `changeino()`, and inode macros from fsck_ffs.
- Uses `libedit`/`history` for command editing.
- Shares many fsck globals locally because linked fsck modules expect them.

## Risks And Edge Cases

- The tool deliberately does low-level unchecked mutations; it always marks the filesystem dirty and tells the user to run fsck.
- Directory name replacement only succeeds if the new `DIRSIZ()` fits the existing record length.
- `chmode()` and several mutators return `1` even after successful modification, causing the loop to warn about nonzero return; this is existing behavior.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsdb/fsdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsdb/fsdb.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsdb/fsdb.h

## Scope

Shared declarations for the `fsdb` interactive debugger.

## Main Contents

- Declares imported low-level I/O and prompt functions: `bread()`, `bwrite()`, `reply()`.
- Defines `struct cmdtable` for command name, help text, argument bounds, and handler.
- Exposes active inode globals `curinode` and `curinum`.
- Declares utility functions `crack()`, `argcount()`, `printstat()`, `checkactive()`, `checkactivedir()`, and `printactive()`.

## Dependencies

Included by `fsdb.c` and `fsdbutil.c`; relies on `union dinode` and `ino_t` definitions from included UFS headers in users.

## Risks And Edge Cases

The command table stores `minargc`/`maxargc` including the command word itself; help and validation code report user argument counts as minus one.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsdb/fsdb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsdb/fsdbutil.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsdb/fsdbutil.c

## Scope

Utility functions for `fsdb`: command tokenization, command arity diagnostics, inode stat printing, and active-inode checks.

## Main APIs

- `crack(line, argc)` tokenizes a command line into up to eight whitespace-separated arguments.
- `argcount(cmdp, argc, argv)` prints command usage diagnostics.
- `printstat(label, inum, dp)` formats inode type, mode, size, timestamps, owner/group, link count, flags, block count, and generation.
- `checkactive()`, `checkactivedir()`, and `printactive()` validate and display the current inode.

## Control Flow

`printstat()` switches on inode type and special-cases inline symlink contents when size is below `fs_maxsymlinklen` and `di_blocks` is zero. It formats timestamps with `ctime()` when possible and falls back to numeric seconds. Owner and group names are resolved through `user_from_uid()` and `group_from_gid()`.

## Dependencies

- Uses `DIP()` macros and global `sblock` from fsck_ffs.
- Uses `curinode`/`curinum` from `fsdb.c`.
- Uses system user/group lookup helpers.

## Risks And Edge Cases

- `crack()` uses a static fixed-size argv array of eight entries; longer commands are silently truncated by token count.
- `printactive()` handles unknown inode modes without mutating state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsdb/fsdbutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsirand/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsirand/Makefile

## Scope

Build file for OpenBSD `fsirand`.

## Build Role

- Builds `PROG=fsirand` with manual page `fsirand.8`.
- Links `libutil`.

## Dependencies

The program itself is a single-source utility using OpenBSD device helpers from `libutil`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsirand/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsirand/fsirand.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/fsirand/fsirand.c

## Scope

FFS inode-generation and filesystem-id randomizer. It can print current generation values or rewrite `fs_id` and every inode `di_gen`.

## Main APIs

- `main()` parses `-b`, `-f`, `-p`, raises data-size limit, and runs `fsirand()` for each device.
- `fsirand(device)` performs all superblock validation, optional printing, randomization, and writes.
- `usage()` reports syntax.

## Control Flow

The utility opens the device read-only for print mode or read-write otherwise, optionally reads disklabel sector size, pledges `stdio`, searches known superblock locations, validates FFS magic/location/size/format, rejects non-clean filesystems unless forced, and verifies all backup superblocks.

For modern inode formats, non-print mode randomizes `fs_id[0]` with current time and `fs_id[1]` with `arc4random()`, writes the primary superblock, then writes each backup superblock. It reads each cylinder group’s inode area into a reusable buffer and either prints generation numbers or assigns new random generations for all inodes at or above `ROOTINO`, then writes modified inode buffers.

## Dependencies

- Uses FFS/UFS structures and macros including `SBLOCKSEARCH`, `ino_to_fsba()`, and `cgsblock()`.
- Uses `opendev()` from `libutil`.
- Uses disklabel `DIOCGDINFO` unless `-b` ignores labels.

## Risks And Edge Cases

- Refuses old `FS_42POSTBLFMT`.
- Clean-check can be bypassed with `-f`; otherwise it requires `FS_ISCLEAN`.
- Writes the primary superblock at `SBOFF`, while searched superblock location may be from `SBLOCKSEARCH`.
- Reads entire `fs_ipg` inode set per cylinder group, which can be large.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/fsirand/fsirand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/growfs/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/growfs/Makefile

## Scope

Build file for OpenBSD `growfs`.

## Build Role

- Builds `PROG=growfs` with manual page `growfs.8`.
- Links `libutil`.
- Contains commented `CFLAGS+=-Wall`.

## Dependencies

The source is standalone `growfs.c` plus OpenBSD system headers and `libutil` device helpers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/growfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/growfs/growfs.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/growfs/growfs.c

## Scope

Offline FFS filesystem grower. It expands an unmounted clean FFS partition to a larger disklabel/user-specified size, updates superblock geometry, creates or expands cylinder groups, moves cylinder-summary storage when needed, relocates occupied blocks, rewrites references, and updates the disklabel.

## Main APIs

- `main()` parses `-N`, `-q`, `-s size`, `-v`, `-y`, opens devices, validates disklabel/partition/superblock, computes new geometry, confirms backup, and calls `growfs()`.
- `growfs()` coordinates the grow operation and writes summaries, superblocks, and backups.
- `initcg()` creates new cylinder groups.
- `updjcg()` expands the former last cylinder group.
- `updcsloc()` expands or relocates cylinder-summary storage.
- `updrefs()` and `indirchk()` walk inode direct and indirect block references to update relocated data blocks.
- Low-level helpers: `rdfs()`, `wtfs()`, `alloc()`, `isblock()`, `clrblock()`, `setblock()`, `ginode()`, `frag_adjust()`, `cond_bl_upd()`, `updclst()`, disklabel helpers, and `ffs1_sb_update()`.

## Control Flow

`main()` opens the raw device for read and write unless dry-run `-N`, reads the disklabel, verifies an FFS partition, reads a valid UFS1/UFS2 superblock, requires a clean filesystem, rejects active snapshots unless expert `-y`, confirms backup, probes the final sector, computes new `fs_size`, `fs_ncg`, `fs_ncyl`, `maxino`, and expanded `fs_cssize`, then runs the grow.

`growfs()` reads old cylinder summaries, updates the old last cylinder group, initializes all newly added groups, then calls `updcsloc()` to handle cylinder-summary growth. It writes the expanded summary area, writes the new primary superblock dirty, sanitizes dynamic fields for backup copies, and writes duplicate superblocks for all cylinder groups.

`updcsloc()` either relocates the entire cylinder-summary area to a new cylinder group when the original group lacks enough free blocks, or grows it in place. In-place growth may consume blocks currently holding data; those blocks are copied to newly allocated blocks, then every allocated directory/regular-file/non-fast-symlink inode and indirect block is scanned so references to old fragments are rewritten.

## Dependencies

- FFS/UFS layout macros and on-disk structures.
- Disklabel ioctls `DIOCGDINFO` and `DIOCWDINFO`.
- `opendev()` from `libutil`.
- Uses `arc4random()` to initialize generation numbers for new inodes.

## Risks And Edge Cases

- The file explicitly notes incomplete snapshot copy-on-write support; normal mode refuses active snapshots unless `-y`.
- Dry-run `-N` cannot simulate some later relocation paths because it would need data just written to new cylinder groups.
- Cylinder-summary relocation has two strategies with different compatibility implications; moving it to a new group may require fsck versions aware of nonstandard summary placement.
- Reference updates only scan directory, regular file, and non-fast-symlink blocks, matching where block pointers are expected.
- After growing, the filesystem is intentionally marked dirty so fsck should be run.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/growfs/growfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ifconfig/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/ifconfig/Makefile

## Scope

Build file for OpenBSD `ifconfig`.

## Build Role

- Builds `PROG=ifconfig` with sources `ifconfig.c`, `brconfig.c`, and `sff.c`.
- Installs manual page `ifconfig.8`.
- Links `libutil` and `libm`.

## Dependencies

This file is outside the filesystem utilities but included in the group. It defines only build composition and library dependencies for the networking configuration tool.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ifconfig/Makefile -->