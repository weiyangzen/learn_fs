# sources/distributed-fs/ceph-client/tools/perf/util/trace-event.h

## Purpose

`trace-event.h` is the shared declaration point for trace-event metadata, parsing, scripting, and formatting utilities.

## Important APIs, Types, and Functions

It defines `struct trace_event`, `MAKE_LIBTRACEEVENT_VERSION`, `tep_func_resolver_t`, `struct tracing_data`, `struct scripting_ops`, and `struct scripting_context`. It declares trace initialization/cleanup, tracepoint format lookup, event-format printing/parsing, raw field access, task-state parsing, trace metadata reading/writing, scripting registration, context update, common field helpers, and sample flag formatting. It also defines `SAMPLE_FLAGS_BUF_SIZE`, `SAMPLE_FLAGS_STR_ALIGNED_SIZE`, and a compatibility `tep_field_is_relative()` helper.

## Control Flow and State

The header ties several subsystems together: metadata capture/replay, live tracefs format lookup, and script engine event callbacks. `struct scripting_ops` is a vtable for language-specific script engines.

## Dependencies and Integration Points

It depends on libtraceevent types, perf events, sessions, samples, evsels, machines, and address locations. It is included by trace readers, script engines, and tracepoint users.

## Risks and Test Signals

Risks include version compatibility with libtraceevent, callback ABI drift, and build configurations without libtraceevent/Python/Perl. Compile matrix tests should cover feature combinations and verify compatibility helpers.
