# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/uncore-interconnect.json

Purpose: Defines 9 Ivy Bridge uncore ARB/interconnect aliases for tracker occupancy, tracker request allocation, and socket uncore clock counting. The file gives perf users named access to package interconnect pressure signals.

Important APIs/types/functions: Entries use the perf PMU event schema: `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `CounterMask`, `PerPkg`, and `BriefDescription`. Families are `UNC_ARB_COH_TRK_OCCUPANCY`, `UNC_ARB_COH_TRK_REQUESTS`, `UNC_ARB_TRK_OCCUPANCY`, `UNC_ARB_TRK_REQUESTS`, and `UNC_CLOCK.SOCKET`. Occupancy aliases use `CounterMask` to distinguish all occupancy cycles, cycles with any request, and cycles over half full. `UNC_CLOCK.SOCKET` uses the ARB fixed counter.

Control flow: Build-time perf tooling includes these records in the Ivy Bridge PMU event table. Runtime alias resolution maps names to the ARB uncore PMU, applies event select/unit mask/counter mask, and schedules on ARB counters. Users can combine request counts and occupancy cycles to infer average outstanding interconnect or coherency pressure.

State and persistence: Static repository data only. It persists event encodings and descriptions; runtime state lives in ARB uncore counters and perf's measurement buffers.

Dependencies/integration: Depends on Intel Ivy Bridge ARB uncore event semantics and the kernel's uncore PMU driver exposing ARB counters. It complements `uncore-cache.json` CBOX events and memory-controller events in other Ivy Bridge files. Derived metrics may use `UNC_CLOCK.SOCKET` as an uncore time base.

Risks: Occupancy events are cycle-weighted and can be misinterpreted as simple request counts. `CounterMask` thresholds are semantically important; removing or changing them changes the meaning while leaving the event code stable. Fixed-counter `UNC_CLOCK.SOCKET` has a different scheduling model from programmable ARB events. As package-scoped events, counts may not compose cleanly with per-thread core counters in the same perf report.

Test signals: Validate JSON fields and generated table rows, including `Unit: ARB`, `PerPkg: 1`, and `CounterMask` on thresholded events. On hardware, compare `UNC_ARB_TRK_REQUESTS.ALL` and occupancy aliases under memory-load stress versus idle, and verify `UNC_CLOCK.SOCKET` increments as a package clock source.
