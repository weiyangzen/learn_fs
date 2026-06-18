# sources/distributed-fs/ceph-client/kernel/trace/trace_eprobe.c

## Purpose
`trace_eprobe.c` implements event probes: dynamic events that attach to an existing trace event and emit a new event populated from selected fields of the original event. It reuses trace probe parsing and event trigger infrastructure but hides the trigger from user-controlled trigger files.

## Important APIs, types, and functions
Key types are `struct trace_eprobe` and `struct eprobe_data`. Important functions include dynamic-event callbacks (`eprobe_dyn_event_create()`, `eprobe_dyn_event_show()`, `eprobe_dyn_event_release()`, `eprobe_dyn_event_is_busy()`, `eprobe_dyn_event_match()`), lifecycle helpers (`alloc_event_probe()`, `unregister_trace_eprobe()`, `trace_event_probe_cleanup()`), field/print helpers (`eprobe_event_define_fields()`, `print_eprobe_event()`), fetch helpers (`get_event_field()`, `get_eprobe_size()`, `process_fetch_insn()`), trigger glue (`new_eprobe_trigger()`, `enable_eprobe()`, `disable_eprobe()`), registration (`eprobe_register()`), parsing (`trace_eprobe_parse_filter()`, `__trace_eprobe_create()`), and early registration (`trace_events_eprobe_init_early()`).

## Control flow
Dynamic event creation accepts commands like `e[:[GRP/]ENAME] SYSTEM.EVENT [FETCHARGS] [if FILTER]`. Parsing resolves the target event under `event_mutex`, allocates a trace probe object, optionally validates a filter against the original event, parses fetch args in `TPARG_FL_TEVENT` context, sets print format, registers a trace event call, and adds it to the dynamic event list. When the eprobe event is enabled, `enable_trace_eprobe()` creates hidden event-trigger data on the target event. When the target event fires, `eprobe_trigger_func()` receives the original record, `__eprobe_trace_func()` reserves a new eprobe event record, copies fetched args, and commits it.

## State and persistence behavior
Each eprobe stores the attached event system/name, a reference to the target `trace_event_call`, optional filter string, dynamic-event node, and trace probe metadata. Enablement state lives through trace probe file links and hidden trigger entries in the target event's trigger list. Disabling removes the trigger, synchronizes tracepoint unregister, frees filters and private data, and may unregister the eprobe event call when no siblings remain.

## Dependencies and integration points
The file depends on dynamic events, trace probe parsing, event filters, event triggers, trace event registration, ring-buffer event buffer helpers, and `event_mutex`. It integrates with perf registration only as no-op cases in `eprobe_register()`, while normal trace enable/disable attaches and detaches hidden triggers.

## Risks
Lifetime management is complex: target events require references, hidden trigger private data must survive concurrent tracepoints until `tracepoint_synchronize_unregister()`, and unregister must reject enabled or ftrace/perf-used probes. Field fetching handles dynamic, relative dynamic, static, pointer string, integer, long-sized, and array fields; incorrect offset/type handling can corrupt output or leak data. Rollback in partial enable failures warns if non-ENOMEM failures occur after earlier probes succeeded.

## Test signals
Create eprobes against normal events with integer, string, dynamic string, and array fields; apply `if` filters; enable and disable via tracefs; delete by event-only, system/event, attached event, and full command matching. Stress concurrent target event firing during deletion and run with lockdep/KASAN to catch lifetime errors.
