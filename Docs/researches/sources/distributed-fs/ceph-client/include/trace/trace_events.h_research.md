# sources/distributed-fs/ceph-client/include/trace/trace_events.h

Purpose: Core trace event macro engine that expands `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, syscall events, flags, perf permissions, callbacks, classes, and calls through seven generation stages.

Important APIs/types/functions: Redefines `TRACE_EVENT`, `TRACE_EVENT_SYSCALL`, `DECLARE_EVENT_CLASS`, `DECLARE_EVENT_SYSCALL_CLASS`, `DEFINE_EVENT`, `DEFINE_EVENT_FN`, `DEFINE_EVENT_PRINT`, `TRACE_EVENT_FN`, `TRACE_EVENT_FN_COND`, `TRACE_EVENT_FLAGS`, and `TRACE_EVENT_PERF_PERM`. It includes stage headers for raw structs, data offsets, print output, field registration, offset calculation, callbacks, and class definitions.

Control flow: The target trace header is included repeatedly via `TRACE_INCLUDE(TRACE_INCLUDE_FILE)`. Each inclusion uses a different macro environment to generate one part of the tracepoint implementation, then perf-specific hooks are added when enabled.

State/persistence: Generates static `trace_event_class`/`trace_event_call` metadata and runtime callbacks that write raw event records into trace/perf buffers.

Dependencies/integration: Central to all `include/trace/events/*.h` providers; depends on tracepoint definitions, trace event internals, perf optional support, and syscall tracing.

Risks: This file is macro-order critical. A small change can break all trace event compilation, field ABI, enable/disable behavior, or perf integration.

Test signals: Full kernel build with broad trace configs, trace event selftests, format-file inspection, ftrace enable/disable, filters, and perf tracepoint recording.
