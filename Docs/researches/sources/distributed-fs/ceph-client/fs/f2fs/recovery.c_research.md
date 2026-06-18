# sources/distributed-fs/ceph-client/fs/f2fs/recovery.c

## Purpose

`recovery.c` implements F2FS roll-forward recovery for fsynced data after an unclean shutdown. It scans the warm-node segment chain for recoverable fsync-marked dnodes, reconstructs missing inode pages when needed, recovers inode metadata, dentries, inline data, xattrs, and data block mappings, fixes write pointers, and writes a recovery checkpoint when data recovery succeeds.

## Important APIs and functions

- `f2fs_space_for_roll_forward()` checks whether recovery has enough user blocks and does not exceed the configured roll-forward node block limit.
- `find_fsync_dnodes()` scans recoverable warm-node pages, builds a list of inodes requiring recovery, reconstructs missing inode pages for inode+dentry-marked nodes, tracks last dentry blocks, and detects looped node chains.
- `recover_inode()` restores mode, uid/gid, project quota, size, timestamps, advise flags, F2FS inode flags, GC failure count, inline flags, and marks the inode dirty.
- `recover_dentry()` reconstructs the parent directory entry from the raw inode name/pino, handling encrypted and casefolded names and replacing conflicting entries.
- `do_recover_data()` recovers inline xattrs, xattr node data, inline data, and data block addresses for one recovered node page.
- `check_index_in_prev_nodes()` finds and truncates previous mappings for a destination block so recovery does not leave duplicate live references.
- `recover_data()` performs the second pass over recoverable dnodes, applying inode, dentry, and data recovery to entries discovered in the first pass.
- `f2fs_recover_fsync_data()` is the main entry point for check-only and real recovery.
- `f2fs_create_recovery_cache()` and `f2fs_destroy_recovery_cache()` manage the `fsync_inode_entry` slab.

## Control flow and state

Recovery starts in `f2fs_recover_fsync_data()`. It takes `cp_global_sem` for write to block checkpoint, then calls `find_fsync_dnodes()`. In check-only mode, finding recoverable fsync data or a new inode returns `1` without modifying data. In real mode, it sets `need_writecp`, calls `recover_data()`, releases inode lists, truncates temporary meta pages, fixes zoned write pointers, clears `SBI_POR_DOING`, drops recovered directory inodes, sets `SBI_IS_RECOVERED`, and writes a `CP_RECOVERY` checkpoint.

The first pass begins at `NEXT_FREE_BLKADDR()` of `CURSEG_WARM_NODE` and follows `next_blkaddr_of_node()` through recoverable dnodes. It uses `is_recoverable_dnode()` to match checkpoint version/CRC and `is_fsync_dnode()` to select fsynced nodes. It handles the documented roll-forward scenarios where inode and dnode fsync/dentry marks can appear before or after checkpoint. `sanity_check_node_chain()` uses Floyd-style fast pointer scanning to detect loops and stop corrupt recovery chains.

The second pass scans the same recoverable chain. For each node whose inode is in the recovery list, it may recover inode attributes, recover the dentry if this is the last dentry-marked block for the inode, and call `do_recover_data()`. Once the node block matching `entry->blkaddr` is processed, the inode entry moves to a temporary list to show it is done.

`do_recover_data()` first handles xattr and inline data special cases. For normal data addresses, it obtains or allocates the current dnode path, validates source and destination block addresses, adjusts file size unless `file_keep_isize()` applies, truncates stale source blocks for `NULL_ADDR` destinations, reserves blocks for `NEW_ADDR`, removes any previous reference to the destination block, and finally calls `f2fs_replace_block()` to map the recovered destination block with the right NAT version. It then copies the recovered node footer and marks the current dnode dirty.

## Persistence behavior

The file repairs persistent state after a crash. It can create inode pages, allocate quota for recovered inodes, restore inode metadata, recreate directory entries, delete conflicting dentries into orphan handling, recover inline xattr and xattr-node contents, update block mappings, invalidate stale data blocks, reserve new blocks, replace blocks, allocate new segments, clear power-on-recovery state, and write a checkpoint. It also sets quota repair flags if quota transfer fails during recovered uid/gid changes.

The recovery chain depends on node footer persistence from `node.h`: checkpoint version/CRC, fsync mark, dentry mark, inode number, node id, node offset, and next block address. Its output depends on node-manager helpers in `node.c` to rebuild NAT and node-page state consistently.

## Dependencies and integration points

`recovery.c` depends on node helpers, segment summaries, current segment state, directory entry operations, filename hashing/casefolding/encryption helpers, quota APIs, inline data/xattr helpers, block replacement, checkpoint, write-pointer repair, and error handling. It integrates tightly with `namei.c` because recovered dentries must match normal directory formats, and with `node.c` because all recovered data passes through dnode lookup/allocation, node info validation, xattr recovery, and inode-page reconstruction.

## Risks and edge cases

- Recovery follows on-disk `next_blkaddr` links; loop detection and block-address validation are essential to avoid infinite scans or reading arbitrary metadata.
- Encrypted plus casefolded names may not be hashable without keys, so `init_recovered_filename()` uses the saved on-disk hash appended after the encrypted name.
- `recover_dentry()` deletes conflicting entries and retries; failures after orphan acquisition or quota initialization can leave recovery incomplete and force mount failure/repair.
- `check_index_in_prev_nodes()` uses segment summaries to find previous owners of a destination block; inconsistent summaries are treated as corruption.
- `do_recover_data()` must avoid duplicate block references while handling `NULL_ADDR`, `NEW_ADDR`, and valid destination cases differently.
- If recovery fails, node and meta mappings are truncated and `SBI_POR_DOING` may remain set, so subsequent mount behavior depends on the propagated error.

## Test signals

Recovery tests should cover the eight documented inode/dnode ordering scenarios, check-only mode, missing inode reconstruction, encrypted names, encrypted+casefolded saved hashes, conflicting dentries, quota uid/gid/project changes, inline data, inline xattr, external xattr nodes, `NULL_ADDR` and `NEW_ADDR` destinations, duplicate destination block cleanup via previous summaries, looped node chains, invalid block addresses, zoned write-pointer repair, recovery checkpoint writing, and failure paths that truncate node/meta mappings.
