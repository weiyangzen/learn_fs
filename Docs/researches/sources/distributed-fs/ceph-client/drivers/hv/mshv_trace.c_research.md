# sources/distributed-fs/ceph-client/drivers/hv/mshv_trace.c

## Purpose

`mshv_trace.c` instantiates the MSHV tracepoints declared in `mshv_trace.h` by defining `CREATE_TRACE_POINTS` and including the header.

## Important APIs, Types, and Functions

There are no functions or data structures beyond tracepoint definition generation. The inclusion emits the tracepoint objects for events such as partition/VP lifecycle, hypercalls, memory mapping, ioeventfd assignment, dispatch, and GPA intercept handling.

## Control Flow

Build-time control flow is the important behavior: exactly one C file must define `CREATE_TRACE_POINTS` before including the trace header so the tracepoint storage is emitted once. Other files include `mshv_trace.h` normally and call `trace_mshv_*()`.

## State and Persistence Behavior

Tracepoint state is managed by the kernel tracing subsystem. This file contributes static tracepoint definitions that persist while the module is loaded.

## Dependencies and Integration Points

It depends directly on `mshv_trace.h` and indirectly on Linux tracepoint infrastructure and Hyper-V types used in event prototypes.

## Risks and Edge Cases

Adding another `CREATE_TRACE_POINTS` inclusion would cause duplicate definitions. Removing this file would leave callers with declarations but no tracepoint storage. It has no runtime error handling.

## Test Signals

Build and load the module with tracing enabled, confirm `/sys/kernel/tracing/events/mshv/*` entries exist, enable representative events, and verify lifecycle/ioctl paths emit records.
