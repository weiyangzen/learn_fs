# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/sco_trace.h

## Purpose

This trace header defines implicit DA event instances for `sco`.

## Important APIs, Types, and Functions

It instantiates `event_sco` and `error_sco` under `CONFIG_RV_MON_SCO`.

## Control Flow

Included by `rv_trace.h`, it maps generic no-ID DA trace classes to monitor-specific tracepoints.

## State and Persistence Behavior

No runtime state is stored.

## Dependencies and Integration Points

It depends on `event_da_monitor` and `error_da_monitor`.

## Risks and Edge Cases

No explicit CPU field is included; consumers rely on trace metadata for CPU context.

## Test Signals

Inspect RV trace events and trigger an invalid state-set-in-scheduler path if possible.
