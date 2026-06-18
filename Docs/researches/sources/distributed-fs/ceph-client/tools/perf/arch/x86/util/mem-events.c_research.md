# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/mem-events.c

Purpose: defines x86 architecture-specific perf memory event templates for Intel and AMD PMUs.

Important APIs/types/functions: exports four `struct perf_mem_event` arrays: `perf_mem_events_intel`, `perf_mem_events_intel_aux`, `perf_mem_events_amd`, and `perf_mem_events_amd_ldlat`. Macro `E()` fills tag, printable name template, event name, load-latency support, and auxiliary event config. `MEM_LOADS_AUX` identifies Intel's auxiliary mem-loads event.

Control flow: there is no runtime control flow. The arrays are selected by `perf_pmu__arch_init()` in `pmu.c` depending on CPU vendor, PMU kind, and caps.

State and persistence: static global arrays define immutable event templates used in process memory. No persistence or dynamic allocation occurs.

Dependencies and integration: depends on `util/mem-events.h` for `struct perf_mem_event` and `PERF_MEM_EVENTS__MAX`. The local `mem-events.h` header exposes the arrays to x86 PMU initialization.

Risks: template strings are parse-events contracts; drift from PMU event names such as `mem-loads-aux`, `mem-loads`, `mem-stores`, or AMD `ibs_op` syntax breaks `perf mem`. Array order must match the generic `PERF_MEM_EVENTS__MAX` enum.

Test signals: `perf mem record` and `perf mem report` on Intel and AMD, Intel systems with and without `mem-loads-aux`, AMD IBS ldlat-capable PMUs, and parse-events validation of every template.
