# sources/distributed-fs/ceph-client/tools/perf/scripts/python/gecko.py

## Purpose

`gecko.py` converts perf samples into Firefox's Gecko Profile JSON format so traces can be inspected in `https://profiler.firefox.com/`. It supports the normal `perf script report gecko` flow and the combined `perf script gecko ...` flow. By default it writes `gecko_profile.json`, starts a local HTTP server, and opens the hosted profile URL in the default browser; with `--save-only` it only writes the selected file.

## Important APIs, Types, and Functions

The script defines type aliases for string, stack, frame, category, and millisecond ids. Gecko row types are `Frame`, `Stack`, and `Sample` as `NamedTuple`s. The central builder is the `Thread` dataclass, which owns per-thread samples and intern tables: `frameTable`, `stringTable`, `stringMap`, `stackTable`, `stackMap`, and `frameMap`.

`Thread._intern_string()`, `_intern_frame()`, and `_intern_stack()` deduplicate profile entities and return ids. `_add_sample()` updates a thread's current comm and appends a timestamped sample for a root-first stack. `_to_json_dict()` emits the Gecko thread object with table schemas.

Perf entry points are `process_event()`, `trace_begin()`, and `trace_end()`. `CORSRequestHandler` adds an `Access-Control-Allow-Origin` header for profiler.firefox.com. `launchFirefox()` builds a `from-url` profiler URL. `main()` parses `--user-color`, `--kernel-color`, and `--save-only`, initializes category metadata, and sets the output path.

## Control Flow and Data Flow

When executed, `main()` parses arguments and defines two categories: User and Kernel, with configurable colors. During tracing, `trace_begin()` starts a daemon `http.server` thread on the default port when not in save-only mode. Each `process_event()` converts perf's sample timestamp from nanoseconds to milliseconds, initializes global `start_time` from the first sample, extracts pid/tid/comm, builds a stack from `callchain` entries when available, or falls back to the event's `symbol` and `dso`.

Stacks are formatted as `function (in dso)`. Callchains are reversed so root frames precede leaf frames. Samples are grouped by tid in `tid_to_thread`; each thread builder interns frames/stacks and appends a `Sample(stack_id, time_ms, responsiveness=0)`. At trace end, all thread builders are converted to JSON and wrapped with Gecko `meta`, empty `libs`, empty `processes`, and empty `pausedRanges`. The JSON is written to `output_file` or `gecko_profile.json`, and non-save-only mode opens Firefox Profiler against `http://localhost:8000/<file>`.

## State and Persistence Behavior

Global state includes `start_time`, `CATEGORIES`, `PRODUCT`, `output_file`, `tid_to_thread`, and `http_server_thread`. Per-thread intern tables persist for the duration of the conversion and reduce JSON size by sharing repeated strings, frames, and stack prefixes. Persistent output is the Gecko JSON file. Non-save-only mode also creates a local server rooted at the current working directory through `SimpleHTTPRequestHandler`.

## Dependencies and Integration Points

The script depends on perf's Python event dictionaries, `PERF_EXEC_PATH`, Firefox Profiler's Gecko profile schema, Python dataclasses, `http.server`, `webbrowser`, and the platform `uname -op` command used for the product string. Wrapper `scripts/python/bin/gecko-report` invokes it with `perf script -s`.

The profiler integration relies on CORS allowing `https://profiler.firefox.com` to fetch `http://localhost:8000/gecko_profile.json`. Category names and color strings are selected to match Firefox Profiler category CSS expectations.

## Risks and Edge Cases

`process_event()` indexes `param_dict['callchain']` directly, so events without that key can fail despite later fallback logic for empty callchains. `start_time` uses `if not start_time`, so a legitimate zero timestamp would be treated as uninitialized again. The local HTTP server uses `http.server.test()` with the default port, which can fail or serve the wrong directory if port 8000 is occupied or the process cwd changes. The server thread is daemonized and not explicitly shut down.

Kernel/user category detection in `_intern_frame()` is string-based: frames containing `kallsyms`, `/vmlinux`, or ending in `.ko)` are kernel, all others are user. The `stackMap` annotation says tuple keys, but implementation uses comma-separated strings; this works internally but can be confusing and could collide only if ids were not integers. The script imports many modules and perf helpers that are unused, increasing startup surface. Browser launch is best-effort and can be undesirable in headless environments unless `--save-only` is used.

## Test Signals

Run `perf record -g` followed by `perf script report gecko --save-only out.json` and validate that JSON contains `meta`, `threads`, `samples`, `frameTable`, `stackTable`, and `stringTable`. A no-callchain trace should still produce samples using `symbol`/`dso`. A normal non-save-only run should create `gecko_profile.json`, start an HTTP server, and open a profiler URL. Tests should cover custom category colors, occupied port 8000, missing callchain key, and traces with kernel frames to verify category assignment.
