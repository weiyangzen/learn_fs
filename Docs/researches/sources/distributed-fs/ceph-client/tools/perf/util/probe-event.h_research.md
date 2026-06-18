# sources/distributed-fs/ceph-client/tools/perf/util/probe-event.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/probe-event.h` is the central public contract for perf probe event parsing, conversion, display, and application. It defines both user-facing `perf probe` descriptions and kernel/uprobe-tracer command representations, plus line-range and variable-list containers used by probe discovery.

## Important APIs, Types, and Functions

Important state/configuration includes `struct probe_conf`, global `probe_conf`, global `probe_event_dry_run`, `DEFAULT_PROBE_MAGIC_NUM`, and `MAX_EVENT_INDEX`. Core tracefs-facing types are `struct probe_trace_point`, `struct probe_trace_arg_ref`, `struct probe_trace_arg`, and `struct probe_trace_event`. User-facing probe types are `struct perf_probe_point`, `struct perf_probe_arg_field`, `struct perf_probe_arg`, and `struct perf_probe_event`. Source and variable discovery use `struct line_range` and `struct variable_list`.

Declared APIs cover symbol map lifetime (`init_probe_symbol_maps`, `exit_probe_symbol_maps`), parser/synthesizer paths (`parse_perf_probe_command`, `parse_probe_trace_command`, `synthesize_perf_probe_command`, `synthesize_probe_trace_command`, `synthesize_perf_probe_arg`), conversion/application (`convert_perf_probe_events`, `apply_perf_probe_events`, `show_probe_trace_events`, `show_bootconfig_events`, `cleanup_perf_probe_events`), display queries (`show_perf_probe_event`, `show_perf_probe_events`, `show_line_range`, `show_available_vars`, `show_available_funcs`), architecture fixups (`arch__fix_tev_from_maps`, `arch__post_process_probe_trace_events`), and helper contracts (`e_snprintf`, `copy_to_probe_trace_arg`, `get_target_map`).

## Control Flow

This header has no executable flow. Its types describe the flow used elsewhere: parse a user command into `perf_probe_event`, optionally resolve/debug-info expand it into one or more `probe_trace_event` records, synthesize tracefs commands, and either apply them to tracefs or show them to the user.

## State and Persistence Behavior

The file owns no storage beyond declarations. The global configuration controls behavior across probe modules, including dry-run behavior, cache usage, inline handling, and maximum generated probe count. Persistent state is indirect through tracefs probe event files and probe cache files managed by other modules.

## Dependencies and Integration Points

The header depends only on compiler annotations and boolean support, while forward-declaring `intlist`, `nsinfo`, `symbol`, `strlist`, `strfilter`, and `map`. It is included by probe parsing, probe cache, DWARF resolver, and perf command code. It also forms an architecture extension point for map fixups and post-processing.

## Risks and Edge Cases

The structures encode ownership-sensitive strings and arrays, so callers must use the clear/copy helpers consistently. `probe_trace_arg_ref` chains carry dereference and user-access semantics that must match tracefs syntax. The `magic_num` fallback is used when some generated probe instances lack a variable location, so bad defaults can silently alter captured data. ABI drift with tracefs kprobe/uprobe command syntax is a recurring risk.

## Test Signals

Useful tests include parser/synthesizer round trips for perf-probe and trace-probe commands, memory cleanup tests for copied and cleared events, user/kprobe/uprobe conversion tests with and without variables, dry-run application checks, bootconfig display checks, and architecture-specific post-processing tests for map-relative addresses.
