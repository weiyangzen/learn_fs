# sources/distributed-fs/ceph-client/block/blk-pm.c

## Purpose

`blk-pm.c` implements request-based runtime power-management support for block queues. It lets drivers bind a queue to a `struct device`, coordinate runtime suspend with queue usage references, and restore queue access on resume. It is only useful for request-based drivers, not bio-only drivers.

## Important APIs, Types, And Functions

`blk_pm_runtime_init()` stores `q->dev`, marks the queue runtime-PM state active, sets autosuspend delay to `-1`, and enables autosuspend semantics. `blk_pre_runtime_suspend()` transitions the queue to suspending, sets PM-only mode, freezes the queue usage counter, switches it to atomic mode, and allows suspend only if the usage counter reaches zero. `blk_post_runtime_suspend()` finalizes `RPM_SUSPENDED` on success or restores active state and clears PM-only mode on failure. `blk_pre_runtime_resume()` marks `RPM_RESUMING`. `blk_post_runtime_resume()` marks active, updates last busy time, requests autosuspend, and clears PM-only mode if the old state was not active.

## Control Flow

A driver initializes runtime PM after queue allocation but before normal I/O can race with runtime PM. During runtime suspend, the driver calls `blk_pre_runtime_suspend()` near the start of its suspend callback. That function blocks new non-PM queue entrants by setting PM-only, then freezes queue entry and synchronously switches `q_usage_counter` to atomic mode so new entrants observe the PM-only state. If the counter is zero, suspend can proceed; otherwise it restores active state, marks the device busy, clears PM-only, and returns `-EBUSY`. After the device-level suspend callback, the driver calls `blk_post_runtime_suspend()` with the callback result. Runtime resume uses the pre/post pair to mark the transient state and then reopen normal queue entry.

## State And Persistence Behavior

The file updates in-memory queue fields: `q->dev`, `q->rpm_status`, PM-only queue state, and the queue usage percpu ref mode. It also updates runtime-PM state in the device core through `pm_runtime_*()` calls. There is no durable persistence. Locking is through `q->queue_lock`, freeze/unfreeze functions, and percpu ref synchronization.

## Dependencies And Integration Points

It includes `<linux/pm_runtime.h>`, `<linux/blk-pm.h>`, block queue definitions, and `blk-mq.h`. It integrates with `blk_queue_enter()` PM behavior, queue freeze/unfreeze, runtime-PM autosuspend, and the driver runtime suspend/resume callbacks. `blk-pm.h` provides inline fast-path helpers used by request allocation/free paths.

## Risks And Edge Cases

The suspend path is sensitive to ordering. PM-only must be set before checking for in-flight non-PM users, and the q_usage_counter must switch to atomic mode so later entrants observe the state. A failed suspend must clear PM-only or normal I/O can remain blocked. `q->dev == NULL` is treated as no-op support. Drivers must call the post hooks consistently; otherwise `rpm_status` and PM-only state can remain stale. Runtime resume always clears PM-only for non-active old states even if hardware resume failed, because error handling still needs device communication.

## Test Signals

Relevant tests include runtime suspend while I/O is idle, suspend rejection with active I/O, PM requests allowed while PM-only is set, resume after successful and failed suspend, lockdep for queue_lock/freeze ordering, and driver tests that ensure no I/O is admitted after `blk_pre_runtime_suspend()` succeeds.
