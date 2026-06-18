# sources/distributed-fs/ceph-client/net/batman-adv/trace.c

## Purpose
Materializes batman-adv tracepoints by defining `CREATE_TRACE_POINTS` before including `trace.h`. This is the single compilation unit that instantiates the trace event definitions declared in the header.

## Important APIs And Functions
No functions are defined directly. The important side effect is generation of tracepoint symbols for events in `trace.h`, currently `batadv_dbg`.

## Control Flow
There is no runtime control flow in this file. Build-time include ordering causes Linux tracepoint macros to emit definitions rather than declarations.

## State And Persistence
No local state or persistence. Tracepoint state is managed by the kernel tracing subsystem when enabled.

## Dependencies And Integration Points
Depends entirely on `trace.h` and the Linux tracepoint infrastructure. It integrates batman-adv debug logging with ftrace/perf-style tracing.

## Risks
Tracepoint instantiation must happen in exactly one compilation unit. Removing or duplicating this file can cause missing symbols or duplicate definitions. Include path changes in `trace.h` can break trace generation.

## Test Signals
Kernel/module build with tracing enabled is the primary signal. Runtime signal is the presence of batman-adv trace events under tracing facilities and successful event enable/disable.
