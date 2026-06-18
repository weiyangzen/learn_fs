# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/sssw_trace.h

## Purpose

This header defines ID-aware DA tracepoint instances for `sssw`.

## Important APIs, Types, and Functions

It instantiates `event_sssw` and `error_sssw` under `CONFIG_RV_MON_SSSW`.

## Control Flow

Included by `rv_trace.h`, it exposes per-task transition and error tracing.

## State and Persistence Behavior

No mutable state is stored.

## Dependencies and Integration Points

It depends on generic ID-aware DA event classes.

## Risks and Edge Cases

Consumers must account for PID reuse and task lifetime when interpreting IDs.

## Test Signals

Enable `sssw` and verify task IDs appear in transition/error records.
