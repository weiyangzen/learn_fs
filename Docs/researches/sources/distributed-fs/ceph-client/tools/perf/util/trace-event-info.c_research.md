# sources/distributed-fs/ceph-client/tools/perf/util/trace-event-info.c

## Purpose

`trace-event-info.c` records the tracefs metadata needed to decode tracepoint raw data later. It serializes trace headers, selected event formats, ftrace formats, printk formats, saved command lines, and a compatibility kallsyms marker into perf.data.

## Important APIs, Types, and Functions

Public functions are `tracing_data_get()`, `tracing_data_put()`, `read_tracing_data()`, `have_tracepoints()`, and `tracepoint_id_to_name()`. Internal helpers include `record_file()`, `record_header_files()`, `copy_event_system()`, `record_ftrace_files()`, `record_event_files()`, `record_proc_kallsyms()`, `record_ftrace_printk()`, `record_saved_cmdline()`, `tracepoint_id_to_path()`, `tracepoint_name_to_path()`, `get_tracepoints_path()`, and `tracing_data_header()`. `struct tracepoint_path` links selected subsystem/event pairs.

## Control Flow and State

`get_tracepoints_path()` walks evsels and builds a selected tracepoint list from names or config IDs. `tracing_data_get()` sets a file-scope `output_fd`, optionally writes to a temporary file, emits the magic/version/endian/long/page header, then records header files, ftrace event formats, selected event-system formats, a zero-sized kallsyms placeholder, printk formats, and saved cmdlines. `tracing_data_put()` copies the temp file into the final output if temp mode was used and unlinks it.

## Dependencies and Integration Points

It depends on tracefs path helpers, tracepoint iteration macros, evsel attributes, libtraceevent-compatible format text, host endianness helpers, page size, and perf debug output. It integrates with `perf record` tracing data feature generation and with `trace-event-read.c` replay.

## State and Persistence Behavior

The serialized stream becomes persistent perf.data metadata. Temporary mode stores the stream under `/tmp/perf-XXXXXX` until copied. `output_fd` is global module state during recording, so calls are not reentrant.

## Risks and Test Signals

Risks include tracefs files changing during recording, endian-size backpatch errors, temp-file leaks, missing tracepoint IDs, and format counts that do not match payloads. Tests should record a tracepoint workload, replay with `perf script`, compare event names from config IDs, validate temp and direct modes, handle absent `printk_formats` and `saved_cmdlines`, and verify old-parser compatibility for zero kallsyms payload.
