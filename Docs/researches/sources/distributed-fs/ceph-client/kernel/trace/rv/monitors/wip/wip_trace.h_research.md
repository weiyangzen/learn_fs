# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/wip_trace.h

## Purpose

This header defines implicit DA tracepoints for `wip`.

## Important APIs, Types, and Functions

It instantiates `event_wip` and `error_wip` under `CONFIG_RV_MON_WIP`.

## Control Flow

Included by `rv_trace.h`, it binds generic implicit DA trace classes to the sample monitor.

## State and Persistence Behavior

No mutable state is stored.

## Dependencies and Integration Points

It depends on generic no-ID DA event classes.

## Risks and Edge Cases

CPU identity is implicit in standard trace metadata.

## Test Signals

Verify trace event availability and record formatting during wakeup/preempt events.
