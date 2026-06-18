# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/scpd_trace.h

## Purpose

This header defines tracepoint instances for the `scpd` implicit DA monitor.

## Important APIs, Types, and Functions

It instantiates `event_scpd` and `error_scpd` under `CONFIG_RV_MON_SCPD`.

## Control Flow

Included by `rv_trace.h`, it maps generic implicit DA trace classes to monitor-specific names.

## State and Persistence Behavior

No state is stored in this header.

## Dependencies and Integration Points

It depends on no-ID DA event classes and ftrace event generation.

## Risks and Edge Cases

No explicit CPU ID is emitted beyond standard trace metadata.

## Test Signals

Build with `RV_MON_SCPD` and inspect trace event availability and emitted transitions.
