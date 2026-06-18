# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/memory-controller.json

Purpose: Defines 13 Zen 5 unified memory controller PMU events for MEMCLK cycles and ACTIVATE, PRECHARGE, CAS, and data-slot cycles split by all/read/write masks.

Important APIs/types/functions: The schema uses `EventName`, `EventCode`, `RdWrMask`, `Unit: UMCPMC`, `PerPkg: "1"`, and `PublicDescription`. Event families are `umc_mem_clk`, `umc_act_cmd.*`, `umc_pchg_cmd.*`, `umc_cas_cmd.*`, and `umc_data_slot_clks.*`.

Control flow: Perf maps these JSON aliases to UMC PMU counters. `recommended.json` consumes them for data bus utilization, CAS/read/write ratios, bandwidth, activate rate, and precharge rate.

State and persistence: No runtime state. The persistent behavior is package-level UMC event naming and read/write mask semantics.

Dependencies and integration: Integrates with the UMC PMU driver and recommended memory-controller metrics. Bandwidth formulas assume 64-byte CAS data and use `duration_time`; utilization divides data-slot clocks by two before comparing to `umc_mem_clk`.

Risks: Per-package UMC counters are topology-sensitive and can be overcounted if users aggregate across CPUs incorrectly. `RdWrMask` differs from the core event `UMask` schema, so generic validators must allow this field. Memory clock and CAS semantics must match DDR generation and controller documentation.

Test signals: Validate `perf list umc_`, run read/write memory bandwidth workloads, compare recommended UMC bandwidth to an external benchmark, and test read/write ratio behavior on read-only and write-heavy streams.
