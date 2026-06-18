<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/iostat.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/iostat.h

## Purpose

`iostat.h` declares the perf stat iostat mode interface and the hooks used by generic stat code and platform-specific implementations.

## Important APIs, Types, and Functions

`enum iostat_mode_t` has `IOSTAT_NONE`, `IOSTAT_RUN`, and `IOSTAT_LIST`. `iostat_print_counter_t` is a callback for printing an evsel count. The header declares prepare, parse, list, release, prefix, header, metric, and counter-print functions plus global `iostat_mode`.

## Control Flow

Generic command-line parsing calls `iostat_parse()`, setup calls `iostat_prepare()`, and output paths use prefix/header/metric/counter hooks. Release cleans platform-specific state.

## State and Persistence Behavior

The header exposes the global mode and opaque platform state through `evlist`/`perf_stat_config`; it does not define persistence.

## Dependencies and Integration Points

It includes parse-options, stat, parse-events, and evlist headers, tying iostat to perf stat event selection and output formatting.

## Risks and Edge Cases

The public callback signatures must stay aligned with generic stat code. Platform implementations must tolerate null or unsupported evlists and release partially prepared state.

## Test Signals

Command-line tests should cover `--iostat=list`, iostat run mode, unsupported-platform fallback, and output prefix/metric formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/iostat.h -->
