# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/virtual-memory.json

Purpose: Defines three Clearwater Forest virtual-memory PMU aliases for completed page walks from load DTLB misses, store DTLB misses, and instruction TLB misses. It is a compact translation-pressure topic compared with the broader Cascade Lake X virtual-memory table.

Important APIs/types/functions: Each record uses counters `0,1,2,3,4,5,6,7`, `SampleAfterValue: 1000003`, and `UMask: 0xe`. `DTLB_LOAD_MISSES.WALK_COMPLETED` uses `EventCode: 0x08`; `DTLB_STORE_MISSES.WALK_COMPLETED` uses `EventCode: 0x49`; `ITLB_MISSES.WALK_COMPLETED` uses `EventCode: 0x85`. Public descriptions state that walks include all page sizes and page walks that fault.

Control flow: The build generator creates three core aliases in the Clearwater Forest table. At runtime, perf maps each alias to the corresponding core PMU event and counts completed page walks caused by data loads, data stores, or instruction fetches after misses in all TLB levels.

State and persistence behavior: Static build metadata only. Runtime counts are per-core and interval-based. The events count completed walks, including faulting walks, and do not distinguish 4K, 2M/4M, or 1G page sizes in this model file.

Dependencies: Depends on perf event generation and Clearwater Forest core PMU support for the standard DTLB/ITLB walk-completed encodings. It also depends on the x86 mapfile selecting the `clearwaterforest` model directory for family/model `GenuineIntel-6-DD`.

Integration points: Integrates with `pipeline.json` backend/frontend topdown events and `cache.json`/`memory.json` memory-latency events. These aliases identify translation overhead at a coarse level; if counts rise with backend bound or frontend bound slots, the workload may benefit from huge pages, locality changes, or reduced code/data footprint.

Risks: The file has only aggregate completed-walk events, so it cannot distinguish page size, STLB hits, walk pending cycles, or EPT overhead. Counts include faulting walks, so page-fault-heavy workloads can inflate translation metrics. Because all three rows share `UMask: 0xe`, a wrong event code is the main way load/store/instruction categories could be swapped.

Test signals: Validate JSON and generated aliases. `perf list` should expose all three walk-completed events. Hardware tests should compare TLB-friendly workloads with random page walks, huge-page versus 4K-page configurations, and instruction-footprint tests that selectively raise `ITLB_MISSES.WALK_COMPLETED`.
