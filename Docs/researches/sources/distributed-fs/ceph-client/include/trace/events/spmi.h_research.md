
# sources/distributed-fs/ceph-client/include/trace/events/spmi.h

## Purpose
Defines SPMI tracepoints for read/write transaction boundaries and command completion, exposing opcode, slave id, address, return status, length, and transferred bytes.

## Important APIs, Types, and Functions
Events are `spmi_write_begin`, `spmi_write_end`, `spmi_read_begin`, `spmi_read_end`, and `spmi_cmd`. Write/read begin events identify opcode, sid, and address; end events add return code and read/write payload where applicable.

## Control Flow
The SPMI core emits begin events before bus transactions and end events after controller completion. `spmi_cmd` covers command-style operations without an address/payload. Dynamic arrays copy transaction data into the trace record.

## State and Persistence
The header owns no SPMI bus state. Trace buffers persist copied transaction metadata and payload bytes. Original buffers may be reused after the event without affecting trace output.

## Dependencies and Integration Points
Depends on `linux/spmi.h` and `linux/tracepoint.h`. Integrates with SPMI controllers, PMIC drivers, regulator/clock/power-management diagnostics, and SoC bring-up tracing.

## Risks
Payload traces can expose PMIC register values. Length and buffer pointer correctness is trusted. High-frequency register polling can generate large trace volume.

## Test Signals
Signals include SPMI register reads/writes, command operations, controller error injection, PMIC driver probe with tracing enabled, and payload hex output verification.
