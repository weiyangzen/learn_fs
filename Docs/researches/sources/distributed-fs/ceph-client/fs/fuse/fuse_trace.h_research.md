# sources/distributed-fs/ceph-client/fs/fuse/fuse_trace.h

## Purpose
`fuse_trace.h` defines FUSE tracepoints for request submission and completion. It gives ftrace/perf/BPF users a stable view of connection device ID, request unique ID, opcode, request length, reply length, and reply error for the FUSE protocol operations listed in the local opcode table.

## Important APIs, Types, And Functions
The `OPCODES` macro lists symbolic names for protocol opcodes from `FUSE_LOOKUP` through `FUSE_STATX`, plus `CUSE_INIT`. The file expands that list first into `TRACE_DEFINE_ENUM()` declarations, then into the `__print_symbolic()` table used in trace output. Two `TRACE_EVENT`s are defined: `fuse_request_send` and `fuse_request_end`.

`fuse_request_send` records `connection`, `unique`, `opcode`, and input `len` from `req->fm->fc->dev` and `req->in.h`. `fuse_request_end` records `connection`, `unique`, output `len`, and protocol `error` from `req->out.h`.

## Control Flow
This header is consumed by the Linux tracepoint generation machinery. FUSE request code includes/emits the trace events around the lifecycle of a `struct fuse_req`: when a request is sent to userspace and when it completes. At runtime, tracepoint enablement controls whether the fast assignment and print formatting execute.

## State And Persistence Behavior
No FUSE runtime state is stored here. Trace records are ephemeral diagnostics emitted through the kernel tracing subsystem. The only persistent contract is the mapping between numeric opcodes and printable symbolic names compiled into the tracepoint format.

## Dependencies And Integration Points
The file includes `linux/tracepoint.h`, expects `struct fuse_req` fields from the including translation unit, sets `TRACE_SYSTEM` to `fuse`, and ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` for tracepoint generation. It integrates with request send/end instrumentation in the FUSE device/request implementation.

## Risks And Edge Cases
Trace output can mislead diagnostics if `OPCODES` is not kept in sync with UAPI opcode additions. The trace events dereference `req->fm->fc`, so instrumentation must only be used while the request still holds valid mount/connection references. High-volume tracing on busy FUSE mounts can create significant trace data and perturb timing, especially around request latency investigations.

## Test Signals
Useful checks include building with tracing enabled, verifying `format` files expose the expected fields, enabling `fuse:fuse_request_send` and `fuse:fuse_request_end` during simple filesystem operations, confirming symbolic opcode names print for newer operations such as `FUSE_STATX` and `FUSE_COPY_FILE_RANGE`, and confirming completion errors match userspace daemon replies.
