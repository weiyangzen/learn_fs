# sources/distributed-fs/ceph-client/tools/perf/util/smt.h

`smt.h` declares perf helpers for SMT and core-wide recording checks. It exposes `smt_on()` and `core_wide()` to callers without exposing the sysfs/topology details used by the implementation.

`smt_on()` returns true when SMT, also known as hyperthreading, is enabled. `core_wide(bool system_wide, const char *user_requested_cpu_list)` returns true when the recording is system-wide and the requested CPU set covers all SMT threads for each core, or when SMT is disabled.

The header has no state of its own. State lives in the implementation's cache and in CPU topology/sysfs providers. There is no persistence.

Dependencies are intentionally minimal; the header only needs boolean support from the including context and include guards. Integration points are perf command code that needs a simple predicate before enabling core-wide optimizations or interpreting events as covering full cores.

Risks include callers assuming `core_wide()` only checks CPU lists while it also requires `system_wide`, or assuming `smt_on()` is dynamically refreshed. Compile units including this header must have `bool` available through prior includes or compiler defaults used by the perf tree.

Test signals should validate API use from C files, correct linkage to `smt.c`, and behavior for system-wide/non-system-wide and complete/partial CPU-list cases.
