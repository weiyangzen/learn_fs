# sources/distributed-fs/ceph-client/tools/perf/util/trace-event-read.c

## Purpose

`trace-event-read.c` reads the tracing metadata stream produced by `trace-event-info.c` and reconstructs a `struct trace_event`/libtraceevent handle for perf.data replay.

## Important APIs, Types, and Functions

The public function is `trace_report(int fd, struct trace_event *tevent, bool repipe)`. Internal helpers read exact byte counts, optionally repipe bytes to stdout, read strings, skip legacy kallsyms, read and parse header files, ftrace files, event files, printk formats, and saved command lines.

## Control Flow and State

`trace_report()` validates the magic bytes and `"tracing"` tag, reads the version string, endian flag, long size, and page size, initializes a trace-event handle, sets libtraceevent endian/size configuration, then parses headers, ftrace formats, event formats, kallsyms placeholder, printk data, and saved cmdlines for version 0.6 and newer. It returns the number of bytes consumed or -1 on failure.

## Dependencies and Integration Points

It depends on libtraceevent, trace-event parsing helpers, host endian detection, and debug logging. It is used when reading perf.data trace metadata before decoding tracepoint raw samples.

## State and Persistence Behavior

Module-level `input_fd`, `trace_data_size`, and `repipe` hold current read state, making parsing non-reentrant. Successful parsing leaves `tevent->pevent` initialized for later event formatting.

## Risks and Test Signals

Risks include corrupt size fields causing large allocations, non-reentrant globals, repipe write failures, version-gated saved-cmdline parsing, and endian/long-size mismatches. Tests should round-trip metadata from `trace-event-info.c`, parse older streams without saved cmdlines, reject bad magic/tag, exercise repipe mode, and run with big-endian fixture data when available.
