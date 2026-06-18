# sources/distributed-fs/ceph-client/tools/perf/util/trace-event.c

## Purpose

`trace-event.c` owns the common libtraceevent handle used for live tracepoint format lookup and function resolution.

## Important APIs, Types, and Functions

Public functions are `trace_event__init()`, `trace_event__cleanup()`, `trace_event__register_resolver()`, `trace_event__tp_format()`, and `trace_event__tp_format_id()`. Internal `tp_format()` reads a tracefs `format` file and parses it into a `tep_event`.

## Control Flow and State

`trace_event__init()` allocates a `tep_handle` and loads plugins. A file-scope `tevent` and `tevent_initialized` are lazily initialized by `trace_event__init2()`, which sets nanosecond output and endian flags. Format lookup by name reads `events/<sys>/<name>/format`; lookup by ID asks libtraceevent for an already parsed event. Cleanup unloads plugins and frees the handle.

## Dependencies and Integration Points

It depends on libtraceevent, tracefs path helpers, machine resolver callbacks, and filename read helpers. It supports event parsing, scripting, and tracepoint formatting.

## State and Persistence Behavior

The global trace-event object has no registered cleanup hook according to the local TODO, so process lifetime owns it. Parsed events persist in the `tep_handle`.

## Risks and Test Signals

Risks include global lifetime leaks, stale tracefs formats after initialization, error-pointer handling, and plugin load/unload mismatches. Tests should initialize and cleanup explicit handles, lazily fetch a known tracepoint format, lookup by ID after parsing, and register a symbol resolver.
