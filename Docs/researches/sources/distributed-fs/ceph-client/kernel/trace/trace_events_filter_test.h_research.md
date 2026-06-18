# sources/distributed-fs/ceph-client/kernel/trace/trace_events_filter_test.h

## Purpose
`trace_events_filter_test.h` declares the synthetic `ftrace_test_filter` trace event used by the `CONFIG_FTRACE_STARTUP_TEST` self-test in `trace_events_filter.c`. It provides a simple event schema with eight integer fields so the filter parser and predicate program can be tested against predictable records and short-circuit expectations.

## Important APIs, Types, and Functions
- `TRACE_SYSTEM test` sets the trace system name for this generated event header.
- `TRACE_EVENT(ftrace_test_filter, ...)` defines the tracepoint prototype, arguments, record layout, assignment, and print format.
- `TP_PROTO(int a, int b, int c, int d, int e, int f, int g, int h)` and `TP_ARGS(...)` define eight integer inputs.
- `TP_STRUCT__entry()` creates fields `a` through `h`, all `int`, which become filterable fields in the generated `struct trace_event_raw_ftrace_test_filter`.
- `TP_fast_assign()` copies the arguments into the trace record.
- `TP_printk()` formats all eight fields in a fixed, human-readable order.
- `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE trace_events_filter_test`, and `<trace/define_trace.h>` enable tracepoint code generation when included with `CREATE_TRACE_POINTS`.

## Control Flow
The header follows the standard trace event header pattern. Include guards allow normal inclusion while `TRACE_HEADER_MULTI_READ` lets trace generation re-read the header. When `trace_events_filter.c` is built with `CONFIG_FTRACE_STARTUP_TEST`, it defines `CREATE_TRACE_POINTS` before including this header. That causes the trace event macros to emit the generated tracepoint, event call, raw record struct, and helper functions.

The startup test then calls `create_filter()` against `event_ftrace_test_filter`, constructs `struct trace_event_raw_ftrace_test_filter` records with different `a` through `h` values, and runs `filter_match_preds()` against those records. The event may also be emitted once through `trace_ftrace_test_filter(1, 2, 3, 4, 5, 6, 7, 8)` to avoid unused tracepoint warnings.

## State and Persistence
The header does not store runtime state itself. It defines the schema that generated trace code uses to create event metadata and raw records. Runtime state for the self-test lives in `trace_events_filter.c`: compiled filters, test data arrays, visited-predicate markers, and the generated `event_ftrace_test_filter` descriptor.

There is no persistence beyond compiled kernel text/data for the test build. The event exists only when the self-test configuration includes it.

## Dependencies and Integration Points
This header depends on `<linux/tracepoint.h>` and the kernel `TRACE_EVENT` macro system. It is included by `trace_events_filter.c` under `CONFIG_FTRACE_STARTUP_TEST`, where generated artifacts integrate with the normal event registration path, field-definition logic in `trace_events.c`, and filter lookup through `trace_find_event_field()`.

Because the fields are plain integers with simple names, the event is ideal for exercising logical-expression compilation without complications from string, cpumask, function, or dynamic-array predicate types.

## Risks
- The header must remain outside ordinary include protection for `<trace/define_trace.h>` at the bottom; moving it inside the guard would break tracepoint generation.
- Field names `a` through `h` are assumed by the test data in `trace_events_filter.c`. Renaming or changing field types would invalidate those tests.
- The generated raw struct name is consumed directly by the test (`struct trace_event_raw_ftrace_test_filter`), so event-name changes require coordinated updates.
- Because this is a startup-test-only header, it may receive less build coverage in configurations without `CONFIG_FTRACE_STARTUP_TEST`.

## Test Signals
The main signal is boot-time output from `ftrace_test_event_filter()`, especially the final `Testing ftrace filter: OK` line. Failures report either filter creation errors, unexpected predicate visits that indicate short-circuit regressions, or mismatched filter results. Successful generation also exposes the synthetic event metadata internally as `event_ftrace_test_filter` and the helper `trace_ftrace_test_filter()`.
