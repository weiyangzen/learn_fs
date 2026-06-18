# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv-trace.h

## Purpose
Declares RTRS server trace events, currently focused on immediate IO responses.

## Important APIs, Types, And Functions
Sets `TRACE_SYSTEM rtrs_srv`, forward-declares server types, defines symbolic names for `enum rtrs_srv_state`, provides `show_rtrs_srv_state()`, and declares `TRACE_EVENT(send_io_resp_imm)`. The event records direction, invalidation mode, message id, WR count, signal interval, path state, errno, and session name.

## Control Flow
`send_io_resp_imm()` calls the generated trace hook before posting response WRs. `TP_fast_assign` walks from `struct rtrs_srv_op` to connection, common path, and server path, snapshots state and counters, and copies the kobject session name for formatted output.

## State And Persistence
No driver state is owned by the header. Event data is transient and captured only when tracing is active.

## Dependencies And Integration Points
Requires Linux tracepoint infrastructure and server/core type definitions to be available before macro expansion. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE rtrs-srv-trace` support kernel trace header generation.

## Risks
Trace event fields are a user-visible tracing ABI. The event dereferences `id->con` and kobject name, so call sites must only trace valid live operations. Copying `NAME_MAX` bytes assumes the destination has that bound.

## Test Signals
Compile with tracepoints, inspect generated event format, enable event while issuing read/write responses, verify symbolic state/direction formatting, and test with both `always_invalidate` values.
