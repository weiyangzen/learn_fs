<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/seccomp/seccomp_benchmark.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/seccomp/seccomp_benchmark.c

## Purpose

Seccomp microbenchmark kselftest that measures getpid syscall overhead for native execution and several seccomp RET_ALLOW filter configurations, then checks expected relative costs.

## Important APIs, Types, and Functions

Uses kselftest.h output helpers, prctl/seccomp filter installation, BPF sock_filter programs, syscall(SYS_getpid), clock timing, sched affinity, /proc and sysctl text reads for environment reporting, and namespace-related build config indirectly through seccomp support.

## Control Flow and Integration

main pins affinity, prints environment and BPF sysctl settings, calibrates a sample count for a target duration, measures native getpid and one/two constant-action bitmap filters plus fuller filter chains, estimates incremental costs, and compares benchmark relationships with tolerance/skip handling for unsupported constant-action bitmap behavior.

## State and Persistence Behavior

No persistent state. It changes only the process seccomp filter state, which is irreversible for the process and intentionally cumulative across benchmark phases.

## Dependencies and Integration Points

Requires CONFIG_SECCOMP and CONFIG_SECCOMP_FILTER, usable prctl/seccomp APIs, stable timing, and kselftest harness helpers. The Makefile links libcap for the broader seccomp suite.

## Risks and Edge Cases

Performance thresholds are noisy on virtualized or loaded machines. Once filters are installed they cannot be removed, so measurement order matters. Kernel optimizations can legitimately change expected relative costs.

## Test Signals

Plan has seven kselftest results. Pass signals are positive timing samples, nonnegative estimated costs, and expected ordering between bitmap and full-filter paths; unsupported bitmap expectations are skipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/seccomp/seccomp_benchmark.c -->
