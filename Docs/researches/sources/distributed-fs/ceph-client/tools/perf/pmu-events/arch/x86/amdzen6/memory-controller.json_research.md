# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/memory-controller.json

Purpose: Defines 13 Zen 6 UMC PMU events for memory clock cycles and ACTIVATE, PRECHARGE, CAS, and data bus slot activity split by all/read/write masks.

Important APIs/types/functions: The event schema uses `EventName`, `EventCode`, `RdWrMask`, `Unit: UMCPMC`, `PerPkg: "1"`, and `PublicDescription`. Event families are `umc_mem_clk`, `umc_act_cmd.*`, `umc_pchg_cmd.*`, `umc_cas_cmd.*`, and `umc_data_slot_clks.*`.

Control flow: Perf maps these aliases to memory-controller PMU counters. Zen 6 recommended metrics use them for utilization, command rates, read/write ratios, and memory bandwidth.

State and persistence: No runtime state. The persistent API is package-level UMC event naming and read/write mask behavior.

Dependencies and integration: Integrates with the UMC PMU driver and Zen 6 recommended memory-controller metrics. Bandwidth formulas assume CAS commands transfer 64 bytes and divide by `duration_time`.

Risks: Per-package UMC aggregation is topology-sensitive. `RdWrMask` is a UMC-specific field, so generic event validators must not require `UMask`. Command-rate formulas depend on `umc_mem_clk` being available and measured in the same interval as command counters.

Test signals: Validate `perf list umc_`, run read-heavy and write-heavy memory streams, compare bandwidth metrics to external tools, and verify per-package aggregation on multi-socket systems.
