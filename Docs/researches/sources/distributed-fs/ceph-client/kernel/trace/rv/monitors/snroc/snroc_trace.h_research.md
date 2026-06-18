# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/snroc_trace.h

## Purpose

This header defines ID-aware DA tracepoints for `snroc`.

## Important APIs, Types, and Functions

It instantiates `event_snroc` and `error_snroc` under `CONFIG_RV_MON_SNROC`.

## Control Flow

Included by `rv_trace.h`, it exposes task-ID transition and error records.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

It depends on `event_da_monitor_id` and `error_da_monitor_id`.

## Risks and Edge Cases

PID reuse can affect long trace interpretation.

## Test Signals

Inspect tracefs events and ensure records include the task ID.
