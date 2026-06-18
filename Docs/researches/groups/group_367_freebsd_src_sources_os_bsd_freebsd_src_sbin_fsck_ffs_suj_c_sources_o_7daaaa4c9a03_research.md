# Group Research: group_367_freebsd_src_sources_os_bsd_freebsd_src_sbin_fsck_ffs_suj_c_sources_o_7daaaa4c9a03

Scope checked against `Docs/research_subset_a.md`. All listed files were read completely in manifest order.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/suj.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/suj.c

## Purpose

Implements `fsck_ffs` recovery using UFS/FFS Soft Updates Journaling (SU+J). The file parses the `.sujournal` inode, reconstructs valid journal segments, builds per-cylinder-group recovery tables, and applies block, inode, truncate, link-count, and unlinked-inode repairs before marking the filesystem clean.

## Main Entry Points

- `suj_check(const char *filesys)`: top-level SU+J recovery orchestration.
- `suj_checkblkavail(ufs2_daddr_t blkno, long frags)`: checks and reserves free fragments for snapshot handling.
- `initsuj(void)`: resets all module-global recovery state.

## Core Data Structures

- `struct suj_seg`: in-memory journal segment with `jsegrec` header and copied segment bytes.
- `struct suj_rec`: wrapper for journal records queued on inode/block lists.
- `struct suj_ino`: per-inode recovery state, including ref records, move records, pending truncation, link adjustments, dot-link count, and block-adjust flag.
- `struct suj_blk`: per-base-block journal state for allocation/free records.
- `struct suj_cg`: per-cylinder-group hash tables for affected inodes and blocks, plus cached CG buffer.
- `struct jblocks` / `struct jextent`: extent map of the journal inode so the circular journal can be scanned as contiguous disk ranges.

## Recovery Flow

1. `suj_check()` initializes state, finds the journal inode in the root directory, verifies its flags, mode, size, timestamp, and link count with `suj_verifyino()`.
2. The journal inode’s block map is visited with `ino_visit()` and stored in `suj_jblocks`.
3. `suj_read()` scans journal extents, validating segment headers, timestamps, segment sizes, block continuity, and sequence metadata.
4. `suj_prune()` discards expired or non-contiguous segments and computes processed byte/record counters.
5. `suj_build()` dispatches journal records:
   - reference records to `ino_append()`
   - block records to `blk_build()`
   - truncate/sync records to `ino_build_trunc()`
6. Per-CG passes run in a strict order:
   - `cg_build()` normalizes moved and duplicate inode references.
   - `ino_unlinked()` reclaims inodes from `fs_sujfree`.
   - `cg_trunc()` applies truncates before directory lookup.
   - `cg_check_blk()` frees incomplete or orphaned block allocations.
   - `cg_adj_blk()` recalculates inode block counts.
   - `cg_check_ino()` fixes link counts and reclaims dead inodes.
7. Snapshot block counts are checked, snapshots flushed, summary totals recomputed, clean flags set, and `ckfini(1)` finalizes writes.

## Important Algorithms

- Block safety:
  - `blk_freemask()` determines whether fragments were reallocated before freeing.
  - `blk_isindir()` decides if an indirect block can be trusted and traversed.
  - `blk_free_lbn()` recursively frees indirect trees only when safe.
- Inode traversal:
  - `ino_visit()` walks UFS direct blocks, indirect blocks, and UFS2 extattr blocks.
  - `indir_visit()` recursively traverses indirect trees with trust flags.
- Directory/link recovery:
  - `ino_isat()` validates that a directory entry still points at an inode and reports dot/dotdot status.
  - `ino_clrat()` clears stale directory entries.
  - `ino_check()` computes new link counts from initial journal link count, surviving references, removals, and dot links.
  - `ino_adjust()` writes corrected counts or reclaims the inode.
- Truncation:
  - `ino_trunc()` frees full blocks beyond a target size, truncates indirect trees, updates `di_blocks`/`di_size`, and zeroes trailing bytes.
  - `indir_trunc()` clears indirect entries beyond the retained logical block.

