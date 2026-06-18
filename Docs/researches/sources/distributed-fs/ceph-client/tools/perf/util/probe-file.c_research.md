# sources/distributed-fs/ceph-client/tools/perf/util/probe-file.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/probe-file.c` implements perf probe interactions with tracefs/debugfs probe event files and the build-id-backed probe cache. It opens `kprobe_events` and `uprobe_events`, reads and filters installed probe names, writes synthesized probe commands, deletes probes, persists resolved probe mappings, scans SystemTap SDT ELF notes, and probes tracefs README feature availability.

## Important APIs, Types, and Functions

Tracefs APIs include `open_trace_file`, `probe_file__open`, `probe_file__open_both`, `probe_file__get_rawlist`, `probe_file__get_namelist`, `probe_file__add_event`, `probe_file__get_events`, and `probe_file__del_strlist`. Cache APIs include `probe_cache__new`, `probe_cache__purge`, `probe_cache__delete`, `probe_cache_entry__get_event`, `probe_cache__find`, `probe_cache__find_by_name`, `probe_cache__add_entry`, `probe_cache__scan_sdt`, `probe_cache__commit`, `probe_cache__filter_purge`, and `probe_cache__show_all_caches`. Feature probes include `probe_type_is_available`, `kretprobe_offset_is_supported`, `uprobe_ref_ctr_is_supported`, `user_access_is_supported`, `multiprobe_event_is_supported`, and `immediate_value_is_supported`.

Internal helpers include warning printers for common tracefs failures, `__probe_file__get_namelist`, `__del_trace_probe_event`, cache open/load/write/compare/show helpers, SDT note address/ref-counter extractors, SDT argument parsing/synthesis, and `scan_ftrace_readme`. `MAX_CMDLEN` reflects the tracefs command length budget.

## Control Flow

Opening a probe file builds a path under `tracing_path_mount()`, opens read-only unless write access is requested and dry-run is disabled, and emits targeted warnings for permission, missing tracefs, missing kprobe/uprobe support, or general open failure. Listing installed probes reads raw lines from the tracefs file, parses each line into a `probe_trace_event`, and returns either raw commands, event names, or group:event names.

Adding probes synthesizes a trace command from `probe_trace_event` and writes it to the selected tracefs file unless `probe_event_dry_run` is set. Deletion converts stored `group:event` names into tracefs delete syntax and writes one delete command per list entry.

Cache creation resolves a target build-id, creates or locates a build-id cache directory, opens the `probes` file, and loads entries. Cache load treats lines beginning with `#` as perf probe definitions, `%` as SDT definitions, and following lines as trace-probe commands. Adding a cache entry removes any matching existing entry, creates a new entry from the perf probe command, synthesizes each trace event command, and appends it. Commit rewinds/truncates the cache file, writes every entry, and rolls back file size if a partial write occurs.

When SDT note support is enabled, `probe_cache__scan_sdt` walks SDT notes in an ELF file, creates `sdt_PROVIDER:NAME` entries, synthesizes uprobe commands with optional reference counters and parsed operands, and stores them in the cache. Feature queries lazily scan tracefs `README` once with glob patterns and cache the booleans.

## State and Persistence Behavior

Tracefs probe state is external kernel state in `kprobe_events` and `uprobe_events`. Probe cache state is persistent under the perf build-id cache as a `probes` file, keyed by target build-id or kallsyms. `struct probe_cache` owns an open fd and an in-memory list of `struct probe_cache_entry` objects. Static feature state in `scan_ftrace_readme` is process-local and scanned once.

## Dependencies and Integration Points

The file integrates with tracefs/debugfs path helpers, build-id cache, namespace switching for target build-id lookup, ELF/SDT note helpers, strlist/strfilter, probe event parsing/synthesis, dwarf register SDT operand parsing, and perf debug/color output. Public prototypes are gated by `HAVE_LIBELF_SUPPORT`; SDT scanning is gated by `HAVE_GELF_GETNOTE_SUPPORT`.

## Risks and Edge Cases

Partial tracefs writes are reported but leave kernel state dependent on tracefs behavior. `probe_cache_entry__get_event` returns the number parsed even if a later parse fails, so callers must treat short results carefully. Cache fd cleanup only closes `fd > 0`, so fd 0 would not be closed, although cache files are normally not stdin. SDT argument parsing has architecture-specific operand assumptions and special Arm64 stack-operand concatenation. Feature detection depends on README wording and can be stale for the process after the first scan. Cache commit truncates before rewriting, making rollback logic important for corruption avoidance.

## Test Signals

Tests should cover permission/missing-file warning paths, dry-run add behavior, raw/name/group listing with duplicate names, deletion syntax conversion, cache load/commit round trips, cache replacement and filter purge, build-id target/kallsyms cache opening, SDT note synthesis with typed operands and reference counters, README feature probes on mocked README content, and failure injection for partial cache writes.
