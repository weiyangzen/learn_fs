# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_trace_points.c

## Purpose

`v3d_trace_points.c` is the tracepoint instantiation unit for V3D. It includes the driver header and, outside sparse checking, defines `CREATE_TRACE_POINTS` before including `v3d_trace.h`.

## Important APIs, Types, and Functions

- `CREATE_TRACE_POINTS`: causes `TRACE_EVENT` declarations in `v3d_trace.h` to emit storage and registration code.
- `#ifndef __CHECKER__`: avoids confusing sparse with generated trace definitions.

## Control Flow

The build compiles this file once into the V3D driver. Other files include `v3d_trace.h` normally and get extern declarations; this file supplies the definitions required by the trace subsystem.

## State and Persistence Behavior

It creates the static tracepoint metadata for the module lifetime and has no runtime logic of its own.

## Dependencies and Integration Points

It depends entirely on `v3d_trace.h`, the Linux trace build system, and `v3d_drv.h` for type visibility. Removing it would leave tracepoint references unresolved.

## Risks and Edge Cases

The primary risk is duplicate or missing tracepoint instantiation. Only one translation unit may define `CREATE_TRACE_POINTS` for this trace header.

## Test Signals

Compile/link the V3D driver with tracing enabled and verify `trace_v3d_*` symbols resolve and ftrace exposes V3D event directories.
