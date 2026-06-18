# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/mem-events.h

Purpose: declares x86 memory event template arrays for PMU initialization.

Important APIs/types/functions: exports `perf_mem_events_intel`, `perf_mem_events_intel_aux`, `perf_mem_events_amd`, and `perf_mem_events_amd_ldlat`, all sized by `PERF_MEM_EVENTS__MAX`.

Control flow: header-only declarations guarded by `_X86_MEM_EVENTS_H`.

State and persistence: no state; provides external linkage contracts for arrays defined in `mem-events.c`.

Dependencies and integration: requires `struct perf_mem_event` and `PERF_MEM_EVENTS__MAX` to be visible through includers. Used by x86 `pmu.c`.

Risks: declarations must stay in sync with definitions; missing includes in a translation unit could make this header fragile.

Test signals: compile x86 perf with memory event support and verify `pmu.c` links against all four arrays.
