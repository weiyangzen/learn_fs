# sources/distributed-fs/ceph-client/tools/perf/builtin-list.c

## Purpose

`builtin-list.c` implements `perf list`, the command that enumerates predefined perf events, PMU aliases, tracepoints, SDT probes, libpfm events when available, metrics, and metric groups. It supports default human output, raw name-only output, JSON output, optional descriptions and details, PMU/unit filtering, deprecated-event inclusion, and output redirection.

## Important APIs, Types, and Functions

`struct print_state` holds the common printing configuration: output stream, PMU glob, event glob, output style flags, metric toggles, duplicate tracking, and last printed topic/group. `struct json_print_state` embeds `print_state` and adds separator state for JSON arrays. Output is driven by `struct print_callbacks` from `util/print-events.h`; this file supplies default and JSON callbacks for start, end, event, metric, and duplicate-PMU behavior.

Key helpers include `wordwrap()` for pager-width aligned text wrapping, `default_print_event()`, `default_print_metric()`, `fix_escape_fprintf()` for JSON escaping of string fields, `json_print_event()`, `json_print_metric()`, `default_skip_duplicate_pmus()`, `json_skip_duplicate_pmus()`, and `cmd_list()`.

## Control Flow

`cmd_list()` parses options, selects either default or JSON callback tables, opens `--output` when supplied, and configures the pager for non-raw output. In default mode it initializes `last_topic`, a `visited_metrics` string list, and optional `pmu_glob` from `--unit` or the hidden compatibility `--cputype`. If no positional arguments are given, it enables metrics and metric groups unless a unit filter is active, then calls `print_events()`.

With positional filters, the command handles well-known selectors. `tracepoint` temporarily restricts the PMU glob to tracepoints. `hw`, `sw`, `cache`, and `pmu` map to legacy event globs or ABI-excluding PMU listings. `sdt` calls `print_sdt_events()`. `metric` and `metricgroup` toggle metric callbacks and call `metricgroup__print()`. `pfm` calls libpfm printing when compiled in. Arguments containing `:` are treated as tracepoint-style globs and are also used to search SDT and metrics. All other arguments are wrapped in `*...*` and used as broad event, SDT, and metric globs.

Default event printing filters deprecated events, PMU names, ABI PMUs, event names, aliases, and topics before printing topic headers, names, aliases, type descriptions, descriptions, and detailed encodings. Metric printing filters by metric or group name, emits group headers, deduplicates metric names in raw mode, and optionally prints descriptions, expressions, and thresholds. JSON callbacks apply similar filters and emit an array of event/metric objects with escaped fields.

## State and Persistence Behavior

There is no persistent repository or kernel state. Runtime state consists of allocated glob strings, last-topic/group strings, visited metric names, optional output `FILE *`, and JSON separator state. `cmd_list()` frees `pmu_glob`, `last_topic`, `last_metricgroups`, and `visited_metrics` and closes the output file at exit. It does not validate `fopen()` failure before using `ps->fp`, which is an important operational edge case.

## Dependencies and Integration Points

The file integrates with perf PMU discovery, event printing, SDT printing, metric groups, optional libpfm, pager utilities, parse-options, string glob helpers, strlist, strbuf, and global `verbose`.

## Risks and Edge Cases

JSON is manually emitted, so escaping or separator regressions can break machine consumers. `fix_escape_fprintf()` supports only `%s` and `%S`; unexpected format characters log an error but still writes literal output. `default_print_event()` allocates a unit-augmented description with `asprintf()` and relies on positive length to choose it. Pager setup is called twice in some non-raw paths. The default mode skips duplicate PMUs unless long descriptions are requested, while JSON intentionally does not, so output size and duplicate semantics differ. `--output` failure can leave a null stream.

## Test Signals

Useful tests include default output with no args, `--raw-dump`, `--json`, `--desc` and `--long-desc`, `--details`, `--deprecated`, `--unit`, hidden `--cputype`, output to a file, selectors for hardware/software/cache/pmu/tracepoint/sdt/metric/metricgroup, colon tracepoint globs, arbitrary globs, JSON escaping of quotes, backslashes, and newlines, metric deduplication in raw output, and behavior when no PMU matches.
