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
