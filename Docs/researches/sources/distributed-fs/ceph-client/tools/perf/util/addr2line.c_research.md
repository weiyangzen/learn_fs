# sources/distributed-fs/ceph-client/tools/perf/util/addr2line.c

## Purpose

`addr2line.c` maintains a persistent subprocess interface to GNU `addr2line` or LLVM `llvm-addr2line` so perf can resolve addresses to source file/line and inline frames.

## Important APIs, Types, and Functions

Public APIs are `cmd__addr2line` and `dso__free_a2l`. Internal helpers split `file:line`, start/cleanup `struct child_process`, detect command style with a sentinel request, parse records with `read_addr2line_record`, and append inline records through `inline_list__append_record`.

## Control Flow and State

`cmd__addr2line` lazily starts and stores a subprocess in the DSO when debug line info exists. It configures command style once, writes an address plus comma sentinel, reads the first record, stores file/line outputs, optionally appends inline frames up to `MAX_INLINE_NEST`, drains remaining records until sentinel, and cleans up if EOF is seen. The subprocess is reused across calls per DSO.

## Dependencies and Integration Points

It depends on perf DSO/symbol/srcline/inline infrastructure, `api/io` buffered reads with timeout, `run-command`, and `symbol_conf` options for path, timeout, and warnings. It feeds annotation and source-line reporting.

## Risks and Test Signals

Risks include protocol differences between GNU and LLVM, sentinel misdetection, subprocess hangs/timeouts, SIGPIPE handling, leaked child processes, and inline recursion limits. Tests should resolve normal addresses, address zero, unknown locations, no `.debug_line`, GNU/LLVM tools, inline stacks, timeout/eof, and cleanup on DSO destruction.
