## sources/distributed-fs/ceph-client/arch/x86/entry/vsyscall/vsyscall_trace.h

Purpose: tracepoint definition for vsyscall emulation events.

Important API: `TRACE_EVENT(emulate_vsyscall, TP_PROTO(int nr), TP_ARGS(nr), ...)`, recording the vsyscall number.

Control flow: tracepoint is invoked from `__emulate_vsyscall()` after address-to-number decoding. It has no independent runtime path.

State/persistence: trace events are emitted to ftrace/perf tracing buffers when enabled.

Integration points: `CREATE_TRACE_POINTS` in `vsyscall_64.c`, Linux tracepoint infrastructure, and perf/ftrace users.

Risks: trace ABI is small but user-observable. Test signals include enabling the tracepoint while running legacy vsyscall callers and confirming recorded numbers.
