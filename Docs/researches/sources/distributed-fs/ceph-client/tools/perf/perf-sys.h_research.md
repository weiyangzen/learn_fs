# sources/distributed-fs/ceph-client/tools/perf/perf-sys.h

### Purpose
`perf-sys.h` provides a tiny wrapper around the `perf_event_open` syscall for code that wants direct syscall access without libc support.

### Important APIs, Types, And Functions
It forward-declares `struct perf_event_attr` and defines `sys_perf_event_open()`, which calls `syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags)`.

### Control Flow
The inline function returns the raw syscall result: a file descriptor on success or `-1` with `errno` set on failure.

### State And Persistence
No state is stored.

### Dependencies And Integration Points
It depends on `<sys/syscall.h>` exposing `__NR_perf_event_open`, POSIX `syscall()`, and Linux perf event attributes. It is included by `perf.c` and other perf internals.

### Risks
Availability is Linux-specific. Callers must initialize `perf_event_attr` correctly and handle permission/sysctl failures.

### Test Signals
Build on supported Linux architectures and run perf commands that open events, checking error paths under restrictive `perf_event_paranoid` settings.
