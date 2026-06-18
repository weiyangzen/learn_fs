# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/virtual-memory.json

Purpose: defines 19 SP virtual-memory aliases for DTLB and ITLB misses, page walks, EPT walk cycles, ITLB flushes, large ITLB hits, and precise retired load/store DTLB misses.

Important APIs/types/functions: event families include `DTLB_LOAD_MISSES.*`, `DTLB_MISSES.*`, `ITLB_MISSES.*`, `EPT.WALK_CYCLES`, `ITLB_FLUSH`, `ITLB_MISS_RETIRED`, `LARGE_ITLB.HIT`, `MEM_LOAD_RETIRED.DTLB_MISS`, and `MEM_STORE_RETIRED.DTLB_MISS`. Retired TLB miss rows carry `PEBS`.

Control flow: `jevents.py` loads this topic, normalizes aliases, and generates C PMU rows. At runtime, perf chooses the SP table by CPUID and programs the corresponding event select/umask values.

State and persistence: static source file only. Runtime state is active counter or sampling configuration.

Dependencies and integration points: integrates with memory translation profiling, huge-page analysis, and virtualization investigations through EPT walk cycles. It complements `cache.json` retired memory rows and `memory.json` offcore locality events.

Risks: this SP file is slightly narrower than the DP counterpart, omitting `DTLB_LOAD_MISSES.LARGE_WALK_COMPLETED`, `DTLB_MISSES.PDE_MISS`, and `ITLB_MISSES.LARGE_WALK_COMPLETED`. Page-walk cycle aliases measure time spent walking, not just miss counts. PEBS support must match kernel PMU behavior.

Test signals: `jq empty`, generated `perf list tlb` aliases, TLB-thrashing workloads, huge-page comparisons, and VM workloads that exercise EPT walks.
