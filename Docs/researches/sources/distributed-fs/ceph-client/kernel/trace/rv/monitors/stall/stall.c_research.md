# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/stall.c

## Purpose

This module implements the standalone `stall` per-task HA monitor that detects tasks remaining enqueued but not running longer than a configurable jiffy threshold.

## Important APIs, Types, and Functions

It uses `RV_MON_PER_TASK`, `HA_TIMER_WHEEL`, generated `stall.h`, `threshold_jiffies` module parameter, HA callbacks for jiffy clock handling, and scheduler switch/wakeup handlers.

## Control Flow

On wakeup from dequeued state or preemption from running state, it resets the jiffy clock. Entering `enqueued` starts a timer for `threshold_jiffies`; leaving enqueued cancels it. `sched_switch` maps blocking switch-out to wait/dequeued and other switch-outs to preempt/enqueued, then marks the next task switch-in. `sched_wakeup` marks a task enqueued.

## State and Persistence Behavior

State is per task in HA storage, with one clock environment `clk`. Timers are armed while a task is enqueued. State is destroyed on disable and has no persistence.

## Dependencies and Integration Points

It depends on scheduler tracepoints, HA monitor helpers, and ID-aware HA trace events. It registers with no parent.

## Risks and Edge Cases

Jiffy resolution means detection precision depends on HZ and timer behavior. The monitor treats all preempted running tasks as enqueued and all non-running non-preempt switch-outs as wait/dequeued, matching scheduler tracepoint semantics but not every scheduling nuance.

## Test Signals

Use runnable task starvation scenarios, vary `threshold_jiffies`, and observe `event_stall`, `error_stall`, and `error_env_stall`.
