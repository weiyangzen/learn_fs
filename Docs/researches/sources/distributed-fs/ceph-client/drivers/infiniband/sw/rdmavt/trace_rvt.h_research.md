# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_rvt.h

## Purpose
`trace_rvt.h` declares a generic rdmavt debug trace event.

## Important APIs, types, and functions
`TRACE_EVENT(rvt_dbg)` records the rdmavt device name and a string message supplied by the caller. It uses `RDI_DEV_ENTRY` and `RDI_DEV_ASSIGN` from the aggregate trace header.

## Control flow
The header does not implement driver flow. Callers such as registration/unregistration paths emit `trace_rvt_dbg()` to mark high-level lifecycle transitions.

## State and persistence
It records transient debug messages into the tracing subsystem. No rdmavt state is changed.

## Dependencies and integration points
It depends on tracepoint infrastructure, `ib_verbs.h`, and `rdma_vt.h`. It complements more structured QP/CQ/MR trace systems with low-volume lifecycle messages.

## Risks
The event stores caller-provided strings, so callsites should pass stable string data rather than short-lived buffers. Overuse would reduce the usefulness of structured tracepoints.

## Test signals
Enable `rvt:rvt_dbg` while registering and unregistering an rdmavt provider and verify device names and messages are emitted.
