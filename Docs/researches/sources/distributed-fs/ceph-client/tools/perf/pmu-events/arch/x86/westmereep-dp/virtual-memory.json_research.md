# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/virtual-memory.json

Purpose: defines 22 DP aliases for DTLB, ITLB, EPT walks, large-page ITLB hits, and precise retired load/store TLB misses.

Important APIs/types/functions: event families include `DTLB_LOAD_MISSES.*`, `DTLB_MISSES.*`, `ITLB_MISSES.*`, `EPT.WALK_CYCLES`, `ITLB_FLUSH`, `ITLB_MISS_RETIRED`, `LARGE_ITLB.HIT`, `MEM_LOAD_RETIRED.DTLB_MISS`, and `MEM_STORE_RETIRED.DTLB_MISS`. PEBS appears on retired TLB miss events.

Control flow: the build converts the JSON records into generated PMU aliases under the `virtual-memory` topic. At runtime, perf resolves aliases after CPUID selection and configures the relevant event select/umask pairs. Precise retired aliases can be used by `perf record` for sampled attribution.

State and persistence: static event source only. Runtime state is PMU counter and sampling state; the file does not persist measurements.

Dependencies and integration points: integrates with memory-management profiling, huge-page tuning, virtualization analysis through `EPT.WALK_CYCLES`, and cache/memory locality diagnosis. Depends on the `westmereep-dp` mapfile entry and perf's PEBS handling.

Risks: DP includes three aliases absent from the SP virtual-memory assignment: `DTLB_LOAD_MISSES.LARGE_WALK_COMPLETED`, `DTLB_MISSES.PDE_MISS`, and `ITLB_MISSES.LARGE_WALK_COMPLETED`. Treating DP and SP tables as interchangeable can hide large-page or page-directory behavior. Walk-cycle events count time rather than miss instances.

Test signals: JSON validation, generated aliases in `perf list tlb`, synthetic workloads with TLB pressure, huge-page tests for large-walk aliases, and virtualization workloads for EPT walk cycles.
