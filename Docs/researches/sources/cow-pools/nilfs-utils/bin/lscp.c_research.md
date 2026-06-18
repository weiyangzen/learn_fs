# File Research: sources/cow-pools/nilfs-utils/bin/lscp.c

Implements `lscp`, the checkpoint and snapshot lister. Options include showing all checkpoints, block count versus increment count, reverse order, snapshot-only mode, starting index, and line limit.

It opens NILFS read-only with device search, retrieves checkpoint stats with `nilfs_get_cpstat()`, then pages checkpoint records through `nilfs_get_cpinfo()`. Forward scans are straightforward batched iteration. Reverse checkpoint scans use an accelerating/decelerating search strategy to find earlier checkpoints efficiently.

Snapshot mode follows the snapshot list using `ci_next` for forward listing. Reverse snapshot listing falls back to checkpoint-window scans and a remainder pass over snapshot records. Output includes CNO, timestamp, mode, minor flag, block or increment count, and inode count.
