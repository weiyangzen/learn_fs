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
