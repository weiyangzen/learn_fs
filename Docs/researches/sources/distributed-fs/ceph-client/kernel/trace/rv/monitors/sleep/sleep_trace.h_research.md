# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/sleep_trace.h

## Purpose

This header defines tracepoint instances for the `sleep` LTL monitor.

## Important APIs, Types, and Functions

It instantiates `event_sleep` and `error_sleep` under `CONFIG_RV_MON_SLEEP`.

## Control Flow

Included by `rv_trace.h` under `CONFIG_LTL_MON_EVENTS_ID`, it binds generic LTL event/error classes to monitor-specific names.

## State and Persistence Behavior

No mutable state is stored here.

## Dependencies and Integration Points

It depends on the LTL ID event classes and the `sleep` monitor's atom/state string generation.

## Risks and Edge Cases

Task PID reuse can make long trace captures ambiguous without timestamps and task lifetime context.

## Test Signals

Enable the monitor, inspect tracefs event availability, and trigger a known violation to observe `error_sleep`.
