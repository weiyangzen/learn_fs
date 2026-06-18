# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace.c

## Purpose
`trace.c` is the tracepoint instantiation unit for rdmavt. It defines `CREATE_TRACE_POINTS` once and includes the aggregate trace header so the trace events declared in the individual `trace_*.h` files get generated.

## Important APIs, types, and functions
There are no functions. The important mechanism is `#define CREATE_TRACE_POINTS` followed by `#include "trace.h"`, which pulls in `trace_rvt.h`, `trace_qp.h`, `trace_tx.h`, `trace_mr.h`, `trace_cq.h`, and `trace_rc.h`.

## Control flow
No runtime control flow is implemented directly. At build time, the Linux tracepoint framework emits event descriptors and callsites for all rdmavt trace events.

## State and persistence
No driver state is owned here. Tracepoint enablement state is owned by the kernel tracing subsystem.

## Dependencies and integration points
This file depends on every included trace header being tracepoint-safe and using `TRACE_INCLUDE_FILE` correctly. It integrates with ftrace/perf trace events and rdmavt callsites such as QP insertion/removal, send posting, CQ events, MR mapping, and RC timeout/RNR handling.

## Risks
Adding `CREATE_TRACE_POINTS` in more than one compilation unit would cause duplicate definitions. Broken include guards or mismatched `TRACE_INCLUDE_FILE` values in individual trace headers can break module builds.

## Test signals
Build `rdmavt` with tracing enabled, verify trace event files appear under tracing for `rvt`, `rvt_qp`, `rvt_tx`, `rvt_mr`, `rvt_cq`, and `rvt_rc`, and enable events while exercising QP/CQ/MR paths.
