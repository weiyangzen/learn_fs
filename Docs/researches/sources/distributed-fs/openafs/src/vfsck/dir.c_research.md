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
