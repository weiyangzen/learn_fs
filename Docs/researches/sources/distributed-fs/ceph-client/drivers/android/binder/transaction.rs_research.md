# sources/distributed-fs/ceph-client/drivers/android/binder/transaction.rs

## Purpose
`transaction.rs` implements the Rust Binder `Transaction` work item and `TransactionInfo` metadata. It owns copied target-process allocations until userspace receives them, manages outstanding transaction accounting, selects target delivery queues, supports oneway transaction replacement, prepares translated file descriptors, and emits reply/error behavior on cancellation or delivery failure.

## Important APIs, Types, And Functions
`TransactionInfo` stores from/to pids and tids, code, flags, source data/offset pointers, sizes, target handle, reply errno/code, spam and reply flags. `Transaction` stores debug ID, target node, caller stack parent, sender thread, target process, allocation, outstanding flag, code/flags/sizes, sender euid, optional security-context offset, and start time. Key methods are `new`, `new_reply`, `submit`, `can_replace`, `is_stacked_on`, `clone_next`, `find_target_thread`, `find_from`, `set_outstanding`, `drop_outstanding_txn`, `prepare_file_list`, and `debug_print_inner`. The `DeliverToRead` implementation provides `do_work`, `cancel`, `should_sync_wakeup`, and `debug_print`.

## Control Flow
Constructors call `Thread::copy_transaction_data` to create an allocation in the target process, then annotate allocation metadata for target node, oneway node, clear-on-drop, or security context. `submit` locks the target process, marks the transaction outstanding, handles frozen-process behavior, routes oneway transactions through the target node async queue, or sends sync work to a thread found in the existing transaction stack or to the process queue. `do_work` prepares translated fd lists, fills `binder_transaction_data` or `binder_transaction_data_secctx`, writes the return code and payload to userspace, commits fds, keeps the allocation alive for userspace free, clears outstanding accounting, traces receipt, and updates the recipient thread's current transaction for sync calls.

## State And Persistence
The transaction persists as a refcounted work item until delivered, canceled, or dropped. Its allocation is protected by a spinlock and is taken exactly once for fd translation and userspace handoff; after `keep_alive`, userspace owns the buffer lifetime through Binder free-buffer commands. `is_outstanding` is an atomic guard ensuring target-process outstanding counts are decremented once. `from_parent` preserves transaction-stack ancestry for nested sync calls.

## Dependencies
The file depends on allocation and fd translation types, Binder flags/return constants, `Node` and `NodeRef`, `Process`, `Thread`, Binder security credentials, seq_file debugging, kernel atomics/time/task uid APIs, and the crate tracing layer. It also exports `TRANSACTION_LAYOUT` with field offsets for C/Rust trace integration.

## Integration Points
`Thread` creates and delivers transactions; `Process` queues work and tracks outstanding transactions; `Node` owns oneway queues and update-transaction replacement; allocation code translates fds and tracks buffer cleanup; tracing observes send/receive latency and metadata. Frozen process handling sets `sync_recv` or `async_recv` and returns Binder frozen errors.

## Risks
Error paths are subtle: delivery failures must send `BR_FAILED_REPLY` or `BR_DEAD_REPLY` without leaking allocations or double-dropping outstanding counts. Oneway replacement requires exact matching on sender pid, code, flags, and target node to avoid dropping semantically distinct work. File descriptor preparation happens just before userspace delivery; failures intentionally notify the sender and skip target delivery. The Rust/C transaction trace layout must stay synchronized with this struct.

## Test Signals
Test sync calls, replies, oneway calls, update transactions, frozen targets, dead-thread reply unwinding, fd transfer success/failure, `TF_CLEAR_BUF`, `FLAT_BINDER_FLAG_TXN_SECURITY_CTX`, oneway spam reporting, debugfs transaction output, outstanding transaction counts during freeze waits, and tracepoint transaction metadata.