## Integration Points

Uses `fsck_ffs` globals and helpers from `fsck.h`, including `sblock`, `ginode()`, `irelse()`, `getdatablk()`, `dirty()`, `cglookup()`, `cgdirty()`, `ckinode()`, `findino()`, `snapremove()`, `snapflush()`, `check_blkcnt()`, and `ckfini()`. It depends heavily on UFS/FFS layout macros from `<ufs/ufs/*>` and `<ufs/ffs/fs.h>`.

## Error Handling

Fatal SU+J inconsistencies call `err_suj()`, which prints context and `longjmp`s to `suj_check()`. The caller can fall back to full fsck unless declined. Direct logic errors sometimes use `errx(1)` when continued recovery would be unsafe.

## Risk Notes

This file edits live filesystem metadata directly. Correctness depends on record ordering, fragment overlap detection, sequence pruning, and not trusting reallocated indirect blocks. The most delicate areas are `blk_freemask()`, `ino_build_ref()` move/duplicate handling, truncate ordering before directory traversal, and the distinction between recoverable journal inconsistency and unrecoverable metadata corruption.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/suj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/utilities.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/utilities.c

## Purpose

Provides `blockcheck()`, a device-name resolver used by UFS fsck-derived tools. It maps user input to a usable block or character device path when possible.

## Main Behavior

- Accepts an original filesystem/device name.
- If the path cannot be `stat()`ed and has no slash, retries under `/dev`.
- If the path is a character or block device, returns that path.
- If the path is a directory, removes a trailing slash, consults `getfsfile()`, and retries using the fstab device spec.
- If resolution fails or the target is not a device, returns the original name and leaves the caller/user to decide.

## Integration Points

Includes `fsck.h` and is shared by fsck-derived UFS utilities. Uses libc/fstab APIs and `_PATH_DEV`.

## Risk Notes

The function mutates `origname` to remove a trailing slash when resolving directories. It returns a static buffer for `/dev/<name>` expansion, so callers must not expect stable contents across repeated calls.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_ffs/utilities.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/Makefile

## Purpose

Builds the `fsck_msdosfs` FAT filesystem checker.

## Build Definition

- Program: `fsck_msdosfs`
- Manual page: `fsck_msdosfs.8`
- Sources: `main.c`, `check.c`, `boot.c`, `fat.c`, `dir.c`, and shared `fsutil.c`
- Adds include path to sibling `fsck`
- Defines `HAVE_LIBUTIL_H`
- Links `libutil`

## Integration Notes

Uses `.PATH` to pull `fsutil.c` from `sbin/fsck`, sharing prompting and diagnostic helpers with other fsck utilities.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/boot.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/boot.c

## Purpose

Parses and validates the FAT boot sector and FAT32 FSInfo sector into the internal `struct bootblock`.

## Main Entry Points

- `readboot(int dosfs, struct bootblock *boot)`: reads BPB/EBPB fields, validates geometry/layout, computes derived FAT layout values.
- `writefsinfo(int dosfs, struct bootblock *boot)`: updates FAT32 FSInfo free-count and next-free hints.

## Key Checks

- Boot signature must be `0x55aa`.
- Sector size must be 512 through 4096 and a power of two.
- Sectors per cluster must be nonzero and a power of two.
- Reserved sectors and FAT count must be valid.
- FAT32 must use 32-bit total-sector and FAT-sector fields, not legacy 16-bit fields.
- EXFAT OEM name is rejected.
- FAT32 version must be 0.0.
- FSInfo signatures are validated and optionally repaired.
- FAT type is inferred from cluster count, with bounds checks for FAT12/16/32.
- FAT size must fit the computed cluster count.

## Derived Fields

Computes `NumSectors`, `FATsecs`, `FirstCluster`, `NumClusters`, `ClustMask`, `NumFatEntries`, `ClusterSize`, and initial statistics counters.

## Integration Points

Feeds `readfat()` and directory traversal with trusted layout. Uses `ask()`, `pfatal()`, `pwarn()`, and `perr()` from the fsck utility layer.

## Risk Notes

