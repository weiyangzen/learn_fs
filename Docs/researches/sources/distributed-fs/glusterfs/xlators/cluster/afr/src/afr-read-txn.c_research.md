# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-read-txn.c

## Purpose
Implements AFR read transaction selection and retry logic. It chooses a readable replica for a read-like operation, refreshes inode readability state when cached generations are stale, retries failed reads on alternate readable children, and handles thin-arbiter decision paths.

## Important APIs, types, and functions
`afr_read_txn()` is the exported orchestration function. `afr_read_txn_wind()` updates pending read counters and invokes the caller-provided read wind function. `afr_read_txn_continue()` refreshes once after a failed read, then falls through to `afr_read_txn_next_subvol()`. `afr_read_txn_refresh_done()` picks a new read subvol after refresh or applies split-brain choice. Thin-arbiter helpers `afr_ta_read_txn_synctask()` and `afr_ta_read_txn()` use xattrop and a thin-arbiter lock to determine which data child is safe when a brick is down.

## Control flow
The caller supplies an inode, read wind callback, and transaction type. AFR verifies quorum, consistent I/O, and thin-arbiter quorum. It consults cached inode read-subvolume state, intersects data and metadata readable masks, refreshes stale caches, selects by policy, and winds the chosen child. On child read failure, the caller callback invokes `afr_read_txn_continue()`, which refreshes once and then tries each unread attempted readable child before finally winding `subvol == -1` to force unwind with the stored error.

## State and persistence behavior
State is frame-local (`readable[]`, `read_attempted[]`, `read_subvol`, `refreshed`, transaction type) plus `priv->pending_reads[]` atomics. Thin-arbiter logic performs xattrop reads of pending changelog state and takes a thin-arbiter inodelk but does not change user data.

## Dependencies and integration points
Used by directory reads and inode reads. Depends on inode refresh/readable caches, read-subvolume policy, split-brain choice helpers, quorum helpers, thin-arbiter loc/xattr helpers, syncop xattrop/inodelk, and child up/event generation state.

## Risks and test signals
Risks include off-by-one child-index checks in pending read counters, stale generation handling, retry loops skipping valid children, split-brain choice overriding incorrectly, thin-arbiter lock/xattrop failures returning misleading errno, and pending read counter imbalance. Tests should cover first read on uncached inode, stale generation refresh, failover after read error, no readable subvol, split-brain chosen child, thin-arbiter one-child-down reads, and pending read accounting.
