# sources/distributed-fs/ceph-client/fs/jffs2/background.c

## Purpose
`background.c` owns the JFFS2 garbage-collection daemon thread. It starts and stops the per-MTD GC kthread, wakes it when eraseblock state requires work, handles freezer and signal interactions, and repeatedly invokes `jffs2_garbage_collect_pass()` while throttling itself to reduce boot-time/user-space starvation.

## Important APIs and functions
The external functions are `jffs2_garbage_collect_trigger()`, `jffs2_start_garbage_collect_thread()`, and `jffs2_stop_garbage_collect_thread()`. The internal thread body is `jffs2_garbage_collect_thread()`. State is stored in `struct jffs2_sb_info`: `gc_task`, `gc_thread_start`, `gc_thread_exit`, `erase_completion_lock`, and the MTD index used in the thread name.

## Control flow
`jffs2_start_garbage_collect_thread()` asserts no existing GC task, initializes start/exit completions, starts `jffs2_garbage_collect_thread()` with `kthread_run()`, waits until the thread publishes `c->gc_task`, and returns the PID or an error. `jffs2_stop_garbage_collect_thread()` takes `erase_completion_lock`, sends `SIGKILL` to the GC task if present, drops the lock, and waits for `gc_thread_exit`.

`jffs2_garbage_collect_trigger()` must be called with `erase_completion_lock` held. If a GC task exists and `jffs2_thread_should_wake(c)` is true, it sends `SIGHUP` to wake the thread.

The thread allows `SIGKILL`, `SIGSTOP`, and `SIGHUP`, publishes `gc_task`, lowers priority with nice value 10, and marks itself freezable. In its loop it unblocks SIGHUP, sleeps when `jffs2_thread_should_wake()` is false, delays 50 ms to avoid starving user-space after boot, handles freezer and pending signals, blocks SIGHUP while doing work, and calls `jffs2_garbage_collect_pass()`. `-ENOSPC` from a GC pass logs a notice and terminates the thread. On exit it clears `gc_task` under the erase lock and completes the exit completion.

## State and persistence behavior
This file does not directly persist flash data; persistence happens inside `jffs2_garbage_collect_pass()` and erase/write paths. Its state controls whether background GC runs and whether mount/unmount can safely wait for the daemon. Signal handling is used as an in-kernel wake/stop mechanism rather than user-visible process control.

## Dependencies and integration points
It depends on `nodelist.h` for JFFS2 internal state and `jffs2_thread_should_wake()`/`jffs2_garbage_collect_pass()`, on MTD for device naming, on kthreads, completions, freezer support, and kernel signal helpers. Mount/superblock code starts and stops this thread; erase completion paths trigger it when dirty/free-space thresholds require collection.

## Risks and edge cases
The start function must only be called when no GC thread exists; it uses `BUG_ON(c->gc_task)`. Stop relies on the thread processing `SIGKILL`; if the thread blocks in lower layers, unmount waits. The trigger requires the erase-completion spinlock and can race with exit unless `gc_task` is protected consistently. The deliberate 50 ms throttle improves interactivity but can delay reclaim under tight free-space pressure. `-ENOSPC` terminates background GC, which can leave the filesystem relying on foreground operations or remount/error handling.

## Test signals
Test thread start/stop on mount/unmount, trigger wakeups under the erase lock, freezer suspend/resume, SIGSTOP/SIGKILL/SIGHUP handling, no-work sleep and wake behavior, GC pass `-ENOSPC` termination, repeated start/stop cycles, and races between trigger and stop.