All later FAT offsets depend on this file’s arithmetic. It contains overflow and bounds checks for FAT count, sectors per FAT, cluster area position, and FAT entry capacity.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/boot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/check.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/check.c

## Purpose

Top-level filesystem check driver for `fsck_msdosfs`.

## Main Entry Point

- `checkfilesys(const char *fname)`

## Flow

1. Opens the device read-write, falling back to read-only.
2. Reads and validates the boot block with `readboot()`.
3. In preen mode with `skipclean`, checks the FAT dirty flag and skips clean filesystems.
4. Phase 1: reads FAT and builds chain ownership state with `readfat()`.
5. Phase 2: initializes directory checking, then scans the directory tree with `handleDirTree()`.
6. Phase 3: checks for lost FAT chains with `checklost()`.
7. Writes FAT changes with `writefat()` only after directory/lost-chain processing.
8. Prints file/free/bad-cluster statistics.
9. Optionally marks FAT16/FAT32 filesystems clean via `cleardirty()`.
10. Releases directory state, FAT descriptor, and file descriptor.

## Integration Points

Coordinates `boot.c`, `fat.c`, `dir.c`, and shared prompting/diagnostic functions.

## Risk Notes

`mod` is a bitmask combining fatal, repair, dirty, and unresolved-error state. The deferred FAT write is intentional: directory repairs can depend on in-memory FAT state before final persistence.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/check.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/dir.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/dir.c

## Purpose

Validates and repairs FAT directory trees, long filename records, file sizes, dot entries, directory connectivity, and lost-chain reconnection into `LOST.DIR`.

## Main Entry Points

- `resetDosDirSection(struct fat_descriptor *fat)`: allocates buffers and initializes root directory state.
- `finishDosDirSection(void)`: frees pending directory nodes, directory tree nodes, and buffers.
- `handleDirTree(struct fat_descriptor *fat)`: scans root and pending subdirectories.
- `reconnect(struct fat_descriptor *fat, cl_t head, size_t length)`: creates entries in `LOST.DIR` for lost chains.
- `finishlf(void)`: frees lost-file working buffer.

## Directory Model

Uses `struct dosDirEntry` nodes linked by parent/child/next to represent the discovered tree, and `struct dirTodoNode` as a pending stack for breadth/depth traversal.

## Important Logic

- Long filename handling:
  - Tracks LFN sequence records in `longName`.
  - Verifies sequence index, checksum against short 8.3 name, zero cluster field, and maximum length.
  - `removede()` deletes invalid LFN runs when approved.
- Directory slot handling:
  - Detects entries after `SLOT_EMPTY`.
  - Offers to extend by deleting empty-slot gap or truncate/delete later entries.
- Cluster validation:
  - Ensures non-empty files and directories start at valid unclaimed FAT chain heads.
  - Invalid directories can be deleted; invalid files can be truncated to size zero.
- File size validation:
  - `checksize()` compares directory size with checked chain size.
  - Can truncate size or drop superfluous FAT clusters.
- Subdirectory validation:
  - `check_subdirectory()` verifies first entries are `.` and `..` with directory attributes.
  - During main scan, repairs incorrect `.` and `..` starting cluster fields.
- Lost chain reconnection:
  - `reconnect()` finds free slots in `LOST.DIR`, writes an 8.3 numeric name based on head cluster, and records the chain as a file.

## Integration Points

Uses `fat_get_cl_next()`, `fat_set_cl_next()`, `fat_is_valid_cl()`, `fat_is_cl_head()`, `checkchain()`, and `clearchain()` from `fat.c`. Uses BPB/layout values from `struct bootblock`.

## Risk Notes

Directory writes happen cluster-by-cluster, while FAT changes are delayed elsewhere. LFN deletion across cluster boundaries is particularly delicate and handled through `delete()` plus in-buffer slot updates.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/dosfs.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/dosfs.h

## Purpose

Defines FAT filesystem constants and architecture-independent in-memory data structures used by `fsck_msdosfs`.

## Key Definitions

