# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/opid_trace.h

## Purpose

This file defines tracepoint instances for the implicit per-CPU `opid` monitor.

## Important APIs, Types, and Functions

It instantiates `event_opid`, `error_opid`, and `error_env_opid` from implicit DA/HA event classes when `CONFIG_RV_MON_OPID` is enabled.

## Control Flow

The file is included by `rv_trace.h` under HA implicit events. Transition events use the no-ID schema; environment errors include state, event, and environment name.

## State and Persistence Behavior

No state is stored here; tracepoint schemas are generated at build time.

## Dependencies and Integration Points

It requires `event_da_monitor`, `error_da_monitor`, and `error_env_da_monitor` to be declared first.

## Risks and Edge Cases

Because it is no-ID tracing, consumers infer CPU from trace metadata rather than an explicit field.

## Test Signals

Verify `/sys/kernel/tracing/events/rv/event_opid` and `error_env_opid` exist and emit records with expected state/event strings.
