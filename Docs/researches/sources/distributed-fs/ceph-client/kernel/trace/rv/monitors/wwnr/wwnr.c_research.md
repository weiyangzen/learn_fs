# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/wwnr.c

## Purpose

This module implements the standalone `wwnr` per-task sample monitor for wakeup while not running. The model is intentionally flawed to exercise RV reactors.

## Important APIs, Types, and Functions

It uses generated `wwnr.h`, `rv/da_monitor.h`, `handle_switch()`, `handle_wakeup()`, and standard RV lifecycle registration.

## Control Flow

On enable, it initializes DA storage and attaches `sched_switch` and `sched_wakeup`. Switch-out starts monitoring only after the first interruptible suspension; other switch-outs are normal events. Switch-in moves a task to running, and wakeup emits a wakeup event for the target task.

## State and Persistence Behavior

State is per task in DA storage. It is reset by `da_monitor_reset_all` and destroyed on disable.

## Dependencies and Integration Points

It depends on scheduler tracepoints, ID-aware DA events, and RV core registration. It has no parent container.

## Risks and Edge Cases

Because the model is deliberately broken, errors are expected and useful for reactor testing. Starting only after interruptible suspension means early task history is ignored.

## Test Signals

Enable with `printk` or `panic` reactors in controlled environments, run sleep/wakeup workloads, and observe `event_wwnr`/`error_wwnr`.