- Boot sector sizes:
  - `DOSBOOTBLOCKSIZE_REAL` = 512
  - `DOSBOOTBLOCKSIZE` = 4096 for 4Kn reads
- Cluster type:
  - `typedef u_int32_t cl_t`
- `struct bootblock`:
  - Raw BPB fields
  - FAT32 extended fields
  - Derived layout fields
  - Filesystem statistics
- Cluster constants:
  - `CLUST_FREE`, `CLUST_FIRST`, `CLUST_RSRVD`, `CLUST_BAD`, `CLUST_EOFS`, `CLUST_EOF`, `CLUST_DEAD`
- FAT masks:
  - `CLUST12_MASK`, `CLUST16_MASK`, `CLUST32_MASK`
- Directory structures:
  - `struct dosDirEntry`
  - `struct dirTodoNode`
- Directory scan flags:
  - `DIREMPTY`, `DIREMPWARN`

## Integration Notes

Included by `ext.h`, which exposes the checker API. It is the shared type contract between boot parsing, FAT scanning, directory traversal, and check orchestration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/dosfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/ext.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/ext.h

## Purpose

Public internal header for `fsck_msdosfs`, declaring global options, return-state flags, opaque FAT descriptor accessors, and cross-file functions.

## Key Globals

- `alwaysno`, `alwaysyes`
- `preen`
- `rdonly`
- `skipclean`
- `allow_mmap`

## Return Flags

- `FSOK`
- `FSBOOTMOD`
- `FSDIRMOD`
- `FSFATMOD`
- `FSERROR`
- `FSFATAL`
- `FSDIRTY`

## Declared Interfaces

Includes functions from:
- `main.c`: `ask()`
- `check.c`: `checkfilesys()`
- `boot.c`: `readboot()`, `writefsinfo()`
- `fat.c`: dirty flag handling, FAT read/write, cluster get/set, chain checks, lost-chain scan
- `dir.c`: directory section lifecycle, tree scan, reconnect helpers

## Integration Notes

Uses an opaque `struct fat_descriptor` to keep FAT implementation details private to `fat.c` while exposing enough operations for directory checking.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/ext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/fat.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/fat.c

## Purpose

Loads, validates, repairs, writes, and scans FAT12/FAT16/FAT32 allocation tables. It also tracks chain heads to identify lost cluster chains.

## Core Data Structures

- `struct fat_descriptor`: private FAT state containing boot pointer, FAT buffer, accessor callbacks, head bitmap, file descriptor, mmap/cache state, and FAT32 cache state.
- `long_bitmap_t`: bitmap where set bits represent possible chain heads.
- `struct fat32_cache_entry`: LRU cache entry for large FAT32 tables when mmap is unavailable.

## Main Entry Points

- `readfat(int fs, struct bootblock *boot, struct fat_descriptor **fp)`
- `writefat(struct fat_descriptor *fat)`
- `checkdirty(int fs, struct bootblock *boot)`
- `cleardirty(struct fat_descriptor *fat)`
- `checkchain(struct fat_descriptor *fat, cl_t head, size_t *chainsize)`
- `checklost(struct fat_descriptor *fat)`
- `clearchain(struct fat_descriptor *fat, cl_t head)`
- Accessors: `fat_get_cl_next()`, `fat_set_cl_next()`, `fat_is_valid_cl()`, `fat_is_cl_head()`, `fat_clear_cl_head()`

## FAT Access

Implements separate get/set callbacks for:
- FAT12 packed 12-bit entries
- FAT16 little-endian 16-bit entries
- FAT32 little-endian 28-bit entries
- FAT32 cached access for large non-mmap tables

## Head Bitmap Algorithm

`readfat()` initializes every cluster as a possible chain head, then scans the FAT:
- Free and bad clusters are cleared from the head map.
- Valid next-cluster pointers clear the pointed-to cluster as a head.
- Cross-linked chains are detected when a next cluster was already cleared.
- Remaining head bits after directory traversal are candidates for lost chains.

## Repair Logic

