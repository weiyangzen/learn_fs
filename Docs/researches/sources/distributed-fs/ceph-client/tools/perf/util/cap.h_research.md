# sources/distributed-fs/ceph-client/tools/perf/util/cap.h

Purpose: provides capability-check declarations and compatibility definitions for older kernel headers.

Important APIs/types: defines fallback values for `CAP_SYSLOG`, `CAP_PERFMON`, and `CAP_BPF`; declares `perf_cap__capable`.

Control flow: callers pass a capability id and receive support status plus whether root fallback was used.

State and persistence: no state.

Dependencies and integration: includes `stdbool.h` and `linux/capability.h`; used by perf permission checks.

Risks: fallback capability numbers must match Linux UAPI. Callers must pass valid `used_root` storage.

Test signals: build on old/new kernel headers and run perfmon/syslog/BPF permission tests.
