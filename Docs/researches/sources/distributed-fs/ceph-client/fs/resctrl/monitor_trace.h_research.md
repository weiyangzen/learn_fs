# sources/distributed-fs/ceph-client/fs/resctrl/monitor_trace.h

## Purpose
`monitor_trace.h` defines the resctrl tracepoint used by LLC occupancy limbo scanning. It lets tracing users observe CLOSID/RMID occupancy values while the monitor code decides whether an RMID is clean enough for reallocation.

## Important APIs, Types, And Functions
The header sets `TRACE_SYSTEM resctrl` and declares `TRACE_EVENT(mon_llc_occupancy_limbo)`. The event takes `ctrl_hw_id`, `mon_hw_id`, `domain_id`, and `llc_occupancy_bytes`, stores them as trace fields, and prints them in a compact key/value format. `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` complete Linux tracepoint generation.

## Control Flow
There is no normal runtime logic in the header. Including it with `CREATE_TRACE_POINTS` in `monitor.c` instantiates the tracepoint. `__check_limbo()` calls `trace_mon_llc_occupancy_limbo()` after successful LLC occupancy reads for busy RMID entries.

## State And Persistence
The tracepoint stores no persistent resctrl state. It emits transient trace records into the kernel tracing infrastructure when enabled. The recorded identifiers reflect architecture-decoded CLOSID/RMID values and the current L3 monitor domain id.

## Dependencies And Integration Points
It depends on Linux tracepoint macros and is tightly coupled to `monitor.c` RMID limbo handling. User space can consume the event through ftrace, perf, or tracefs if tracing is configured.

## Risks
The event is diagnostic, so the main risk is semantic drift between field names and architecture behavior. On architectures where RMID depends on CLOSID, both IDs are meaningful; on x86 the CLOSID may be the empty/reserved value for RMID-only indexing. Excessive tracing during limbo scans can add overhead if enabled on systems with many RMIDs/domains.

## Test Signals
Build tests should ensure tracepoint generation succeeds with `CREATE_TRACE_POINTS`. Runtime validation can enable the event, force RMIDs into limbo, and confirm emitted records contain the expected domain id and occupancy bytes.