- Odd FAT signatures can be corrected.
- Dirty FAT16/FAT32 signatures are detected.
- Out-of-range chain links can be truncated to EOF.
- Cross-linked chains can be truncated.
- `checkchain()` validates a claimed chain and can truncate or clear invalid endings.
- `checklost()` reconnects remaining chains through `reconnect()` or clears them, then fixes FAT32 FSInfo hints.

## I/O Strategy

Attempts `mmap()` unless disabled. For large FAT32 without mmap, keeps a 4 MiB working buffer split into 128 KiB LRU chunks and flushes dirty cache entries before copying FAT0 to backup FATs.

## Risk Notes

The bitmap is both an ownership model and lost-chain detector. Any missed `fat_clear_cl_head()` can create false lost chains; any premature clearing can hide real lost data. Cached FAT32 mode must flush dirty chunks before backup FAT copies.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/fat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/main.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/main.c

## Purpose

Command-line entry point and interactive prompt handler for `fsck_msdosfs`.

## Main Behavior

- Parses options:
  - `-f`: do not skip clean filesystems
  - `-F`: unsupported background check probe, exits 5
  - `-n`: assume no
  - `-y`: assume yes
  - `-p`: preen mode
  - `-M`: disable mmap
  - `-B`, `-C`: accepted for compatibility/no-op
- Iterates over filesystems, sets device name, and calls `checkfilesys()`.
- Returns the maximum filesystem check result.

## `ask()`

Central yes/no prompt function:
- Honors `alwaysyes`, `alwaysno`, and `rdonly`.
- In preen mode, automatically applies default answers and prints `FIXED` when default is yes.
- Otherwise prompts on stdin.

## Integration Notes

Defines global option variables declared in `ext.h`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsdb/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsdb/Makefile

## Purpose

Builds the `fsdb` interactive UFS/FFS filesystem debugger/editor.

## Build Definition

- Program: `fsdb`
- Manual: `fsdb.8`
- Own sources: `fsdb.c`, `fsdbutil.c`
- Reuses many `fsck_ffs` sources: directory, inode, pass, setup, utility, and FFS support files.
- Includes fsck_ffs headers.
- Links `libedit` and `libufs`.
- Pulls `prtblknos.c` from diagnostic tooling.

## Integration Notes

`fsdb` is intentionally built on fsck internals so it can inspect and mutate UFS metadata through the same inode, block, and directory routines.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsdb/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsdb/fsdb.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsdb/fsdb.c

## Purpose

Implements the interactive `fsdb` shell for inspecting and editing UFS/FFS filesystems.

## Main Flow

- `main()` parses `-d`, `-f`, and `-r`, opens and sets up the filesystem through fsck/libufs routines, then enters `cmdloop()`.
- On exit, critical modifications mark the filesystem dirty and warn the user to run fsck.
- Non-critical modifications leave clean state unchanged.

## Command Framework

`struct cmdtable cmds[]` maps command names to handler functions, argument counts, help text, and write-risk flags:
- `FL_RO`: read-only
- `FL_WR`: non-critical metadata write
- `FL_CWR`: critical filesystem-integrity write
- `FL_ST`: re-split final argument for names with spaces

Commands include:
- Navigation/inspection: `inode`, `lookup`, `cd`, `back`, `active`, `print`, `blocks`, `ls`, `findblk`
- Directory edits: `rm`, `del`, `ln`, `chinum`, `chname`
- Inode edits: `clri`, `uplink`, `downlink`, `linkcount`, `chtype`, `chmod`, `chown`, `chgrp`, `chflags`, `chgen`, `chsize`, `chdb`
- Time edits: `btime`, `mtime`, `ctime`, `atime`
- Exit: `quit`, `q`, `exit`, `quitclean`

## Important Logic

- `cmdloop()` uses libedit/history, parses commands, enforces read-only mode for write commands, and tracks whether modifications were critical.
- `setcurinode()` releases the prior inode and loads a new current inode.
- `focusname()` walks path components using fsck’s `findino()` and `ckinode()`.
- `findblk()` scans cylinder groups, inodes, direct blocks, and indirect trees to find owners of disk blocks.
- Directory slot functions (`chinumfunc()`, `chnamefunc()`) mutate directory entries through fsck directory traversal callbacks.
- Inode mutation handlers use `DIP_SET()` and `inodirty()` to write fields.

