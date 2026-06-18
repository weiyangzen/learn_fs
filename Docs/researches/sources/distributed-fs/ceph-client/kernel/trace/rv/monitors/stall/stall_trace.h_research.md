# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/stall_trace.h

## Purpose

This header defines ID-aware HA tracepoints for the `stall` monitor.

## Important APIs, Types, and Functions

It instantiates `event_stall`, `error_stall`, and `error_env_stall` under `CONFIG_RV_MON_STALL`.

## Control Flow

Included by `rv_trace.h`, it exposes transition, invalid event, and environment/timer violation records.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

It depends on ID-aware DA/HA event classes.

## Risks and Edge Cases

Trace interpretation requires correlating task IDs with scheduler events and threshold settings.

## Test Signals

Force an enqueued task past the threshold and verify the environment error tracepoint.
