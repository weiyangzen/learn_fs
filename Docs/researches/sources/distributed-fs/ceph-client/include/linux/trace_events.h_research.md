# sources/distributed-fs/ceph-client/include/linux/trace_events.h

## Purpose
Defines the core trace event metadata, record formatting APIs, ring-buffer reservation/commit interface, per-event file state, dynamic event command builders, trigger/filter flags, and optional perf/BPF integration hooks.

## Important APIs, Types, And Functions
Core types include `struct trace_entry`, `struct trace_iterator`, `struct trace_event_functions`, `struct trace_event`, `struct trace_event_class`, `struct trace_event_call`, `struct trace_event_file`, `struct trace_event_buffer`, `struct dynevent_cmd`, `struct synth_field_desc`, and `struct synth_event_trace_state`. APIs cover printing helpers (`trace_print_flags_seq()`, `trace_print_hex_seq()`), event registration (`register_trace_event()`, `trace_add_event_call()`), buffer reservation (`trace_event_buffer_reserve()`), commit (`trace_event_buffer_commit()`), filtering (`trace_define_field()`, `filter_match_preds()`), dynamic synth/kprobe event creation, event enable/disable, trigger execution, and perf/BPF probe attachment.

## Control Flow
An event call has a class, fields, print format, flags, and optional perf/BPF state. Runtime tracing reserves a buffer record, fills a `trace_entry`, applies filters/triggers/PID checks, commits to the ring buffer, and optionally submits to perf/BPF. Dynamic event builders accumulate a command in `seq_buf`, add fields, and call `dynevent_create()`. Disabled config paths provide `-EOPNOTSUPP` or neutral stubs for BPF/perf features.

## State, Persistence, And Dependencies
Persistent state lives in event-call lists, class field lists, per-event files, filters protected by RCU, eventfs inode links, trigger lists, atomic/refcount fields, perf arrays, and BPF program arrays. Dependencies include ring buffers, trace_seq, percpu data, hardirq state, perf events, and tracepoints.

## Integration Points
Integrates ftrace event definitions, tracefs event files, perf tracepoints, BPF raw tracepoints, dynamic synthetic/kprobe/uprobe events, hist triggers, and scheduler task-info recording.

## Risks And Test Signals
Risks include flag races, stale dynamic-event references, filter field mismatches, trigger recursion, BPF array lifetime under RCU, oversized perf trace records, and event format ABI drift. Test signals include event enable/disable races, dynamic event create/delete tests, filter parser and field offset tests, perf/BPF attach-detach coverage, tracefs format validation, and disabled-config builds.