## Integration Points

Uses `fsck.h` globals and routines such as `sblock_init()`, `openfilesys()`, `readsb()`, `setup()`, `ginode()`, `irelse()`, `ckinode()`, `makeentry()`, `changeino()`, `clearinode()`, `inodirty()`, `cglookup()`, and `ckfini()`.

## Risk Notes

This is a direct metadata editor. Critical edits intentionally dirty the filesystem to force a later full fsck. `quitclean` can override that, warning the user that a modified filesystem is being marked clean.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsdb/fsdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsdb/fsdb.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsdb/fsdb.h

## Purpose

Shared declarations for `fsdb`.

## Contents

- External fsck utility functions used by fsdb: `blread()`, `rwerror()`, `reply()`.
- Shared device/filesystem state: `dev_bsize`, `secsize`, `fsmodified`, `fsfd`.
- Command metadata structure `struct cmdtable`.
- Command flag definitions for read/write safety.
- Current inode globals: `curip`, `curinode`, `curinum`.
- Utility function prototypes for argument parsing, active inode printing, and active inode validation.

## Integration Notes

Defines the contract between `fsdb.c` and `fsdbutil.c`, while relying on UFS dinode types from the fsck/FFS headers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsdb/fsdb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsdb/fsdbutil.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsdb/fsdbutil.c

## Purpose

Helper routines for `fsdb` command parsing and inode display/validation.

## Main Functions

- `crack()`: tokenizes a command line into up to 8 whitespace-separated arguments.
- `recrack()`: tokenizes with a maximum argument count, preserving the remaining text as the final argument.
- `argcount()`: prints command argument-count errors and usage.
- `printstat()`: prints inode type, mode, size, times, owner/group, link count, flags, block count, and generation.
- `checkactive()`: verifies that a current inode is loaded.
- `checkactivedir()`: verifies that current inode is a directory.
- `printactive()`: prints current inode stats or block list.

## Integration Points

Calls `prtblknos()` for block display and uses `sblock`, `DIP()`, UFS1/UFS2 timestamp handling, passwd/group lookup, and current inode globals from `fsdb.h`.

## Risk Notes

`recrack()` assumes at least one parsed token before it computes `argv[i - 1]`, matching its intended use for already validated command lines with a final free-form argument.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsdb/fsdbutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsirand/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsirand/Makefile

## Purpose

Builds the `fsirand` UFS generation-number randomizer.

## Build Definition

- Program: `fsirand`
- Manual: `fsirand.8`
- Package: `ufs`
- Links `libufs`
- Warning level set to 3

## Integration Notes

The source is standalone except for UFS/FFS/libufs APIs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsirand/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsirand/fsirand.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/fsirand/fsirand.c

## Purpose

Randomizes UFS inode generation numbers and filesystem IDs, or prints existing generation numbers in print-only mode.

## Main Entry Points

- `main(int argc, char *argv[])`
- `fsirand(char *device)`

## Options

- `-b`: accepted as `ignorelabel`, but not otherwise used in this file.
- `-f`: force operation past one clean-state check.
- `-p`: print generation numbers instead of modifying.

## Operation

1. Opens the device read-only for print mode or read-write for modification.
2. Reads the superblock with `sbget()`.
3. Rejects unclean filesystems or old UFS1 inode formats.
4. Allocates one cylinder group’s worth of inode buffer.
5. In modification mode:
   - Updates `fs_id[0]` with current time and `fs_id[1]` with `arc4random()`.
   - Writes superblock and backups with `sbput()`.
   - Iterates each cylinder group, reads inode blocks, assigns random `di_gen` values, updates UFS2 dinode checksums, and writes the inode buffer back.
6. In print mode:
   - Prints fsid information if present.
   - Prints each inode number and generation.

## Integration Points

