<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/io.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/io.h

## Purpose
`io.h` is a header-only lightweight buffered read library for tools. It wraps a file descriptor with a caller-supplied buffer and provides character, numeric, delimiter, and line reads without using stdio.

## Important APIs, types, and functions
`struct io` stores fd, buffer pointers, timeout, and EOF/error state. Inline helpers are `io__init()`, `io__fill_buffer()`, `io__get_char()`, `io__get_hex()`, `io__get_dec()`, `io__getdelim()`, and `io__getline()`. Numeric functions parse positive hex/decimal values into `__u64`. Delimiter reads dynamically allocate or reallocate the output line.

## Control flow
Callers initialize `struct io` with an fd and buffer. `io__get_char()` refills the buffer when consumed. If `timeout_ms` is nonzero, refill first waits with `poll(POLLIN)`. Numeric readers consume until a nonmatching character and return that terminator. `io__getdelim()` consumes through a delimiter or EOF and returns the allocated length.

## State and persistence behavior
State is entirely in caller-owned `struct io` plus the caller-supplied buffer. `eof` is sticky after EOF, timeout, or read error. Lines allocated by `io__getdelim()` are caller-owned through `*line_out`.

## Dependencies and integration points
It depends on `poll(2)`, `read(2)`, libc allocation, errno, and Linux integer types. `fs.c` uses it for full-file string reads and bool parsing.

## Risks and edge cases
`io__get_char()` returns the negative refill return directly, so EOF and errors are both `-1` with errno only sometimes meaningful. `io__getdelim()` frees any existing `*line_out` and does not preserve caller capacity despite accepting `line_len_out`; callers cannot reuse buffers. Numeric overflow intentionally drops high bits. Timeout poll does not handle `POLLERR`/`POLLHUP` as readable.

## Test signals
Use pipes or temp files to test buffered reads across buffer boundaries, decimal/hex terminators, EOF behavior, timeouts, delimiter allocation growth, and interaction with `filename__read_str()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/io.h -->
