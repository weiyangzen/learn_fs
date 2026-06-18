# sources/distributed-fs/ceph-client/kernel/trace/power-traces.c

## Purpose

`power-traces.c` instantiates and exports selected power-management tracepoints. By defining `CREATE_TRACE_POINTS` before including `<trace/events/power.h>`, it emits the storage and tracepoint definitions for the power event class in exactly one translation unit, then exports key tracepoints for GPL modules.

## Important APIs, Types, and Functions

- Includes power-management and tracing dependencies such as string/types, workqueues, scheduler, and modules.
- `#define CREATE_TRACE_POINTS` controls tracepoint definition generation from `<trace/events/power.h>`.
- `EXPORT_TRACEPOINT_SYMBOL_GPL(suspend_resume)`, `EXPORT_TRACEPOINT_SYMBOL_GPL(cpu_idle)`, and `EXPORT_TRACEPOINT_SYMBOL_GPL(cpu_frequency)` make these tracepoints available to GPL modules.

## Control Flow

There is no runtime function body in this file. Its control flow is compile/link-time tracepoint instantiation: the trace event header expands into tracepoint objects and helper code because `CREATE_TRACE_POINTS` is set. At module/kernel link time, the three named tracepoint symbols are exported.

## State and Persistence Behavior

The generated tracepoint objects are static kernel state created by the trace event macros. Their enabled/disabled runtime state is managed by the common tracepoint/tracing infrastructure, not by explicit code here. No file-local persistent state or cleanup path exists.

## Dependencies and Integration Points

This file integrates with the generic tracepoint system and the power trace event definitions in `<trace/events/power.h>`. Other kernel code and GPL modules can register probes against `suspend_resume`, `cpu_idle`, and `cpu_frequency`. The generated trace events appear through the normal tracing/event infrastructure.

## Risks and Edge Cases

- `CREATE_TRACE_POINTS` must appear in only one translation unit for a given trace event header; duplicating it elsewhere would cause duplicate definitions.
- Removing an export would break GPL modules that attach to these tracepoints.
- The file relies on the event header for actual field schemas and probe call signatures; schema changes happen there, not here.

## Test Signals

Compile/link success is the primary signal because this is a tracepoint definition unit. Runtime signals include the presence of power events in tracefs and successful module/probe registration against `suspend_resume`, `cpu_idle`, and `cpu_frequency`.
