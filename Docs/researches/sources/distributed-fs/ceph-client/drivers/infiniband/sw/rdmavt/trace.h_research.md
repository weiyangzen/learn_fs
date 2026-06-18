# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace.h

## Purpose
`trace.h` aggregates all rdmavt tracepoint headers and defines common device-name helper macros for trace records.

## Important APIs, types, and functions
`RDI_DEV_ENTRY(rdi)` creates a trace string field named `dev` from `rvt_get_ibdev_name(rdi)`. `RDI_DEV_ASSIGN(rdi)` assigns that string in tracepoint fast paths. The header includes the trace systems for rvt core, QP, TX, MR, CQ, and RC.

## Control flow
There is no direct runtime flow. The macros are expanded by individual trace events so every event can include the rdmavt device name consistently.

## State and persistence
No persistent state. Trace event payloads include transient device strings copied at event time.

## Dependencies and integration points
It depends on `rvt_get_ibdev_name()` being available through included RDMA headers. It is included by `trace.c` for instantiation and by implementation files for tracepoint call declarations.

## Risks
Macro changes affect every trace event payload. If the common string field name changes, existing tracing scripts and debug workflows may break.

## Test signals
Tracepoint build coverage and runtime checks that emitted events include the expected `dev` field across all rdmavt trace systems.
