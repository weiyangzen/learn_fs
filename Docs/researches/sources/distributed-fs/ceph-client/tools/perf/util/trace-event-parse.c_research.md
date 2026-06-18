# sources/distributed-fs/ceph-client/tools/perf/util/trace-event-parse.c

## Purpose

`trace-event-parse.c` provides libtraceevent parsing helpers for tracepoint raw data, common fields, ftrace format files, event format files, saved command lines, printk format strings, task state strings, and symbolic flag values.

## Important APIs, Types, and Functions

Public helpers include `common_lock_depth()`, `common_flags()`, `common_pc()`, `raw_field_value()`, `read_size()`, `event_format__fprintf()`, `parse_task_states()`, `parse_ftrace_printk()`, `parse_saved_cmdline()`, `parse_ftrace_file()`, `parse_event_file()`, and `eval_flag()`. Internal recursive helpers search libtraceevent print arguments to find task-state flag mappings.

## Control Flow and State

Common-field helpers lazily cache offsets and sizes in static variables using the first event in the `tep_handle`. Raw field helpers locate fields by name and use libtraceevent number readers. Print helpers wrap raw bytes in a `tep_record` and ask libtraceevent to render `TEP_PRINT_INFO`. `parse_ftrace_printk()` registers address-to-format strings, `parse_saved_cmdline()` registers PID-to-comm mappings, and event parsers pass format text to `tep_parse_event()`.

## Dependencies and Integration Points

It depends on libtraceevent types, scripting context, debug logging, and trace-event declarations. It is used by `perf script`, trace-event readback, and scripting language bindings.

## State and Persistence Behavior

The module mutates the caller's `tep_handle` by registering events, comms, and printk strings. The static common-field caches are process-global and assume a stable field layout.

## Risks and Test Signals

Risks include the common-field helper argument order bug potential because offset/size pointers must be correct, stale static caches across different trace handles, malformed printk/cmdline input, and missing symbolic flags. Tests should parse recorded tracing data, render raw events, read common fields, decode sched task states, register printk formats, register saved cmdlines, and evaluate known softirq/hrtimer symbolic constants.
