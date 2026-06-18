# sources/distributed-fs/ceph-client/tools/perf/util/data-convert-json.c

## Purpose

`data-convert-json.c` implements perf data conversion to a JSON document. It writes perf header metadata and sample records with timestamp, PID/TID, CPU, comm, callchain entries, symbols/DSOs, and tracepoint raw fields when libtraceevent is available.

## Important APIs, Types, and Functions

The main runtime type is `struct convert_json`, carrying `perf_tool`, output stream, first-item delimiter state, time ranges, and counters. `bt_convert__perf2json()` is the public entry. JSON helpers include `output_json_string()`, `output_json_delimiters()`, `output_json_format()`, and key/value wrappers. `process_sample_event()` resolves samples and emits sample JSON objects, while `output_headers()` emits file and environment metadata.

## Control Flow

The converter rejects currently unsupported `--all` and `--tod`, opens the output with `O_EXCL` unless forced, creates a perf session, initializes symbols, parses optional time ranges, writes a top-level object with version and headers, processes ordered events through perf callbacks, appends sample objects into a JSON array, then closes the document and reports counts. Samples are skipped if outside the requested time range and otherwise resolved through `machine__resolve()`.

## State and Persistence Behavior

Persistent output is a single JSON file. The output is streamed directly through `FILE *out`; `first` controls comma placement. It reads `perf.data` without modification and relies on symbol resolution state initialized from the session environment. The JSON version field is `linux-perf-json-version: 1` for future compatibility.

## Dependencies and Integration Points

The file integrates with `perf_session__process_events()`, symbol initialization, machine/thread/map resolution, callchain context markers, perf header/environment metadata, auxtrace pass-through processors, and libtraceevent field formatting. It shares `struct perf_data_convert_opts` with the CTF converter but supports fewer options.

## Risks and Edge Cases

JSON escaping must preserve valid RFC 8259 output for quotes, backslashes, and control characters. If sample resolution fails, conversion errors. Context marker handling must track kernel/user/hypervisor mode across callchain entries. Tracepoint raw fields are printed as strings from libtraceevent rather than typed JSON values. Error handling after `perf_session__new()` assumes `session` is valid on later labels, so early setup changes should be careful.

## Test Signals

Tests should validate syntactically valid JSON, force/no-force output behavior, time filtering and skipped counts, samples with and without callchains, symbol and DSO emission, CPU fallback from thread state, tracepoint raw field output with libtraceevent, auxtrace-containing perf data, and unsupported-option error paths.
