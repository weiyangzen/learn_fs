# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/trace.c

## Purpose

`trace.c` provides rtla's tracefs/libtraceevent abstraction. It creates and destroys trace instances, starts/stops tracing, saves trace buffers, dispatches registered event handlers, tracks missed events, and manages user-requested trace events, filters, triggers, and trace buffer sizing.

## Important APIs, Types, and Functions

Public functions mirror `trace.h`: `enable_tracer_by_name()`, `disable_tracer()`, `create_instance()`, `destroy_instance()`, `save_trace_to_file()`, `collect_registered_events()`, `trace_instance_init()`, `trace_instance_start()`, `trace_instance_stop()`, `trace_instance_destroy()`, `trace_event_alloc()`, `trace_event_add_filter()`, `trace_event_add_trigger()`, `trace_events_enable()`, `trace_events_disable()`, `trace_events_destroy()`, and `trace_set_buffer_size()`.

## Control Flow and Data Flow

Tool initialization calls `trace_instance_init()`, which allocates a `trace_seq`, creates a tracefs instance, loads local event metadata, turns tracing off, and registers missed-event following. Event collection increments `processed_events` and delegates to libtraceevent handlers when present. Event enablement turns on tracefs events, then writes filters and triggers to event files. Disablement saves hist trigger output when applicable, writes `!trigger`/`!filter`, and disables events. Trace saving copies the instance `trace` file to a regular file using robust read/write loops.

## State and Persistence Behavior

`struct trace_instance` owns the tracefs instance, tep handle, trace sequence buffer, missed-event count, and processed-event count. Trace instances persist in tracefs until explicitly destroyed. `save_trace_to_file()` and `trace_event_save_hist()` persist trace or hist-trigger content to files in the current working directory.

## Dependencies and Integration Points

The file depends on libtracefs, libtraceevent, tracefs event files, `utils.h` allocation/error helpers, and rtla tool modules that register handlers. It integrates with timerlat/osnoise subcommands, threshold trace-output actions, user-selected `-e/--filter/--trigger`, and buffer-size options.

## Risks and Edge Cases

Filters and triggers only apply to single events, not whole systems, and are rejected otherwise. Hist trigger output file names are derived from system/event names. Missed events can saturate to `UINT64_MAX` when tracefs reports loss without a count. Event disable paths log failures but continue cleanup. File writes must handle `EINTR`; this file does so for trace and hist output loops.

## Test Signals

Tests should cover instance create/destroy, tracer enable failure for missing tracers, trace copy with interrupted reads/writes, event string parsing with and without `system:event`, filter/trigger validation, hist trigger save, missed-event accounting, and buffer-size write failures.
