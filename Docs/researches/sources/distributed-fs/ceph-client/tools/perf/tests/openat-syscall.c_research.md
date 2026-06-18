# sources/distributed-fs/ceph-client/tools/perf/tests/openat-syscall.c

## Purpose
Tests basic per-thread counting of the `syscalls:sys_enter_openat` tracepoint for the current process.

## Important APIs, Types, and Functions
- `test__openat_syscall_event()` creates a thread map for current pid, creates a tracepoint evsel, opens it per thread, performs 111 `openat()` calls, reads CPU 0/thread 0 count, and checks exact count.
- Uses `evsel__newtp()`, `evsel__open_per_thread()`, `evsel__read_on_cpu()`, `perf_counts()`, and perf tracing error helpers.

## Control Flow
The test creates a thread map, creates `syscalls:sys_enter_openat`, skips if the tracepoint cannot be opened, opens it for the thread, loops 111 times opening and closing `/etc/passwd`, reads the counter, compares it with 111, closes perf fds, deletes evsel, and releases the thread map.

## State and Persistence
State is kernel perf event fd/count storage and transient file descriptors for `/etc/passwd`. No persistent files are created or modified.

## Dependencies and Integration Points
Depends on tracing path availability, perf_event permissions, thread maps, evsel count storage, and suite registration as `suite__openat_syscall_event`.

## Risks and Edge Cases
- Permission/tracepoint failures are treated as skips.
- Open return values are not checked before `close(fd)`, but syscall entry counting does not require successful opens.
- It reads CPU index 0/thread index 0, assuming per-thread open maps counts there.

## Test Signals
Passing confirms the tracepoint counter observes exactly the generated number of `openat()` syscalls for the current thread.