Uses libufs superblock functions and UFS/FFS macros such as `fsbtodb()`, `ino_to_fsba()`, `UFS_ROOTINO`, and `ffs_update_dinode_ckhash()`.

## Risk Notes

Requires a clean filesystem unless forced for a secondary clean-state check. It rewrites large inode regions directly and updates UFS2 dinode checksums, so interrupted writes can require fsck.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/fsirand/fsirand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/geom/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/geom/Makefile

## Purpose

Builds the generic `geom` command-line utility and its shared helper source.

## Build Definition

- Program: `geom`
- Sources: `geom.c`, `subr.c`
- Manual: `geom.8`
- Includes core and top-level geom directories.
- Defines `GEOM_CLASS_DIR`.
- Links `libgeom`, `libutil`, and `libxo`.

## Conditional Build

- In rescue builds, statically includes `geom_label.c` and `geom_part.c`, suppresses the manual, and defines `STATIC_GEOM_CLASSES`.
- Otherwise includes `lib/geom/Makefile.classes` and creates `g<class>` hardlinks for each GEOM class.

## Integration Notes

This Makefile connects the generic dispatcher in `core/geom.c` with class-specific shared libraries or static rescue implementations.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/geom/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/geom/core/geom.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/geom/core/geom.c

## Purpose

Implements the generic GEOM userland command dispatcher. It loads class command definitions, parses command options, issues `gctl` requests, and provides standard `help`, `list`, `status`, `load`, `unload`, provider lookup, and topology tree views.

## Core Concepts

- `class_name`: lowercase class name, such as `part`.
- `gclass_name`: uppercase GEOM class name sent to kernel, such as `PART`.
- `class_commands`: command table loaded from a class library or static rescue class.
- `version`: class ABI/version pointer.
- `std_commands`: built-in generic commands available for all classes where supported.

## Command Flow

1. `main()` handles top-level `geom` options:
   - `-p provider`: list geom owning a provider.
   - `-t`: print GEOM topology tree.
   - `-h`: usage.
2. `get_class()` determines class from either `geom <class>` or a `g<class>` hardlink name.
3. `load_library()` dynamically loads `geom_<class>.so`, checks `G_LIB_VERSION`, and resolves `version` and `class_commands`.
4. `run_command()` finds a class command or standard command, optionally loads the kernel module, builds a `gctl_req`, parses options/arguments, invokes either a local command function or `gctl_issue()`, prints output, and exits.

## Option Parsing

- `parse_arguments()` builds a getopt string from `struct g_option`.
- Supports boolean, string, number, optional, and multi-value options.
- Numeric options use `expand_number()`.
- Parsed values are added to `gctl_req` as read-only params.
- Remaining positional arguments are passed as `arg0`, `arg1`, etc., plus `nargs`.

## Standard Commands

- `help`: usage.
- `list`: prints GEOM instances, providers, consumers, and config.
- `status`: tabular status by geom or provider, with script mode.
- `load`: loads kernel module if available.
- `unload`: unloads kernel module.

## Display Features

Uses `libxo` for structured output in list/status/provider modes. `show_tree()` computes column widths and recursively prints provider-consumer topology from roots.

## Integration Points

Uses `libgeom` for `geom_gettree()`, `geom_gettree_geom()`, `gctl_get_handle()`, `gctl_issue()`, and GEOM mesh structures. Uses kernel module APIs `modfind()`, `kldload()`, `kldfind()`, and `kldunload()`.

## Risk Notes

Class command metadata is trusted after ABI/version checks. `set_option()` stores allocated values inside option descriptors and request params for process lifetime. Standard-command availability can issue GEOM tree queries and kernel module path sysctls before a command runs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/geom/core/geom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/geom/core/geom.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/geom/core/geom.h

## Purpose

Defines the ABI contract between the generic `geom` command and GEOM class command libraries.

## Key Definitions

- `G_LIB_VERSION` = 5
- Command flags:
  - `G_FLAG_VERBOSE`
  - `G_FLAG_LOADKLD`
- Option types:
  - bool, string, number, done, multi
