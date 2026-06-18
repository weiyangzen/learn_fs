# sources/distributed-fs/ceph-client/drivers/infiniband/core/trace.c

## Purpose
`trace.c` is the translation unit that instantiates RDMA core tracepoints. It defines `CREATE_TRACE_POINTS` before including `<trace/events/rdma_core.h>`, causing tracepoint storage and registration data to be emitted exactly once.

## Important APIs, types, and functions
There are no ordinary functions in this file. The important API is the tracepoint provider contract from `trace/events/rdma_core.h`.

## Control flow and behavior
At compile time, `CREATE_TRACE_POINTS` changes the included trace-event header from declarations to definitions. Runtime behavior is owned by the kernel tracing subsystem and any tracepoint call sites in other RDMA core files.

## State, persistence, and dependencies
The emitted tracepoint descriptors are static kernel instrumentation state. The file depends on the trace event header remaining self-contained and included in only one `CREATE_TRACE_POINTS` translation unit.

## Integration points
Used by ftrace, perf, BPF, and other tracing consumers that subscribe to RDMA core events.

## Risks and test signals
Risks include duplicate tracepoint definitions if another file defines `CREATE_TRACE_POINTS` for the same header, missing tracepoints if this file is not built, and trace header drift. Test signals are successful module/kernel link, tracefs event presence under RDMA core events, and enabling/disabling the events while exercising RDMA operations.
