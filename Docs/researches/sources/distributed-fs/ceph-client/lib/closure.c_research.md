# sources/distributed-fs/ceph-client/lib/closure.c

## Purpose

`sources/distributed-fs/ceph-client/lib/closure.c` implements asynchronous closure refcounting and wait-list coordination used by bcache-style asynchronous flows. It combines reference accounting, continuation scheduling, synchronous waits, and optional debug tracking.

## Important APIs, Types, and Functions

Exports include `closure_sub`, `closure_put`, `__closure_wake_up`, `closure_wait`, `__closure_sync`, `closure_return_sync`, `__closure_sync_timeout`, and under `CONFIG_DEBUG_CLOSURES`, `closure_debug_create` and `closure_debug_destroy`. Internal helpers include `closure_put_after_sub_checks`, `closure_put_after_sub`, `closure_sync_fn`, and debugfs `debug_show`.

## Control Flow

Ref drops use release atomics and then validate guard bits and remaining flags. When remaining references reach zero, the closure either queues its continuation function, runs its destructor, and/or drops its parent reference. `closure_wait()` adds a closure to a lockless waitlist, setting waiting bits and taking an extra reference. `__closure_wake_up()` drains and reverses the llist to preserve FIFO order, clears waiting state, and drops wait references. Synchronous waits install `closure_sync_fn` as the continuation and sleep uninterruptibly until the callback marks completion and wakes the task; timeout handling attempts to undo the continuation if it has not completed.

## State and Persistence Behavior

Persistent state is in caller-owned `struct closure`: atomic `remaining` flags, parent pointer, function pointer, work item, wait-list node, syncer pointer, and debug fields. Debug mode tracks live closures in a global list protected by `closure_list_lock` and exposes them through debugfs.

## Dependencies and Integration Points

The file depends on `linux/closure.h`, workqueue callback conventions, atomics, llist, scheduler sleep/wakeup, RCU in the sync callback, debugfs, and seq_file. It integrates with asynchronous subsystems that model completion dependencies with closures.

## Risks and Edge Cases

The remaining field packs refcount and flags, so incorrect flag arithmetic can queue, destroy, or wait forever. Timeout undo in `__closure_sync_timeout()` races the final put and must only restore the initializer when safe. Parent closure puts must happen exactly once. Debug tracking depends on correct create/destroy calls and magic values.

## Test Signals

Tests should cover continuation queueing after final put, destructor path, parent release, multiple waiters woken FIFO, synchronous wait and timeout, closure return without reinitializing refs, debugfs live closure reporting, and warnings for guard bits or bad zero-ref flags.

## Read Coverage

Source read size: 297 lines, 6914 bytes.
