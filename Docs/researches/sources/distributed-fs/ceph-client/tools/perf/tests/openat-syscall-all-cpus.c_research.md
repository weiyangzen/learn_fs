# sources/distributed-fs/ceph-client/tools/perf/tests/openat-syscall-all-cpus.c

## Purpose
Tests counting the `syscalls:sys_enter_openat` tracepoint across all online CPUs by pinning the process to each CPU and verifying per-CPU counts.

## Important APIs, Types, and Functions
- `test__openat_syscall_event_on_all_cpus()` creates a current-thread map, online CPU map, tracepoint evsel, opens it over all CPUs for the thread, generates `openat()` calls per CPU, reads counts per CPU, and validates expected values.
- Uses `perf_cpu_map__for_each_cpu()`, `sched_setaffinity()`, `evsel__open()`, `evsel__read_on_cpu()`, and `perf_counts()`.

## Control Flow
The test creates maps, opens `sys_enter_openat`, then iterates online CPUs. It skips CPUs outside `CPU_SETSIZE`, binds to each CPU, performs `111 + idx` openat calls on `/etc/passwd`, and clears the CPU from the affinity set. It assigns the cpumap to `evsel->core.cpus`, reads each CPU counter, and compares the count to the generated call count.

## State and Persistence
State includes process CPU affinity, perf event fds/counts, and transient file descriptors opened on `/etc/passwd`. FDs are closed immediately, and perf fds/maps are released. It does not restore the original affinity mask explicitly.

## Dependencies and Integration Points
Depends on tracing sysfs availability, perf_event permissions, CPU maps, thread maps, evsel counts, and test suite registration as `suite__openat_syscall_event_on_all_cpus`.

## Risks and Edge Cases
- CPUs above `CPU_SETSIZE` are ignored due to fixed `cpu_set_t`.
- Permission or tracepoint availability failures produce skips.
- Open failures for `/etc/passwd` are not checked before `close(fd)`, though the syscall still triggers the tracepoint.
- Original CPU affinity is not restored.

## Test Signals
Passing indicates per-CPU tracepoint counting attributes the generated openat calls to the CPU on which they were made.
