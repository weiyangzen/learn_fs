# sources/distributed-fs/ceph-client/samples/ftrace/sample-trace-array.h

Purpose: trace event header for `sample-trace-array.c`.

Important APIs/functions: uses Linux tracepoint macros including `TRACE_SYSTEM`, include guard pattern, `TRACE_EVENT`, `TP_PROTO`, `TP_ARGS`, `TP_STRUCT__entry`, `TP_fast_assign`, `TP_printk`, and `include/trace/define_trace.h`.

Control flow: compile-time macro expansion defines the sample event class and generated trace functions.

State and persistence: no runtime state in the header; generated tracepoint state is owned by tracing infrastructure.

Dependencies and integration: included with `CREATE_TRACE_POINTS` in the C file and must stay in include path via the Makefile.

Risks: tracepoint field layout is ABI-like for readers; changing names/types breaks consumers. Include guard and `TRACE_INCLUDE_FILE/PATH` must match file location.

Test signals: successful compile generates the trace event; runtime event appears under tracing events for the sample system.
