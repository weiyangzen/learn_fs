# sources/distributed-fs/ceph-client/samples/trace_events/trace_custom_sched.h

## Purpose

This header declares custom trace events derived from existing scheduler tracepoints with reduced/custom payloads.

## Important APIs, Types, and Functions

It uses `TRACE_CUSTOM_EVENT(sched_switch, ...)` and `TRACE_CUSTOM_EVENT(sched_waking, ...)`, defining custom `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk` sections. It ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE trace_custom_sched`, and `<trace/define_custom_trace.h>`.

## Control Flow

The header is parsed multiple times by the trace macro system. The custom sched_switch event records previous priority, next pid, and next priority. The sched_waking event records pid and priority.

## State and Persistence Behavior

Generated custom event descriptors and format metadata persist while the module is loaded. Data is recorded only when the custom events are enabled.

## Dependencies and Integration Points

It depends on `linux/trace_events.h`, scheduler tracepoint prototypes included by the C file, and the custom trace generator.

## Risks and Edge Cases

Prototype mismatch with upstream scheduler events causes build breakage or incorrect records. Include-file macros must remain outside the guard.

## Test Signals

Build and load the module, inspect custom event `format` files, enable them, and verify priority/pid output during scheduling activity.
