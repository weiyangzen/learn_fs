# sources/distributed-fs/ceph-client/kernel/trace/trace.h

## Purpose
`trace.h` is the private umbrella header for the kernel tracing core. It defines ring-buffer entry types, the central `trace_array` instance object, tracer callback contracts, trace output option bits, event-filter and event-trigger plumbing, function-graph helpers, snapshot hooks, dynamic tracefs helpers, and many cross-file prototypes used by the `kernel/trace` implementation. It is not Ceph-specific despite living under this source snapshot; it provides the infrastructure that Ceph and other subsystems can consume through tracepoints, ftrace, perf, and tracefs.

## Important APIs, types, and functions
Important types include `enum trace_type`, `struct trace_array_cpu`, `struct array_buffer`, `struct trace_array`, `struct tracer`, `struct tracer_flags`, `struct trace_parser`, `struct ftrace_event_field`, `struct event_filter`, `struct trace_subsystem_dir`, `struct event_trigger_data`, `struct event_command`, and `struct trace_min_max_param`. `trace_array` is the persistence and lifecycle hub: it owns live and snapshot buffers, tracefs dentries, enabled events, system lists, PID filters, clock choice, flags, ftrace ops, function-graph ops, error logs, histogram variables, saved command maps, and per-instance reference counts.

Key APIs declared here include trace instance lookup (`trace_array_find_get()`), buffer reservation and commit (`trace_buffer_lock_reserve()`, `trace_buffer_unlock_commit_regs()`), trace file open/release helpers, PID filter operations, tracer registration (`register_tracer()`), event filter application, event trigger registration, snapshot controls, function trace controls, trace option parsing, ring-buffer resizing, and perf ftrace registration. Inline helpers such as `trace_assign_type()`, `tracer_tracing_is_on_cpu()`, `event_trigger_unlock_commit()`, `trace_event_setup()`, and `ftrace_trace_stack()` provide fast paths used by many trace writers.

## Control flow and integration
The header is included by most tracing C files and mediates several flows. Event writers reserve a `ring_buffer_event`, call `trace_event_setup()` or `tracing_generic_entry_update()`, fill an entry structure generated from `trace_entries.h`, then commit through `trace_buffer_unlock_commit()` or `event_trigger_unlock_commit()`. Trigger-aware writers call `__event_trigger_test_discard()`, which runs conditional triggers, filter predicates, soft-disabled checks, and PID filters before committing or discarding. Tracers implement `struct tracer` callbacks and register with the core so tracefs `current_tracer` can call their `init`, `reset`, `start`, `stop`, output, and option handlers.

The file also drives macro expansion. It includes `trace_entries.h` once with `FTRACE_ENTRY` defined to create concrete C structures, then later redefines `FTRACE_ENTRY` to declare the matching `trace_event_call` objects. That two-pass use ties binary ring-buffer layouts to user-visible format metadata.

## State and persistence behavior
Most state referenced here is in-memory kernel state exposed through tracefs. `trace_array` instances persist until trace instances are removed; buffers keep event history, snapshot buffers keep max-latency or user snapshots, and lists such as `events`, `systems`, `err_log`, `hist_vars`, and PID filters retain configuration. The header uses RCU pointers for PID lists and event filters, mutexes for global trace/event list mutation, per-CPU storage for buffers and repeat tracking, and config-gated stubs so callers compile even when tracing features are disabled.

## Dependencies
This header depends on Linux tracing, ftrace, ring buffer, trace events, tracepoint, BPF/BTF-adjacent event definitions, tracefs/eventfs, lock/RCU primitives, workqueues, per-CPU data, and configuration symbols such as `CONFIG_FUNCTION_TRACER`, `CONFIG_FUNCTION_GRAPH_TRACER`, `CONFIG_TRACER_SNAPSHOT`, `CONFIG_EVENT_TRACING`, `CONFIG_HIST_TRIGGERS`, `CONFIG_PERF_EVENTS`, and syscall tracing.

## Risks
The highest risks are ABI layout drift in `trace_entries.h` macro expansion, reference/lifetime mistakes for dynamic `trace_event_file` objects, recursion in trace paths, and locking-order mistakes around `event_mutex`, `trace_types_lock`, `max_lock`, RCU lists, and per-CPU buffers. The inline discard/commit logic is central: a missed filter or PID check can leak data, while a wrong discard can silently drop events. Config-gated stubs reduce ifdef noise but can hide feature-dependent behavior in tests.

## Test signals
Useful signals include booting with tracing selftests, toggling tracers through tracefs, enabling event filters and triggers, exercising snapshots, validating generated event `format` files, running perf tracepoint sampling, and checking lockdep/RCU diagnostics while repeatedly creating and deleting trace instances and dynamic events.
