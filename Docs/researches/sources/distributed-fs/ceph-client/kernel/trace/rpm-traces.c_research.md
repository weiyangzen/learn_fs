# sources/distributed-fs/ceph-client/kernel/trace/rpm-traces.c

## Purpose
`rpm-traces.c` instantiates and exports runtime power-management tracepoints.

## Important APIs, types, and functions
The file defines `CREATE_TRACE_POINTS` before including `<trace/events/rpm.h>`, causing the tracepoint definitions for RPM events to be emitted. It exports `rpm_return_int`, `rpm_idle`, `rpm_suspend`, and `rpm_resume` with `EXPORT_TRACEPOINT_SYMBOL_GPL()`.

## Control flow
There are no functions in this file. Build-time inclusion of `trace/events/rpm.h` creates the tracepoints, and the export statements make them available to GPL modules.

## State and persistence
Tracepoint state is managed by the tracing subsystem. This file owns no persistent data of its own.

## Dependencies and integration points
It depends on the tracepoint event definitions in `<trace/events/rpm.h>` and on module symbol export infrastructure. Runtime PM code and GPL modules can use the exported symbols to emit or attach to RPM trace activity.

## Risks and test signals
Risks are limited but include duplicate tracepoint instantiation if `CREATE_TRACE_POINTS` is incorrectly defined elsewhere for the same header, ABI expectations around exported tracepoint names, and build breakage if event definitions change. Test signals include tracefs listing the RPM events and modules resolving the exported GPL tracepoint symbols.
