# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/snep_trace.h

## Purpose

This header defines implicit DA tracepoint instances for `snep`.

## Important APIs, Types, and Functions

It instantiates `event_snep` and `error_snep` under `CONFIG_RV_MON_SNEP`.

## Control Flow

Included by `rv_trace.h`, it exposes transition and error tracepoints.

## State and Persistence Behavior

No mutable state is stored.

## Dependencies and Integration Points

It depends on generic implicit DA event classes.

## Risks and Edge Cases

Trace names include generated state strings, including the model typo.

## Test Signals

Verify trace event availability and error output under forced invalid preempt/schedule ordering.
