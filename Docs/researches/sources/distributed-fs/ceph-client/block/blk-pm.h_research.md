# sources/distributed-fs/ceph-client/block/blk-pm.h

## Purpose

`blk-pm.h` provides small inline helpers for the block runtime-PM fast path. It keeps PM checks cheap in blk-mq paths while compiling to no-ops when `CONFIG_PM` is disabled.

## Important APIs, Types, And Functions

With `CONFIG_PM`, `blk_pm_resume_queue(pm, q)` decides whether queue entry may proceed or should request runtime resume. If the queue has no runtime-PM device or is not PM-only, it returns `1`. If the caller is a PM request and the queue is not suspended, it returns `1`. Otherwise it calls `pm_request_resume(q->dev)` and returns `0` to indicate that the current queue-enter attempt should not proceed. `blk_pm_mark_last_busy(rq)` marks the device busy after non-PM request completion. Without `CONFIG_PM`, both helpers compile to simple allow/no-op implementations.

## Control Flow

Queue entry code can call `blk_pm_resume_queue()` after detecting PM-only state. A non-PM request against a suspended queue triggers an async resume request rather than entering the queue. A PM-marked request is allowed when the queue is already resuming or active, which avoids blocking the PM machinery itself. Request free/completion paths call `blk_pm_mark_last_busy()` so autosuspend timing is based on normal I/O activity.

## State And Persistence Behavior

The helper reads `q->dev`, queue PM-only state, request `RQF_PM`, and `q->rpm_status`; it updates runtime-PM last-busy state through the device core. No persistent state is stored in this header.

## Dependencies And Integration Points

It depends on `<linux/pm_runtime.h>` and block queue/request fields defined elsewhere. It is coupled to `blk-pm.c` state transitions and blk-mq request free paths.

## Risks And Edge Cases

The return convention is easy to misuse: `1` means request allowed or nothing to do, while `0` means resume was requested and queue entry should be retried later. Marking last busy must skip `RQF_PM` requests; otherwise PM-internal traffic can keep devices awake indefinitely. Non-PM builds must retain identical call-site behavior through no-op helpers.

## Test Signals

Compile with and without `CONFIG_PM`, runtime-PM suspend/resume queue-entry tests, and autosuspend timing after normal I/O completions are the primary checks.
