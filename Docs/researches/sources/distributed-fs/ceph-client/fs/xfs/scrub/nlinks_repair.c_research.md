# sources/distributed-fs/ceph-client/fs/xfs/scrub/nlinks_repair.c

## Purpose
`nlinks_repair.c` repairs inode link counts using the shadow data collected by live nlink scrub. It also reconciles unlinked-list membership and can reattach orphaned linked files to `/lost+found`.

## Important APIs, Types, And Functions
`xrep_setup_nlinks` prepares the orphanage if repair might need adoption. `xrep_nlinks` is the public repair entry point. `xrep_nlinks_repair_inode` is the core per-inode repair routine. `xrep_nlinks_is_orphaned` decides when a linked inode with no observed parents should be adopted. `xrep_nlinks_iunlink_remove` removes an inode from the AG unlinked list.

## Control Flow
Repair requires filetype support because it must distinguish subdirectory links accurately. It scans allocated inodes with `xchk_iscan`, cancels the ordinary scrub transaction before each inode, then repairs with either an adoption-capable transaction or a simple link-count transaction. If orphanage adoption is possible, the code takes IOLOCKs for the orphanage and target, allocates adoption resources, computes a unique orphanage name, moves the inode, and reloads the shadow counts because the move itself updates observations through hooks.

After adoption decisions, the routine removes a linked inode from the unlinked list or adds an unlinked inode to it. It sets `i_nlink` to the observed total capped at `XFS_NLINK_PINNED`, logs the inode, commits dirty transactions, and releases all locks.

## State And Persistence Behavior
Persistent changes include directory entries in `/lost+found`, parent pointers from adoption, unlinked-list updates, and inode core link count updates. The repair relies on the scrub phase keeping live hook data active so the shadow counts reflect repairs and concurrent changes. Transactions are carefully shaped around lock order and resource reservations.

## Dependencies And Integration Points
It depends on `nlinks.h`, orphanage adoption helpers, unlinked-list APIs, inode scanning, tracepoints, and XFS transaction helpers. It is invoked by the scrub framework after `xchk_nlinks` reports fixable corruption.

## Risks And Edge Cases
Repair refuses ftype-less filesystems. Non-directories with observed child directory links are considered unfixable in this path. Adoption can be skipped if orphanage setup or reservation fails, in which case simple nlink repair is still attempted. Hook aborts cancel repair to avoid applying incomplete observations. The code must maintain IOLOCK-before-transaction and ILOCK transaction join order.

## Test Signals
Cover orphaned but linked files, orphaned directories, stale unlinked-list membership, zero-link files missing from unlinked lists, adoption name collisions, repair during live directory churn, and failure to allocate orphanage resources.
