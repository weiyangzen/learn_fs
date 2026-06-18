# sources/distributed-fs/ceph-client/include/trace/syscall.h

Purpose: Declares syscall tracing metadata and registration interfaces used by the trace event subsystem.

Important APIs/types/functions: Defines/forwards `struct syscall_metadata`, `struct trace_event_call`, `struct task_struct`, and syscall trace registration hooks for enter/exit tracepoints and metadata lookup.

Control flow: Architecture syscall table and tracing code use this header to connect syscall numbers to trace event calls. Runtime syscall enter/exit paths consult metadata and emit generated syscall trace events when enabled.

State/persistence: Metadata is statically registered by syscall tracing code; per-task syscall events are transient trace records.

Dependencies/integration: Integrates syscall entry code, trace event registration, perf/ftrace, and task context.

Risks: Syscall metadata must match architecture ABI and argument layout. Incorrect prototypes or registration hooks break syscall tracing globally.

Test signals: Build syscall tracing and run `trace-cmd`/perf syscall events, checking syscall names, numbers, and argument decoding.
