# sources/distributed-fs/glusterfs/libglusterfs/src/timer.c

## Purpose

`timer.c` implements Gluster's context-wide timer registry. It lets callers schedule callbacks after a monotonic delta, cancel pending callbacks, lazily starts a timer thread per context, and drains outstanding timers during registry destruction.

## Important APIs, Types, and Functions

The public API is `gf_timer_call_after()`, `gf_timer_call_cancel()`, and `gf_timer_registry_destroy()`. Internal functions are `gf_timer_registry_init()` and `gf_timer_proc()`. `gf_timer_registry_t` owns a mutex, condition variable using `CLOCK_MONOTONIC`, active timer list, worker thread, and finish flag. `gf_timer_t` stores scheduled time, callback, data, translator `THIS` pointer, fired flag, and list link.

## Control Flow and Data Flow

Scheduling validates the context, lazily initializes the registry under `ctx->lock`, allocates an event, computes `event->at` from `timespec_now()` plus the delta, records callback/data/current translator, and inserts the event into the active list ordered by deadline. If the new event becomes the earliest one, it signals the timer thread. The timer thread waits while the list is empty, timed-waits until the earliest deadline, marks due events fired, removes them from the list, temporarily restores the scheduling translator as `THIS`, invokes the callback outside the registry lock, frees the event, and resumes waiting.

Cancellation fetches `ctx->timer`, locks the registry, checks whether the event already fired, removes and frees it if not fired, and returns failure if fired or registry is gone. Destroy clears `ctx->timer`, sets `fin`, wakes and joins the timer thread, frees any remaining active events without invoking callbacks, destroys synchronization primitives, and frees the registry.

## State and Persistence Behavior

Timer state is volatile and per `glusterfs_ctx_t`. Scheduled callbacks can mutate any caller-owned state but no state is persisted by the timer module itself. Destroy intentionally drops pending callbacks and comments about possible resource leaks when callbacks would have released resources.

## Dependencies and Integration Points

The file depends on Gluster global `THIS`, logging, context locks, `timespec.c`, list primitives, pthreads, and `gf_thread_create()`. It integrates with `syncop.c` for synctask sleep/timeouts and with RPC reconnect or other delayed work users.

## Risks and Edge Cases

Cancellation races with firing are expected; once `fired` is set, cancellation fails and the callback owns cleanup. Destroying the registry frees pending events without running callbacks, so callers that attach references to timer callbacks can leak unless they handle context cleanup elsewhere. Insert ordering uses `TS()` comparisons and reverse traversal; ordering bugs can delay callbacks. Registry initialization sets `ctx->timer` before thread creation succeeds, so failed thread creation leaves a registry pointer that cannot service timers.

## Test Signals

Tests should schedule single and multiple timers, verify deadline order, cancel before fire, cancel after fire, schedule from different translators and verify `THIS`, destroy with pending timers, race cancellation against callback execution, and fault-inject thread creation failure.
