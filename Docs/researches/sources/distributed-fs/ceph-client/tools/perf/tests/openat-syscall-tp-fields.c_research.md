# sources/distributed-fs/ceph-client/tools/perf/tests/openat-syscall-tp-fields.c

## Purpose
Tests raw tracepoint sample parsing for `syscalls:sys_enter_openat`, specifically extracting the `flags` field from the tracepoint payload.

## Important APIs, Types, and Functions
- `test__syscall_openat_tp_fields()` configures an evlist for mmap/raw samples, creates a tracepoint evsel, opens and mmaps it for the current pid, generates one `openat()`, reads samples, parses them, and extracts `flags` through `evsel__intval()`.
- Uses `record_opts`, `evlist__create_maps()`, `evsel__config()`, `evlist__open()`, `evlist__mmap()`, `evlist__enable()`, `perf_mmap__read_event()`, and `evsel__parse_sample()`.

## Control Flow
The test builds an evlist with `sys_enter_openat`, creates maps for a mmap-using target, configures raw samples/no buffering, sets the thread pid to the current process, opens and maps, enables events, calls `openat(AT_FDCWD, "/etc/passwd", O_RDONLY | O_DIRECTORY)`, then polls up to five times while draining mmap buffers. On a `PERF_RECORD_SAMPLE`, it parses the sample, extracts `flags`, compares it to the generated flags, and returns `TEST_OK`.

## State and Persistence
State is perf event fds, mmap buffers, and one attempted `openat()` syscall. The opened fd is not captured or closed because the chosen flags should fail for `/etc/passwd` as a directory, but the tracepoint is generated either way. All evlist resources are deleted.

## Dependencies and Integration Points
Integrates raw tracepoint sample parsing, tracepoint field lookup, mmap polling, current-thread target maps, and test registration as `suite__syscall_openat_tp_fields`.

## Risks and Edge Cases
- Requires tracepoint access and perf permissions.
- Relies on the `flags` field name and layout in the kernel tracepoint format.
- Poll count is bounded; slow systems may fail with "no events".

## Test Signals
Passing confirms a raw tracepoint sample can be parsed and its `flags` field matches the syscall argument.
