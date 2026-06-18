## sources/distributed-fs/ceph-client/arch/s390/kernel/trace.c

Purpose: Defines and exports the s390 diagnose tracepoint and provides a no-recursion helper for tracing DIAG calls from low-level code.

Important APIs and functions: `CREATE_TRACE_POINTS` for `<asm/trace/diag.h>`, exported `s390_diagnose` tracepoint, and `trace_s390_diagnose_norecursion(int diag_nr)`.

Control flow: The norecursion helper avoids lockdep recursion by returning immediately when lockdep is enabled. Otherwise it disables local IRQs, checks a per-CPU recursion depth, emits `trace_s390_diagnose()`, and restores IRQ state.

State and persistence: Per-CPU `diagnose_trace_depth` tracks recursion. The tracepoint is globally registered through the tracing subsystem.

Dependencies and integration: Used by DIAG helper code and tracing users; depends on per-CPU operations, IRQ save/restore, and tracepoint infrastructure.

Risks and test signals: Risks are recursion in low-level tracing paths and missing events under lockdep. Test signals include ftrace/perf tracepoint visibility, DIAG call tracing with lockdep disabled, and no recursion warnings or IRQ-state imbalance.
