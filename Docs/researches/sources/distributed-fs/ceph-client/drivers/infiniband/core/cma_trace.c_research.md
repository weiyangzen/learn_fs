<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_trace.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_trace.c

## Purpose

`cma_trace.c` is the tracepoint instantiation unit for RDMA CMA trace events. It defines `CREATE_TRACE_POINTS`, includes the RDMA CM and IB CM type declarations plus `cma_priv.h`, then includes `cma_trace.h` so the tracepoint definitions generate storage and registration code exactly once.

## Important APIs, types, and functions

There are no runtime functions in this file. Its important interface is the build-time tracepoint pattern: `CREATE_TRACE_POINTS` must be defined before including `cma_trace.h`. The included private and public RDMA headers provide the type information used by trace event prototypes and field extraction.

## Control flow

Control flow is compile/link-time. Other CMA translation units include `cma_trace.h` without `CREATE_TRACE_POINTS` to get tracepoint declarations and inline call sites. This file includes the same header with `CREATE_TRACE_POINTS` so the kernel trace subsystem receives the actual tracepoint definitions for `rdma_cma`.

## State and persistence

The file does not maintain per-object state. Generated tracepoint metadata is registered as part of the kernel/module image and used by ftrace/perf/tracefs when enabled. Trace buffers and enabled/disabled state are owned by the kernel tracing subsystem, not this file.

## Dependencies and integration points

It depends on tracepoint infrastructure, `rdma/rdma_cm.h`, `rdma/ib_cm.h`, `cma_priv.h`, and `cma_trace.h`. It integrates with all `trace_cm_*` call sites in `cma.c`. Removing or duplicating this file would either break tracepoint linkage or create duplicate definitions.

## Risks

The main risk is include-order correctness. `CREATE_TRACE_POINTS` must appear before `cma_trace.h`, and the needed RDMA types must be visible before event definitions are expanded. This file should remain minimal; adding unrelated logic can cause tracepoint compilation dependencies or duplicate symbol issues.

## Test signals

Build success with tracing enabled is the primary signal. Runtime validation is that tracefs lists the `rdma_cma` events defined in `cma_trace.h`, and enabling them captures CMA attach, QP, event, request, and device add/remove activity from `cma.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_trace.c -->
