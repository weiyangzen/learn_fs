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
