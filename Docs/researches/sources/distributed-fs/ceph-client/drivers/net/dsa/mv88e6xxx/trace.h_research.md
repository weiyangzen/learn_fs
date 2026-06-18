# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/trace.h

## Purpose
Defines trace events for mv88e6xxx ATU and VTU violation reporting.

## Important APIs, Types, and Functions
Declares event classes `mv88e6xxx_atu_violation` and `mv88e6xxx_vtu_violation`, then defines ATU member/miss/full events and VTU member/miss events. Payloads capture device name, source port ID, port vector or VID, MAC address for ATU, and FID.

## Control Flow and State
Trace macros generate static tracepoint metadata and fast assignment/print logic. No driver state is mutated. Event output formats show device, SPID, port vector/MAC/FID, or VID.

## Dependencies and Integration Points
Uses Linux tracepoint headers, device names, Ethernet address length, and local `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` so generated trace definitions resolve in the driver directory. Called from violation handling code elsewhere in the driver.

## Risks and Test Signals
Risks include ABI changes to trace event field names, format mismatch, and include-path breakage. Test signals include `trace-cmd`/ftrace visibility, formatted ATU/VTU violation records, and clean builds with `TRACE_HEADER_MULTI_READ`.
