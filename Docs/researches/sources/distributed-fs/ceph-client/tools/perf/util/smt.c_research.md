# sources/distributed-fs/ceph-client/tools/perf/util/smt.c

`smt.c` provides helpers for determining whether simultaneous multithreading is active and whether a recording covers complete physical cores. This is used by perf logic that can make stronger assumptions when all sibling hardware threads for a core are included.

`smt_on()` returns a cached boolean. On first call it tries to read `devices/system/cpu/smt/active` from sysfs; value `1` means SMT is active. If that sysfs file is unavailable, it falls back to `cpu_topology__smt_on(online_topology())`. The result is stored in static `cached_result`, guarded by static `cached`.

`core_wide(bool system_wide, const char *user_requested_cpu_list)` first rejects non-system-wide recordings because partial process/thread recordings cannot be assumed to cover whole cores. If SMT is off, it returns true because each core has only one active hardware thread. If SMT is on, it delegates to `cpu_topology__core_wide(online_topology(), user_requested_cpu_list)` to verify that the requested CPU set includes all siblings for each selected core.

State is limited to the cached SMT result. There is no persistence, but the cache means runtime SMT hotplug or sysfs changes after the first call are not observed.

Dependencies include sysfs helpers from `api/fs/fs.h`, CPU topology helpers from `cputopo.h`, and the public declarations in `smt.h`. Integration points are perf record/report logic that needs to choose core-wide behavior, especially for features sensitive to SMT sibling coverage.

Risks include stale cache after SMT state changes, fallback topology accuracy when sysfs is missing, and interpreting a null or unusual `user_requested_cpu_list` according to `cpu_topology__core_wide()` semantics. The helpers assume `online_topology()` is initialized and valid.

Test signals should cover systems with SMT enabled and disabled, missing sysfs fallback, CPU lists that include all siblings versus partial siblings, non-system-wide recordings, and behavior across repeated calls to confirm caching.
