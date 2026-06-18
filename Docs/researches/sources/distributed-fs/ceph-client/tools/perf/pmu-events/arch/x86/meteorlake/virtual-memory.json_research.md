# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/virtual-memory.json

Purpose: defines 37 Meteor Lake virtual-memory and TLB events for load DTLB misses, store DTLB misses, instruction TLB misses, and one atom-specific load-buffer retirement stall caused by a DTLB miss. The file covers STLB hits, page-walk active cycles, completed walks for all page sizes and specific 4K, 2M/4M, and 1G pages, and pending page-walk cycles.

Important APIs/types/functions: static event descriptors with `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `SampleAfterValue`, and `BriefDescription`. Like the pipeline file, it has hybrid `cpu_core` and `cpu_atom` rows with different event codes for similar semantic names, such as `DTLB_LOAD_MISSES.WALK_COMPLETED` on `0x12` for core and `0x08` for atom. Counter constraints differ between core (`0,1,2,3`) and atom (`0,1,2,3,4,5,6,7`).

Control flow: perf generation consumes the JSON and emits aliases for Meteor Lake. At runtime perf routes the selected event to the core or atom PMU, programs the DTLB/ITLB event code and umask, and counts page-walk activity or STLB hits while workloads run.

State and persistence: no local mutable state. Hardware PMU counters hold transient counts; perf records aggregate or sampled results. `SampleAfterValue` supplies default sampling periods for generated event metadata.

Dependencies and integration points: depends on x86 PMU support for Meteor Lake hybrid units and perf's JSON schema. Integrates with core pipeline stall events such as cycle activity and topdown backend-bound categories, and with kernel memory-management investigations where page size, TLB reach, and page-walk pressure matter.

Risks: semantically similar core and atom events have different encodings and sometimes different availability, so merging rows by name would be wrong. `WALK_ACTIVE`/`WALK_PENDING` are cycle-like occupancy measures, not completed walk counts. The atom `DTLB_STORE_MISSES.WALK_COMPLETED` description says 1G while the event name says all completions, which is a documentation-risk signal worth checking against Intel source material before metric use.

Test signals: validate JSON, inspect generated aliases for both PMU units, run `perf list` on Meteor Lake, and use workloads with large random memory footprints or instruction-cache pressure to move DTLB and ITLB walk counters. Huge-page versus 4K-page tests should change the page-size-specific completed-walk events.
