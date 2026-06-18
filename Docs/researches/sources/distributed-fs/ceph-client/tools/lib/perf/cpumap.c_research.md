## sources/distributed-fs/ceph-client/tools/lib/perf/cpumap.c

Purpose: Implements reference-counted CPU maps for libperf.

Important APIs/functions: Allocation/lifecycle `perf_cpu_map__alloc/get/put/new/new_online_cpus/new_any_cpu/new_int`; parsing `perf_cpu_map__new()`; queries `nr`, `cpu`, `idx`, `has`, `equal`, `min`, `max`, any/empty helpers; set operations `perf_cpu_map__merge()` and `perf_cpu_map__intersect()`.

Control flow: Online CPU maps prefer sysfs `devices/system/cpu/online`, falling back to `sysconf`. String parsing accepts comma-separated integers and ranges, rejects duplicates and invalid ranges, sorts/trims, and uses `-1` for any CPU. Merge/intersect use sorted-array algorithms with reference-count optimizations for subsets.

State/persistence: CPU maps are heap objects with refcounts and optional sanitizer indirection from `rc_check.h`. No durable persistence.

Dependencies/integration: Uses Linux refcount, warnings/asserts, tools sysfs API, internal cpumap definitions, and public libperf cpumap API.

Risks: Parser rejects duplicates as invalid rather than deduplicating in-place. `MAX_NR_CPUS` only warns. This checkout contains a duplicated `struct perf_cpu result = {` line in `perf_cpu_map__cpu()`, which is a compile blocker unless corrected elsewhere. Ownership rules around `merge()` replacing `*orig` require caller care.

Test signals: Unit tests for parsing ranges, duplicates, empty string, online fallback, get/put balance under sanitizers, subset/merge/intersect correctness, any CPU behavior, and a plain build compile check for the duplicated declaration.
