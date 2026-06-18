# sources/distributed-fs/ceph-client/arch/x86/include/asm/msr-trace.h

## Purpose
Defines tracepoints for x86 MSR and PMC access instrumentation.

## Important APIs, Types, And Functions
Declares `TRACE_SYSTEM msr`, trace include path/file, event class `msr_trace_class`, and concrete events `read_msr`, `write_msr`, and `rdpmc`. Each event records MSR/counter number, 64-bit value, and failure status.

## Control Flow
`msr.h` calls trace helpers after MSR/PMC accesses when tracepoints are enabled. The trace event prints the register number, value, and `#GP` marker on failure.

## State And Persistence
Tracepoint state is managed by ftrace/perf infrastructure. Event records persist only in trace buffers.

## Dependencies And Integration Points
Depends on Linux tracepoint APIs and is included by `msr.h`/trace generation. It integrates with kernel tracing, perf, and debugging of MSR failures.

## Risks And Edge Cases
Tracepoint format is user-visible to tracing tools. Excessive tracing of hot MSR paths can perturb timing. Failed accesses must be reported without causing recursive faults.

## Test Signals
Trace event enable/disable tests, `trace-cmd` or ftrace reads of MSR events, and build coverage with tracepoints disabled are useful.
