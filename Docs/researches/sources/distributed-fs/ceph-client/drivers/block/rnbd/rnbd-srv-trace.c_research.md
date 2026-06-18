# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv-trace.c

## Purpose
Instantiates RNBD server tracepoints declared in `rnbd-srv-trace.h`.

## Important APIs, types, and functions
- Includes RTRS and RNBD server/protocol headers so tracepoint prototypes see the relevant types.
- Defines `CREATE_TRACE_POINTS` before including `rnbd-srv-trace.h`, which emits the tracepoint definitions.

## Control flow
The file has no runtime functions of its own. It is compiled into the RNBD server trace object so calls such as `trace_process_rdma()` and `trace_process_msg_open()` resolve to real tracepoints.

## State and persistence behavior
No driver state is owned here. Tracepoint enablement and buffers are handled by the kernel tracing subsystem.

## Dependencies and integration points
Depends on tracepoint declarations in `rnbd-srv-trace.h` and server types from RTRS/RNBD headers. It must include the trace header last so helper types and constants are visible.

## Risks and test signals
Build failures are the primary signal if include order or trace event prototypes drift. Runtime validation is enabling `rnbd_srv:*` trace events while opening, closing, and issuing I/O through RNBD.
