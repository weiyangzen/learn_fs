# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_trace.h

## Purpose
`cros_ec_trace.h` declares the generic Chrome EC request tracepoints used around every transport transfer.

## Important APIs, Types, and Functions
- `TRACE_EVENT(cros_ec_request_start)` records command version, passthrough offset, normalized command ID, outsize, and insize.
- `TRACE_EVENT(cros_ec_request_done)` records the same fields plus EC result and Linux return value.
- `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` direct trace generation to this local header.

## Control Flow
The protocol helper calls `trace_cros_ec_request_start(msg)` immediately before the selected transport callback and `trace_cros_ec_request_done(msg, ret)` immediately afterward. The tracepoint print functions normalize passthrough commands by splitting the command into a device offset and base command ID, then use symbolic tables from `cros_ec_trace.c`.

## State and Persistence
The header defines trace schemas only. Runtime trace state is external to the driver.

## Dependencies and Integration Points
It depends on Linux tracepoint headers, Chrome EC command/protocol definitions, and the `EC_CMDS`/`EC_RESULT` symbolic macros defined before instantiation by `cros_ec_trace.c`.

## Risks and Edge Cases
The `retval` field is printed with `%u` despite being stored as signed `int`, so negative errors can display in unsigned form in trace output. Passthrough offset calculation assumes the PD passthrough offset macro is the intended divisor/modulus for all traced commands.

## Test Signals
Compile-time tracepoint generation is the static signal. Runtime signal is request-start/done trace pairs around EC commands.
