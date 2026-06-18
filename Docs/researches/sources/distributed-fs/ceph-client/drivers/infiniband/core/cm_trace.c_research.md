# sources/distributed-fs/ceph-client/drivers/infiniband/core/cm_trace.c

## Purpose

`cm_trace.c` is the tracepoint instantiation unit for the InfiniBand/RDMA Connection Manager trace events declared in `cm_trace.h`.

## Important APIs, Types, And Functions

- Defines `CREATE_TRACE_POINTS` before including `cm_trace.h`, causing the tracepoint definitions to be emitted exactly once.
- Includes `<rdma/rdma_cm.h>` and `"cma_priv.h"` before the trace header so trace helper types and formatting helpers are visible.

## Control Flow

There is no runtime logic beyond compilation of tracepoint definitions. The file participates in the kernel tracepoint build pattern: declarations live in the header, and one C file defines `CREATE_TRACE_POINTS`.

## State And Persistence

No private state is stored. Tracepoint enablement and buffers are managed by the kernel tracing subsystem.

## Dependencies And Integration Points

This file integrates `cm_trace.h` with ftrace/perf/eBPF tracing infrastructure. It is required so `trace_icm_*` calls in `cm.c` link to real tracepoint objects.

## Risks

- If this file is omitted from the build or `CREATE_TRACE_POINTS` is duplicated elsewhere, tracepoint linkage will fail.
- Include ordering must continue to satisfy helper dependencies used by the trace header.

## Test Signals

Build/link success is the primary signal. Runtime signals include the presence of `ib_cma` trace events under tracing infrastructure and successful capture of CM events emitted by `cm.c`.
