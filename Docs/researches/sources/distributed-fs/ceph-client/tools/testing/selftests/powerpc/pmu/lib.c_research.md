# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/lib.c

## Purpose
`lib.c` provides general PMU selftest helpers for parent/child synchronization, child lifecycle cleanup, address-range discovery from `/proc/self/maps`, CPU-consuming child workloads, and perf paranoid-level checks.

## Important APIs, Types, and Functions
Important functions are `sync_with_child()`, `wait_for_parent()`, `notify_parent()`, `notify_parent_of_error()`, `wait_for_child()`, `kill_child_and_wait()`, `parse_proc_maps()`, and the perf paranoia helper exported with `lib.h`. It also defines `libc` and `vdso` address ranges used by tests that reason about user-space mappings.

## Control Flow and State
Pipe helpers exchange fixed parent/child tokens and report child-side error tokens. Wait helpers reap or kill child processes. `parse_proc_maps()` scans current process mappings and records libc/vdso ranges. The CPU-eating child path synchronizes with its parent and spins until killed. State persists only in process globals and pipe/file descriptors.

## Dependencies and Integration Points
The file depends on POSIX pipes, wait/kill, CPU affinity headers, `/proc/self/maps`, `/proc/sys/kernel/perf_event_paranoid`, and kselftest `utils.h`. It supports PMU tests that need deterministic child process coordination or permission gating.

## Risks and Test Signals
Risks are deadlock if token order changes, false mapping detection across libc path variants, and permission checks that skip too broadly. Signals are clean parent/child handshakes, reliable child cleanup, parsed libc/vdso ranges, and accurate skip behavior under restrictive perf paranoid settings.
