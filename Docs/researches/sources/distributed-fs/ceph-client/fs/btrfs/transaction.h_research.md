# sources/distributed-fs/ceph-client/fs/btrfs/transaction.h

## Purpose
`transaction.h` defines the public transaction data structures, state enum, transaction type flags, abort macro, inline helpers, and exported function prototypes for Btrfs transaction management. It is the contract between transaction implementation and the rest of the filesystem.

## Important APIs, Types, And Functions
`enum btrfs_trans_state` names the commit lifecycle: running, commit prep, commit start, commit doing, unblocked, super committed, completed, and max. `struct btrfs_transaction` holds the global transaction object with transid, writer counts, use count, flags, state, abort code, dirty trees, pending snapshot and device update lists, dirty and IO block group lists, dropped/deleted roots, pinned extents, delayed refs, fs info, and ordered-extents wait state.

`struct btrfs_trans_handle` is the per-task handle with reservation accounting, delayed-ref counters, pointer to the transaction, block reservation pointers, pending snapshot pointer, type, abort field, flags for csum/chunk/relocation/fsync operations, `fs_info`, new block groups, local delayed-ref reservation, and a writeback-inhibited extent-buffer xarray.

`struct btrfs_pending_snapshot` captures all state needed to create a snapshot at commit time: dentry, parent inode, source root, root item, resulting snapshot root, qgroup inheritance, path, block reservation, error, anonymous device id, readonly flag, and list node.

Inline helpers include `btrfs_set_inode_last_trans()`, `btrfs_set_skip_qgroup()`, `btrfs_clear_skip_qgroup()`, and `btrfs_abort_should_print_stack()`. The `btrfs_abort_transaction()` macro records first-abort diagnostics and calls `__btrfs_abort_transaction()`.

## Control Flow
Callers start or join transactions through the declared start/join/attach helpers, modify Btrfs trees under a returned handle, then end or commit through `btrfs_end_transaction()`, `btrfs_end_transaction_throttle()`, or `btrfs_commit_transaction()`. Snapshot callers populate `pending_snapshot` and commit moves it to the transaction list once commit prep starts. Abort callers use the macro, which sets filesystem-level abort state on first hit, decides whether to print a stack based on errno, logs the abort, and delegates to the cold implementation.

## State And Persistence Behavior
The header describes how transaction state controls persistence. `num_extwriters` must reach zero before commit can proceed into the exclusive phase, while `num_writers` must reach zero except for the committer. Dirty pages and pinned extents track metadata that must be written or finalized. `pending_ordered` represents fast-fsync ordered extents that commit must wait on to preserve logged data. The qgroup skip helper mutates delayed-ref root state so snapshot qgroup accounting can omit a newly created qgroup until inheritance accounts it.

## Dependencies And Integration Points
The header depends on Linux atomics, refcounts, lists, waits, mutexes, xarrays, and Btrfs inode and delayed-ref definitions. Its prototypes are used by tree modification code, root management, qgroups, block groups, transaction kthread code, scrub/relocation, fsync/log code, and selftests.

## Risks And Edge Cases
The `aborted` fields are intentionally lockless and must be read with `READ_ONCE()` through `TRANS_ABORTED()`. Transaction type flags are bit encodings used by `transaction.c` state gating, so adding a type requires updating blocked-state logic. The abort macro can print a stack only for errors likely to indicate bugs, while common external failures such as `-EIO`, `-EROFS`, and `-ENOMEM` avoid noisy warnings.

## Test Signals
The header itself is not tested directly, but compile-time and selftest coverage validates structure fields and prototypes. Many Btrfs tests create dummy `struct btrfs_trans_handle` values through `btrfs_init_dummy_trans()` and rely on these definitions for qgroup, raid stripe tree, and tree mutation tests.
