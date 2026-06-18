# sources/distributed-fs/ceph-client/include/trace/stages/stage6_event_callback.h

Purpose: Stage 6 defines macros used by generated event callbacks to assign captured values into raw trace records.

Important APIs/types/functions: Provides `__entry`, static/dynamic field declarations, assignment helpers `__assign_str`, `__assign_vstr`, `__assign_bitmask`, `__assign_cpumask`, `__assign_sockaddr`, relative assignment variants, and `TP_fast_assign`. It also sets defaults for `__perf_count` and `__perf_task`.

Control flow: Generated trace/perf callbacks reserve an event buffer, expand `TP_fast_assign` under this stage, copy scalar/dynamic values into the raw record, and then commit the event.

State/persistence: Writes one raw event payload per callback invocation; no long-lived state is owned by the macros.

Dependencies/integration: Depends on stage 5 offsets, raw event structs, trace event buffers, and dynamic data accessors.

Risks: Assignment helpers must match field declarations exactly. String and relative-buffer copying bugs can corrupt trace buffers or leak data.

Test signals: Enable events with strings, varargs strings, bitmasks, cpumasks, and sockaddrs; verify correct raw and formatted output.
