# File Research: sources/cow-pools/openzfs/module/zfs/zthr.c

## Purpose

Implements OpenZFS's ZTHR infrastructure: a small lifecycle wrapper for long-lived kernel worker threads that perform SPA-scoped work over multiple transaction groups. A zthr has a caller-provided work checker, a work callback, optional periodic wakeups, cancellation/resume support, and a way for callers to wait until the current callback cycle has ended without destroying the thread object.

The file is intentionally generic but the header comment narrows its intended use: operations should have a persistent in-memory or on-disk indicator of whether work is pending/running, and external threads should only transition that indicator from stopped to running while the zthr itself transitions it back to stopped.

## Main APIs And Entry Points

- Creation: `zthr_create()` creates an event-driven zthr; `zthr_create_timer()` also gives it a maximum sleep interval before it wakes itself and rechecks work.
- Cleanup: `zthr_cancel()` requests stop and blocks until the backing kernel thread exits; `zthr_destroy()` releases the zthr metadata after cancellation.
- Runtime control: `zthr_wakeup()` broadcasts the state condition variable; `zthr_resume()` starts a new kernel thread after a cancellation.
- Callback-side polling: `zthr_iscancelled()` lets the zthr callback notice a pending cancellation; `zthr_has_waiters()` lets it notice that another thread is waiting for the current work cycle to end.
- Introspection/waiting: `zthr_iscurthread()` checks whether the caller is the zthr thread; `zthr_wait_cycle_done()` waits for the current callback invocation to finish without cancelling the thread.
- Internal thread body: `zthr_procedure()` runs the check/sleep/work/cancel state machine and calls `thread_exit()` when cancelled.

## Data Structures

`struct zthr` owns the backing `kthread_t`, a `zthr_state_lock` protecting internal state, a `zthr_request_lock` serializing external cancel/resume requests, the main `zthr_cv`, a `zthr_wait_cv` for cycle waiters, cancellation and waiter flags, optional sleep timeout, thread priority, callback pointers, callback argument, and the stable thread name.

The distinction between `zthr_state_lock` and `zthr_request_lock` is central. External lifecycle requests take the request lock first, then the state lock, which serializes state-changing requests while still allowing condition-variable communication. Wakeups and callback-side polling use only the state lock so they do not block behind a cancellation request or deadlock the running callback.

## Control Flow

Creation allocates and initializes the zthr object, installs callback state while holding `zthr_state_lock`, and starts a named kernel thread at the requested priority. The thread enters `zthr_procedure()`, confirms that `zthr_thread` is the current thread, and loops until `zthr_cancel` becomes true.

Each loop runs the caller's `zthr_checkfunc()` while holding `zthr_state_lock`. If the checker returns true, the lock is dropped and `zthr_func()` is called. When the callback returns, the state lock is reacquired and any `zthr_wait_cycle_done()` waiter is notified. If the checker returns false, the thread sleeps on `zthr_cv`; timer-backed zthrs use `cv_timedwait_idle_hires()`, while non-timer zthrs use `cv_wait_idle()`.

Cancellation sets `zthr_cancel`, wakes the thread if sleeping, and waits for `zthr_thread` to become `NULL`. The zthr clears `zthr_thread`, resets `zthr_cancel` to false, broadcasts `zthr_cv`, drops the state lock, and exits. Resume recreates the named kernel thread only if `zthr_thread` is currently `NULL`.

`zthr_wait_cycle_done()` does not stop the zthr. It sets `zthr_haswaiters`, wakes the thread if needed, and waits until the thread clears that flag after its next callback/check cycle or until the thread is cancelled.

## Dependencies And Integration

This file depends on OpenZFS/SPL kernel primitives from `sys/zfs_context.h` and the public zthr declarations in `sys/zthr.h`: mutexes, condition variables, `thread_create_named()`, `thread_exit()`, idle waits, assertions, allocation, and thread priority types. It is used by SPA-level components that need a cancelable, resumable background worker rather than a generic taskq item.

## Risks And Invariants

- `zthr_destroy()` requires the backing thread to already be cancelled; it verifies `zthr_thread == NULL` before destroying locks and condition variables.
- `zthr_checkfunc()` runs under `zthr_state_lock`; callback implementations must not assume they can block there like they can in `zthr_func()`.
- `zthr_func()` must poll `zthr_iscancelled()` or `zthr_has_waiters()` itself if long operations need low-latency cancellation or cycle-wait completion.
- `zthr_iscancelled()` and `zthr_has_waiters()` assert they are called by the zthr thread and deliberately avoid `zthr_request_lock` to prevent deadlock with `zthr_cancel()`.
- Wakeups are level-triggered through the caller's work indicator, not edge-triggered by the condition variable; check functions must tolerate spurious wakeups.
- Timer wakeups only cause the checker to run; they do not imply that work exists.

## Summary

`zthr.c` provides the small but important background-thread state machine used by OpenZFS subsystems for SPA-lifetime work. Its main contribution is disciplined cancellation/resume semantics around caller-owned work indicators and callback code that may span multiple transaction groups.
