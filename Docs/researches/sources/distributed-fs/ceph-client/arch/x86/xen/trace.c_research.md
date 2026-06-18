<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/trace.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/trace.c

## Purpose
Defines Xen tracepoint support and hypercall-name resolution for ftrace/perf trace events.

## Important APIs, Types, And Functions
The file builds `xen_hypercall_names[]` from `asm/xen-hypercalls.h`, provides `xen_hypercall_name`, defines `CREATE_TRACE_POINTS`, and includes `trace/events/xen.h`.

## Control Flow
At compile time, the `HYPERCALL` macro turns hypercall op numbers into an indexed string table. Trace event code can call `xen_hypercall_name` to render a known hypercall or an empty string for unknown/out-of-range values.

## State And Persistence
State is a static read-only string table and generated tracepoint definitions. Runtime persistence is only tracepoint registration by the tracing subsystem.

## Dependencies And Integration Points
Depends on Linux ftrace, Xen public hypercall definitions, MCA definitions used by trace events, and `trace/events/xen.h`.

## Risks And Edge Cases
The string table must remain aligned with `__HYPERVISOR_*` numbering. Unknown ops intentionally return an empty string, so tooling should not assume every trace record has a name.

## Test Signals
Build with Xen tracepoints enabled and inspect `/sys/kernel/tracing/events/xen`; run workloads issuing hypercalls and verify trace output names known operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/trace.c -->
