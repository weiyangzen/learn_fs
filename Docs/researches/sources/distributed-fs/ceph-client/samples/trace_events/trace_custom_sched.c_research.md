# sources/distributed-fs/ceph-client/samples/trace_events/trace_custom_sched.c

## Purpose

This module demonstrates attaching custom trace events to existing scheduler tracepoints.

## Important APIs, Types, and Functions

It includes `<trace/events/sched.h>`, defines `CREATE_CUSTOM_TRACE_EVENTS`, includes `trace_custom_sched.h`, uses `for_each_kernel_tracepoint()`, and calls generated helpers `trace_custom_event_sched_switch_update()` and `trace_custom_event_sched_waking_update()`.

## Control Flow

Module init iterates all kernel tracepoints and passes each to `fct()`, which asks the generated custom-event helpers to attach to matching scheduler tracepoints. Exit has no explicit teardown because trace custom event infrastructure owns lifecycle.

## State and Persistence Behavior

Generated custom event metadata is module state. Event records appear in tracing buffers when enabled.

## Dependencies and Integration Points

It depends on scheduler trace event declarations and the custom trace event mechanism.

## Risks and Edge Cases

The custom event prototypes in the header must match existing scheduler tracepoint prototypes exactly. Tracepoint symbol availability and non-exported events are handled by iteration rather than direct references.

## Test Signals

Load the module, inspect custom scheduler event entries in tracing, enable them, and trigger task switches/wakes.
