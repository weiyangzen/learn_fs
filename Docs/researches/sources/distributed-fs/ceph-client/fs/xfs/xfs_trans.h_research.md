# sources/distributed-fs/ceph-client/fs/xfs/xfs_trans.h

## Purpose

`xfs_trans.h` declares the kernel-only XFS transaction subsystem interface and its core shared data structures. It defines the generic log item contract, transaction state container, log item operation table, exported transaction/buffer/inode APIs, and small context helpers used by transaction allocation and release. It is the header that lets metadata code join buffers, inodes, quota items, and deferred operation items to a transaction without depending on the implementation details in `xfs_trans.c`.

## Important Types and APIs

- `struct xfs_log_item` is the common base for all loggable XFS items. It carries AIL and transaction list links, last on-disk LSN, owning log and AIL pointers, item type, atomic flag bits, optional real buffer pointer, buffer item list link, item operation table, delayed logging/CIL list links, active and shadow log vectors, commit sequence number, and CIL order id.
- Log item flags include `XFS_LI_IN_AIL`, `XFS_LI_ABORTED`, `XFS_LI_FAILED`, `XFS_LI_DIRTY`, `XFS_LI_WHITEOUT`, and `XFS_LI_FLUSHING`; `XFS_LI_FLAGS` maps them to trace strings.
- `struct xfs_item_ops` defines item-specific behavior: size calculation, log formatting, pin/unpin, stable sort key, precommit, committing, committed, AIL push, release, match, and intent lookup.
- Item operation flags `XFS_ITEM_RELEASE_WHEN_COMMITTED`, `XFS_ITEM_INTENT`, and `XFS_ITEM_INTENT_DONE` describe whether an item is released instead of AIL-tracked and whether it is an intent or intent-done item. `xlog_item_is_intent` and `xlog_item_is_intent_done` are convenience classifiers.
- `struct xfs_trans` stores log and block reservations, used reservation counters, realtime reservations, transaction flags, highest locked AGF, log ticket, mount pointer, dquot accounting pointer, staged superblock deltas, transaction item list, busy extent list, deferred operation list, and saved `memalloc_nofs` process flags.
- Exported APIs cover transaction allocation and reservation (`xfs_trans_alloc`, `xfs_trans_alloc_empty`, `xfs_trans_reserve_more`), superblock mutation (`xfs_trans_mod_sb`), buffer acquisition/read/join/log/release operations, inode joining/logging, commit/roll/cancel, AIL initialization/destruction, buffer type tagging, and transaction-aware allocation helpers for inode create/change/directory operations.

## Control Flow Contract

Callers allocate a transaction with a reservation descriptor, reserve data/realtime blocks and log space, join buffers/inodes/log items, mark items dirty, optionally stage superblock and quota deltas, then commit or cancel. Buffer helper inlines convert a single block range into `struct xfs_buf_map` and dispatch to map-based APIs. Commit and cancel are terminal; the header documents that callers must not reference the transaction afterward through the implementation comments in `xfs_trans.c`.

The log item operations table is the polymorphic control-flow hook used by the transaction and log subsystems. During commit, dirty items can be sorted by `iop_sort`, prepared by `iop_precommit`, formatted into log vectors with `iop_format`, pinned/unpinned around log IO, moved in or out of AIL by commit callbacks, pushed for writeback, and released. Intent and intent-done classification supports deferred operation recovery and matching.

## State and Persistence Behavior

`xfs_trans` separates reserved resources from used resources. `t_blk_res`/`t_blk_res_used` and `t_rtx_res`/`t_rtx_res_used` allow allocation paths to check whether transaction-local use stays within reservation and to return unused space at cancel or commit. Superblock changes are persisted indirectly: fields such as `t_icount_delta`, `t_fdblocks_delta`, `t_res_fdblocks_delta`, `t_frextents_delta`, `t_dblocks_delta`, `t_agcount_delta`, `t_rextsize_delta`, and `t_rgcount_delta` accumulate until commit code applies them to in-core counters and, when required, the logged superblock buffer.

`struct xfs_log_item` bridges in-core dirty state and persistent journal state. `li_lsn` tracks the item's on-disk log location, `li_ail` membership tracks whether writeback/tail pinning is still needed, and `li_cil`/`li_lv` fields support delayed logging in the CIL. Atomic flag updates are explicitly used because item state can race without taking the AIL lock for every flag operation.

## Dependencies and Integration Points

This header forward-declares transaction, log, buffer, mount, quota, inode, btree, and deferred intent types instead of including all definitions. It integrates with Linux list infrastructure, atomic bit operations, `memalloc_nofs_save`/`memalloc_nofs_restore`, XFS log format types, buffer maps, AIL, quota accounting, and trace flag tables. Most XFS metadata subsystems depend on this header to join objects to transactions and log modifications.

The buffer APIs declared here connect transactions with the buffer cache and verifier layer. Inode APIs connect transaction lifetime with inode locks and dirty inode logging. Allocation helpers declared at the end package transaction allocation with quota reservation and locking policies for common VFS-facing operations.

## Risks and Maintenance Notes

- `struct xfs_log_item` is embedded in many item types, so field layout and operation semantics have broad impact on CIL, AIL, recovery, and tracepoint code.
- Any new log item type must supply operations consistent with transaction ordering, pin/unpin lifetime, AIL pushing, and abort release behavior.
- `li_flags` are atomic bit flags; code must use bit helpers rather than unsynchronized plain writes.
- Transaction reservation fields are unsigned and can overflow if replenishment paths do not bound additions; implementation code uses explicit caps for some cases.
- Context helpers save and restore `memalloc_nofs` state; every allocation path that sets the context must clear it exactly once during transaction free.
- Buffer and inode helper ownership semantics are subtle: joined locks are released by commit/cancel, while helper comments define cases where callers remain responsible for unlocks after allocation failures.

## Test Signals

Header-level changes should be validated by full XFS build coverage, sparse/compiler warnings for operation table signature mismatches, runtime tests that exercise each public transaction helper, lockdep tests for inode and buffer join/unlock behavior, tracepoint builds that consume `XFS_LI_FLAGS`, and fault-injection tests around commit/cancel to ensure item release, AIL/CIL state, and reservation fields remain consistent.
