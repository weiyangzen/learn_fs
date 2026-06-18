# sources/distributed-fs/ceph-client/fs/dlm/plock.c

## Purpose
`plock.c` delegates distributed POSIX byte-range lock coordination to userspace through the DLM plock misc device while maintaining local VFS lock bookkeeping. It exports kernel helpers used by cluster filesystems for POSIX lock, unlock, cancel, and get operations.

## Important APIs, Types, And Functions
Important exports are `dlm_posix_lock()`, `dlm_posix_unlock()`, `dlm_posix_cancel()`, `dlm_posix_get()`, `dlm_plock_init()`, and `dlm_plock_exit()`. Internal state uses `struct plock_op` and optional `struct plock_async_data`. Device operations are `dev_read()`, `dev_write()`, and `dev_poll()` on `DLM_PLOCK_MISC_NAME`.

## Control Flow
Kernel lock requests build a `dlm_plock_info`, enqueue it on `send_list`, and wake the userspace daemon. `dev_read()` moves most requests from `send_list` to `recv_list` and copies them to userspace; close-generated unlocks do not require replies and are freed after read. `dev_write()` copies a result back, matches it to a waiting operation, updates the op, and either wakes a synchronous waiter or invokes an async callback.

`dlm_posix_lock()` supports blocking, nonblocking, and async locks. Blocking waits can be interrupted; interruption sends a cancel op and either removes the original waiter or waits for completion. Successful locks are also installed in local VFS lock state. `dlm_posix_unlock()` removes local VFS lock state first, sends a distributed unlock, and treats `-ENOENT` as success. `dlm_posix_cancel()` currently supports async requests and either removes the pending op or falls back to unlock if userspace was too late. `dlm_posix_get()` asks userspace for conflicting lock info and maps remote pids to negative values.

## State And Persistence
Global in-memory state consists of `send_list`, `recv_list`, waitqueues, and `ops_lock`. State exists only while the module is loaded. Individual operations persist until userspace reads and replies, close-generated unlocks are read, or cancellation removes them.

## Dependencies And Integration Points
This file integrates with Linux file-lock APIs (`locks_lock_file_wait`, `posix_lock_file`), the misc device framework, DLM lockspace lookup, `linux/dlm_plock.h` wire structs, and userspace daemon compatibility via version fields.

## Risks
The correctness of distributed POSIX locks depends on a responsive userspace plock daemon. Async callback paths intentionally ignore some local VFS bookkeeping failures, which can leave distributed state authoritative but local state imperfect. Cancellation matching requires exact field comparisons and can be racy around userspace completion. Lists must be empty on module exit.

## Test Signals
Test blocking interruption, async NFS-style callbacks, cancel-before-grant and cancel-after-grant, close-generated unlocks, version mismatch rejection, daemon restart behavior, and local VFS lock state after distributed grants/unlocks.