- `G_OPT_MAX`
- Sentinel macros:
  - `G_OPT_SENTINEL`
  - `G_NULL_OPTS`
  - `G_CMD_SENTINEL`

## Structures

- `struct g_option`: option character, kernel/request name, default value, and type flags.
- `struct g_command`: command name, flags, optional local handler, option table, and usage string.

## Integration Notes

Class libraries export command tables using these definitions, and `geom.c` consumes them dynamically or statically.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/geom/core/geom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/geom/misc/subr.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/geom/misc/subr.c

## Purpose

Shared GEOM helper routines for numeric parsing, provider metadata I/O, media queries, bit math, and `gctl_req` parameter manipulation.

## Main Functions

- Math:
  - `g_lcm()`
  - `bitcount32()`
- User size/LBA parsing:
  - `g_parse_lba()`: parses sector/byte values with suffixes `k/m/g/t/p/e`, `b`, and `s`, returning sector counts.
- Provider queries:
  - `g_get_mediasize()`
  - `g_get_sectorsize()`
- Metadata:
  - `g_metadata_read()`: reads last sector, optionally validates magic.
  - `g_metadata_store()`: writes metadata at last sector and flushes.
  - `g_metadata_clear()`: zeros last sector, optionally only if magic matches.
- `gctl` helpers:
  - `gctl_error()`
  - `gctl_get_int()`
  - `gctl_get_intmax()`
  - `gctl_get_ascii()`
  - `gctl_change_param()`
  - `gctl_delete_param()`
  - `gctl_has_param()`

## Metadata Format

`std_metadata_decode()` decodes a standard metadata prefix:
- 16-byte magic
- little-endian 32-bit version

## Integration Points

Used by GEOM class utilities and `geom.c`. Relies on `libgeom` provider open/close/media APIs and `gctl_req` internals.

## Risk Notes

Metadata routines assert metadata fits in one sector. `gctl_get_param()` aborts on missing, unterminated, or wrong-length params, making these helpers suitable for programmer errors rather than user-facing optional lookups.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/geom/misc/subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/geom/misc/subr.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/geom/misc/subr.h

## Purpose

Header for shared GEOM helper routines implemented in `subr.c`.

## Contents

Declares:
- `g_lcm()`
- `bitcount32()`
- `g_parse_lba()`
- `g_get_mediasize()`
- `g_get_sectorsize()`
- Metadata read/store/clear helpers
- `gctl_req` error, getter, mutator, deletion, and existence helpers

## Integration Notes

Included by `geom/core/geom.c` and GEOM class tools that need consistent metadata and argument handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/geom/misc/subr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ggate/Makefile

## Purpose

Top-level subdirectory Makefile for GEOM Gate utilities.

## Build Definition

Builds subdirectories:
- `ggatec`
- `ggated`
- `ggatel`

Includes `<src.opts.mk>` and `<bsd.subdir.mk>`.

## Integration Notes

This file only orchestrates child utility builds; functionality lives in child directories and shared ggate sources.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/Makefile.inc -->
# File Research: sources/os/bsd/freebsd-src/sbin/ggate/Makefile.inc

## Purpose

Shared include for GEOM Gate child Makefiles.

## Contents

Includes FreeBSD source options via:

```make
.include <src.opts.mk>
```

## Integration Notes

Provides a common options include point for `ggatec`, `ggated`, and `ggatel`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/ggatec/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/ggate/ggatec/Makefile

## Purpose

Builds the GEOM Gate client utility `ggatec`.

## Build Definition

- Includes parent `Makefile.inc`.
- Uses shared source path `${.CURDIR:H}/shared`.
- Program: `ggatec`
- Manual: `ggatec.8`
- Sources: `ggatec.c`, shared `ggate.c`
- Package: `ggate`
- Defines:
  - `MAX_SEND_SIZE=32768`
  - `LIBGEOM`
- Adds include path to shared ggate headers.
- Links `libgeom`, `libutil`, and pthreads.

## Integration Notes

This Makefile wires the client-specific source to the shared GEOM Gate implementation and libgeom control interface.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/ggate/ggatec/Makefile -->