# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/trace.h

## Purpose

`trace.h` declares the tracefs support interface used by rtla tools. It exposes trace instance state, trace event configuration state, and helper functions for tracer control, event handling, and trace persistence.

## Important APIs, Types, and Functions

`struct trace_events` is a linked-list node containing system, event, filter, trigger, and enabled-state flags. `struct trace_instance` stores the tracefs instance, tep metadata handle, trace sequence buffer, missed-event count, and processed-event count. The function prototypes cover lifecycle, event enable/disable/destroy, filter/trigger attachment, file saving, and buffer sizing.

## Control Flow and Data Flow

Tool modules include this header, allocate or embed a `trace_instance`, call initialization and start/stop helpers, register libtraceevent callbacks against `trace->tep`, and use `trace_events` lists for command-line `-e`, `--filter`, and `--trigger` requests.

## State and Persistence Behavior

The header itself stores no state but defines ownership contracts: callers pass mutable `trace_instance` and `trace_events` objects to implementation functions, and destroy helpers release tracefs/tep/sequence resources.

## Dependencies and Integration Points

It depends on `<tracefs.h>` and `<stddef.h>` and is included by rtla C files that interact with tracefs. It is a central boundary between command implementations and the low-level tracefs API.

## Risks and Edge Cases

Because `trace_events` uses raw pointers and linked-list ownership, callers must avoid reusing freed event nodes. Filter/trigger enabled flags matter during cleanup. Any code embedding `trace_instance` must call destroy on all error paths to avoid leaked tracefs instances.

## Test Signals

Compile-time tests should ensure declarations match `trace.c`. Runtime tests should exercise a full instance lifecycle plus event enable/disable through command-line options in rtla tools.
