# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/sts_trace.h

## Purpose

This header defines implicit DA tracepoints for `sts`.

## Important APIs, Types, and Functions

It instantiates `event_sts` and `error_sts` under `CONFIG_RV_MON_STS`.

## Control Flow

Included by `rv_trace.h`, it exposes scheduler/task-switch monitor transitions and errors.

## State and Persistence Behavior

No runtime state is held in this header.

## Dependencies and Integration Points

It depends on generic implicit DA trace classes.

## Risks and Edge Cases

Per-CPU identity comes from tracing metadata rather than an explicit trace field.

## Test Signals

Verify event availability and emitted transitions under scheduler activity.
