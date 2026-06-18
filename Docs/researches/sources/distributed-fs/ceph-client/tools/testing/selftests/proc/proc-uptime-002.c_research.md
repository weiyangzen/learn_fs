# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-uptime-002.c

Purpose: validates the same `/proc/uptime` and `CLOCK_BOOTTIME` monotonic relationship while the process tries to move across all CPUs.

Important APIs and functions: raw `sched_getaffinity` and `sched_setaffinity` syscalls size and set CPU masks. It reuses `proc_uptime()` and `clock_boottime()`.

Control flow: dynamically grow an affinity mask until `sched_getaffinity` succeeds, open `/proc/uptime`, then iterate every possible CPU bit, set affinity to that single CPU if possible, read both clocks, and assert monotonic relationships.

State and persistence: dynamically allocated affinity mask only.

Dependencies and integration: depends on CPU affinity syscalls, proc uptime, and clock boottime. Nonexistent CPUs are ignored by allowing setaffinity failure.

Risks and test signals: tests per-CPU timekeeping consistency. Failures indicate clock/proc uptime going backward or divergent boottime accounting across CPUs.
