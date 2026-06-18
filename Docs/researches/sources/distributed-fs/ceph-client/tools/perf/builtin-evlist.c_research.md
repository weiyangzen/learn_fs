<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-evlist.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-evlist.c

## Purpose
Implements `perf evlist`, a small perf.data inspection command that prints the event selectors stored in an input file or pipe and optionally includes detailed event attribute, frequency, grouping, and tracepoint field information.

## Important APIs, Types, and Functions
The entry point is `cmd_evlist()`. `__cmd_evlist()` opens the `perf_data`, creates a `perf_session`, processes pipe headers if needed, iterates `session->evlist`, and prints each `evsel` with `evsel__fprintf()`. `process_header_feature()` is a pipe-mode callback that stops session processing once enough feature/header data has been read. The command uses `struct perf_attr_details` to pass display flags such as `verbose`, `freq`, `event_group`, `trace_fields`, and `force`.

## Control Flow
`cmd_evlist()` parses `--input`, `--freq`, `--verbose`, `--group`, `--force`, and `--trace-fields`. It rejects `--group` when combined with verbose or frequency output because grouped formatting is incompatible with those expanded views. `__cmd_evlist()` builds a read-mode `perf_data` object, initializes a minimally populated `perf_tool` for pipe attr/feature processing, and creates a session. For pipe input, it calls `perf_session__process_events()` to discover attrs. It then walks every evsel, prints it, and records whether any tracepoint or non-leader grouped event was seen so it can print user tips for `--trace-fields` or `-g`.

## State and Persistence Behavior
There is no persistent state beyond reading the input perf.data stream. State is local to `__cmd_evlist()` except for standard perf globals such as `input_name` and `session_done`, which `process_header_feature()` sets for pipe termination. The command does not mutate the perf.data file and does not store output.

## Dependencies and Integration Points
Depends on perf session and evlist/evsel APIs, `evsel_fprintf`, parse-events field formatting, `util/data`, `util/debug`, and parse-options. It integrates with pipe-mode perf data processing through `perf_event__process_attr` and a feature callback. Output is direct stdout text.

## Risks and Edge Cases
Pipe mode depends on receiving enough attr/feature events before `session_done` stops processing. The compatibility check for `--group` is intentionally strict and prevents combinations that might otherwise be useful. The tracepoint and group tips are heuristic and only print when the user did not ask for the expanded information. Errors from `perf_session__new()` are returned directly through `PTR_ERR()`.

## Test Signals
Run against regular perf.data and perf.data pipes, with and without tracepoint events, grouped events, frequency sampling, and verbose attributes. Verify `perf evlist -g -v` and `perf evlist -g -F` reject with usage, `--force` passes through to perf_data, and tips appear only when relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-evlist.c -->
