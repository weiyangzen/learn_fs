# sources/distributed-fs/ceph-client/kernel/trace/trace_stat.h

## Purpose

`trace_stat.h` declares the tracer statistics registration interface used by `trace_stat.c`. The complete 34-line header was read.

## Important APIs, Types, and Functions

The central type is `struct tracer_stat`, with file name, iteration callbacks, optional comparator, row printer, optional release callback, and optional header printer. Public functions are `register_stat_tracer()` and `unregister_stat_tracer()`.

## Control Flow

The contract is pull-based: the infrastructure calls `stat_start()`, repeatedly calls `stat_next()`, sorts entries if possible, optionally prints headers, and calls `stat_show()` for each row.

## State and Persistence Behavior

The header owns no state. A registered `tracer_stat` must outlive registration. Per-entry state may be cached until file release and released through `stat_release()`.

## Dependencies and Integration Points

It includes `linux/seq_file.h` and relies on `cmp_func_t`. It is consumed by tracing subsystems that expose one-shot statistics through tracefs.

## Risks and Edge Cases

Callback ownership must be clear. Missing required callbacks are rejected by the implementation. Name uniqueness is not represented in the type.

## Test Signals

Compile users and test registration, sorted output, headers, release callbacks, and unregister behavior.
