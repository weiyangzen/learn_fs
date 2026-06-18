# sources/distributed-fs/ceph-client/tools/perf/util/probe-event.c

## Purpose
This file converts user-facing `perf probe` definitions into kernel `kprobe_events` and `uprobe_events` trace definitions, lists existing probes, shows source lines and variables, handles SDT/probe caches, and applies or displays generated probe events.

## Important APIs, Types, and Functions
Major exports include `init_probe_symbol_maps`, `exit_probe_symbol_maps`, `get_target_map`, `parse_line_range_desc`, `parse_perf_probe_command`, `parse_probe_trace_command`, `synthesize_perf_probe_arg`, `synthesize_perf_probe_command`, `synthesize_probe_trace_command`, `convert_perf_probe_events`, `show_probe_trace_events`, `show_bootconfig_events`, `apply_perf_probe_events`, `cleanup_perf_probe_events`, `show_available_funcs`, `show_line_range`, `show_available_vars`, and `copy_to_probe_trace_arg`. It manages `struct perf_probe_event`, `struct probe_trace_event`, line ranges, trace args, and blacklist nodes.

## Control Flow
Parsing starts with probe point syntax, optional event/group names, SDT targets, line/offset/return modifiers, and probe arguments. Conversion sets default groups, tries absolute-address conversion, checks probe caches, tries DWARF debuginfo, then falls back to symbol maps. Post-processing rewrites DWARF addresses into kernel/module/user trace definitions, filters out blacklisted or out-of-text kprobes, and assigns event names while avoiding conflicts. Applying opens tracefs probe files, writes events, and optionally updates caches. Listing reads raw probe files, parses trace commands, converts back to user-facing probe events, and prints them.

## State and Persistence
Global state includes `probe_event_dry_run`, `probe_conf`, `host_machine`, `host_env`, a cached debuginfo object/path, and the kprobe blacklist list. Persistent external state is read from or written to tracefs/debugfs probe files, build-id caches, probe caches, debuginfo files, and namespace-aware target paths.

## Dependencies and Integration Points
It depends on symbol maps, DSOs, namespaces, build-id cache, probe cache/file APIs, libdw and optional debuginfod, tracefs feature probes, parse-events helpers, source path lookup, maps, sessions, and architecture weak hooks for probe post-processing.

## Risks
This file has many privilege and environment-sensitive paths: `/proc/kallsyms`, debugfs blacklist, tracefs feature support, debuginfo availability, namespaces, kernel relocation, and module load state. Memory ownership is complex across parse, conversion, and cleanup paths. Fallback behavior can produce less precise probes when DWARF is unavailable. Event naming must respect `MAX_EVENT_NAME_LEN` and conflict rules.

## Test Signals
Tests should cover command parsing, invalid syntax, SDT cache lookup, DWARF-required probes, no-DWARF symbol fallback, kprobe blacklist filtering, uprobe absolute addresses, event name conflict suffixing, trace command synthesis/parsing round trips, cache writes, bootconfig output, namespace target handling, and cleanup after partial failures.
