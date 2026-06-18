# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-transaction.h

## Purpose
`afr-transaction.h` is the public interface for AFR transaction and read-transaction support. It exposes the write transaction state machine in `afr-transaction.c`, the read transaction helpers implemented with the same transaction vocabulary, quorum helpers, delayed changelog callbacks, thin-arbiter lock-release callbacks, and small utility functions used by the rest of the AFR translator.

## Important APIs, Types, And Functions
The central declaration is `afr_transaction(call_frame_t *frame, xlator_t *this, afr_transaction_type type)`, paired with `afr_transaction_resume()` and `afr_transaction_detach_fop_frame()`. FOP implementations report child failure with `afr_transaction_fop_failed()` and may trigger locking directly through `afr_lock()`. Changelog and quorum helpers include `afr_set_pending_dict()`, `afr_txn_nothing_failed()`, `afr_has_quorum()`, `afr_needs_changelog_update()`, `afr_zero_fill_stat()`, and `afr_pick_error_xdata()`.

Read-side declarations include `afr_read_txn()`, `afr_read_txn_continue()`, `afr_pending_read_increment()`, and `afr_pending_read_decrement()`, which integrate read selection and outstanding-read load tracking with the shared AFR private state. Thin-arbiter exported callbacks are `afr_release_notify_lock_for_ta()` and `afr_ta_lock_release_done()`. `__mark_all_success()` is intentionally exposed for shared symmetric-error handling.

## Control Flow
The header is included by FOP implementation files that initialize `afr_local_t`, set transaction wind/unwind callbacks, and call the transaction engine. Write FOP callbacks use `afr_transaction_fop_failed()` before unwinding to `afr_transaction_resume()`. Read FOP paths use `afr_read_txn()` to select a readable child, wind the caller-provided read function, and continue to other candidates through `afr_read_txn_continue()` when a read fails.

## State And Persistence
This header does not define storage by itself, but every declaration operates on `afr_private_t`, `afr_local_t`, `call_frame_t`, and inode/fd state declared in `afr.h`. The APIs coordinate persistent on-disk xattrs through `dict_t` objects and expose quorum decisions based on caller-provided child-bit arrays. Pending read counters are held in `afr_private_t::pending_reads`, while delayed changelog wakeups and transaction frame detachment operate on `afr_inode_ctx_t` and `afr_local_t` lock/timer state.

## Dependencies And Integration Points
The header depends on `afr.h`, which provides transaction types, local/private structures, callback typedefs, and GlusterFS core types. It is part of the AFR internal module boundary: inode-write, dir-write, open/fsync/xattrop paths, self-heal, and read transaction code all depend on these declarations rather than duplicating transaction internals.

## Risks
Because this header exposes low-level state-machine hooks, misuse can corrupt transaction accounting. Calling `afr_transaction_resume()` without restoring proper `op_ret`, `op_errno`, and child failure bits can produce wrong post-op xattrs. Incorrect child arrays passed to `afr_has_quorum()` can grant unsafe writes. Direct use of `__mark_all_success()` must remain limited to verified symmetric-error cases, otherwise real failures would be hidden. Thin-arbiter callback signatures also rely on frame ownership conventions: destroying or reusing frames too early can break wait queue processing.

## Test Signals
Compilation across all AFR FOP modules is the first signal because this file is a shared internal ABI. Behavioral tests should cover all transaction types, read retry/load counters, explicit child failure reporting, quorum helper outcomes for even/odd replica counts, delayed changelog wakeup, and thin-arbiter notify-lock release. Header changes should trigger broad AFR regression tests because seemingly small signature or semantic changes affect most read/write paths.
