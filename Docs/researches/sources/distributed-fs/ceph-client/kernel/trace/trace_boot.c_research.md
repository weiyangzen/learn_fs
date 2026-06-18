# sources/distributed-fs/ceph-client/kernel/trace/trace_boot.c

## Purpose
`trace_boot.c` applies bootconfig-driven tracing setup during early boot. It parses the `ftrace` bootconfig tree and configures the global trace array plus named instances: options, tracing state, clocks, buffer sizes, CPU masks, events, kprobes, synthetic events, histogram triggers, filters, ftrace filters, tracers, and snapshots.

## Important APIs, types, and functions
Core functions include `trace_boot_set_instance_options()`, `trace_boot_enable_events()`, `trace_boot_add_kprobe_event()`, `trace_boot_add_synth_event()`, histogram command builders (`append_printf()`, `trace_boot_hist_add_array()`, `trace_boot_hist_add_handlers()`, `trace_boot_compose_hist_cmd()`), `trace_boot_init_one_event()`, `trace_boot_init_events()`, `trace_boot_set_ftrace_filter()`, `trace_boot_enable_tracer()`, `trace_boot_init_one_instance()`, `trace_boot_init_instances()`, and `trace_boot_init()`.

## Control flow
`core_initcall_sync(trace_boot_init)` runs after the top trace array exists. It finds the `ftrace` bootconfig node, configures the global trace array, then iterates `ftrace.instance.*` nodes and calls `trace_array_get_by_name()` for each instance. Per-instance setup first applies generic options, then configures individual events, then enables event lists, then enables ftrace filters/tracers/snapshots. Event setup can create kprobe or synthetic events before looking up the resulting `trace_event_file`; it then applies filters, actions, hist triggers, and final enablement under `event_mutex`.

## State and persistence behavior
Configuration persists in the target `trace_array` state after boot: ring-buffer size, clock, cpumask, trace options, enabled events, filters, triggers, and tracer selection. Boot-created dynamic events are inserted into the normal dynamic event registries. If boot tracing is active, the code disables tracing selftests to avoid conflicting boot-time activity.

## Dependencies and integration points
The file depends on bootconfig (`xbc_*` APIs), trace array controls from `trace.h`, dynamic event command generation for kprobes and synthetic events, histogram trigger parsing, event filters, ftrace filter APIs, tracefs event enable helpers, and configuration symbols for event tracing, kprobe events, synthetic events, histogram triggers, and dynamic ftrace.

## Risks
Most buffers are bounded by `MAX_BUF_LEN` 256, so long bootconfig strings are rejected or can produce truncated command failures. Histogram command composition is string-heavy and must preserve tracefs trigger syntax exactly. Locking is sensitive because event lookup, filter application, trigger processing, and enablement occur under `event_mutex`. Feature-disabled builds log errors for unsupported kprobes/synthetic events/actions rather than silently configuring them.

## Test signals
Boot with representative `ftrace` bootconfig entries for global and instance tracing; verify tracefs options, `current_tracer`, buffers, cpumasks, enabled events, dynamic events, filters, and hist triggers after boot. Negative tests should include too-long strings, missing hist keys/actions, unsupported feature configs, and invalid event names.
