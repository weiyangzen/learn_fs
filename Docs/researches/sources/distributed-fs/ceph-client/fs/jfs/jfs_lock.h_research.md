# sources/distributed-fs/ceph-client/fs/jfs/jfs_lock.h

Purpose: provides a JFS-specific conditional sleep macro for wait queues protected by caller-supplied spinlock operations.

Important APIs and types: defines `__SLEEP_COND(wq, cond, lock_cmd, unlock_cmd)`. It includes Linux spinlock, mutex, and scheduler headers.

Control flow: the macro adds the current task to a wait queue, repeatedly sets `TASK_UNINTERRUPTIBLE`, checks the condition while the caller's lock is held, releases the lock and calls `io_schedule` if the condition is false, then reacquires the lock and retries. On success it restores `TASK_RUNNING` and removes the wait entry.

State and persistence behavior: runtime-only synchronization helper; it has no persistent on-disk state. It affects task state, wait queue membership, and lock ownership during I/O-oriented waits.

Dependencies and integration: intended for JFS code that needs to sleep until a lock-protected condition changes without open-coding waitqueue boilerplate. It depends on callers passing correct lock/unlock expressions and a condition safe to test under that lock.

Risks and edge cases: the wait is uninterruptible, so callers must ensure the condition will eventually become true. Mispaired lock commands can deadlock or sleep while still holding a spinlock. Because the macro evaluates caller-provided expressions, side effects in `cond`, `lock_cmd`, or `unlock_cmd` can be dangerous.

Test signals: lockdep coverage, I/O wait paths that use this macro, stress under contention, and shutdown/error paths that must wake blocked tasks.
