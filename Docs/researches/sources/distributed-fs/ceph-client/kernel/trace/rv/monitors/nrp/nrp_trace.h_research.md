# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/nrp_trace.h

## Purpose

This file defines `nrp` tracepoint instances for ID-aware DA monitor events.

## Important APIs, Types, and Functions

It instantiates `event_nrp` and `error_nrp` when `CONFIG_RV_MON_NRP` is enabled.

## Control Flow

Included by `rv_trace.h`, it binds the generic `event_da_monitor_id` and `error_da_monitor_id` classes to monitor-specific tracepoint names.

## State and Persistence Behavior

There is no runtime state; the output schema carries task ID, state, event, next state, and final-state status.

## Dependencies and Integration Points

It depends on `CONFIG_DA_MON_EVENTS_ID` and the event classes declared in `rv_trace.h`.

## Risks and Edge Cases

If the trace header is not included under the matching config block, the monitor can still run but will lack expected user-visible transition/error tracepoints.

## Test Signals

Inspect RV trace events after building with `RV_MON_NRP`, and trigger a known invalid path to observe `error_nrp`.
