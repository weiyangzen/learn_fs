# subset-b-006609 Research

Grouped source research for AMD metric generation and Arm64 perf PMU event tables. Each source file has a marker-delimited section so reconciliation can split the report into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/amd_metrics.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/amd_metrics.py

## Purpose
This Python script generates AMD Zen perf metric JSON and metric-group description JSON for the `tools/perf/pmu-events` build. It builds higher-level metrics from AMD raw events, common cycle metrics, and perf software/MSR events, then prints either metric rows or metric group descriptions. The source was read as a complete 493-line file.

## Important APIs, Types, and Functions
Top-level inputs are argparse options `-metricgroups`, `model`, and `events_path`; globals include `_zen_model`, `interval_sec`, `ins`, `cycles`, and SMT-aware `smt_cycles`. Metric builders are `AmdBr()`, `AmdCtxSw()`, `AmdDtlb()`, `AmdItlb()`, `AmdLdSt()`, `AmdUpc()`, `Idle()`, `Rapl()`, and `UncoreL3()`. The script uses `Event`, `Metric`, `MetricGroup`, `Select`, `Literal`, `d_ratio()`, `max()`, `LoadEvents()`, `JsonEncodeMetric()`, and `JsonEncodeMetricGroupDescriptions()` from the local PMU metric framework.

## Control Flow, State, and Persistence
`main()` validates the event-tree directory, loads the selected `x86/<model>/` JSON files, derives `_zen_model` from names such as `amdzen1`, and builds one root `MetricGroup` containing all AMD metric groups. Individual builders create nested groups for branches, context switches, DTLB, ITLB, load/store throughput, uops per cycle, privilege-level cycles, idle time, package power, and L3 behavior. Several branches are model-sensitive: DTLB metrics are skipped for Zen 4 and newer, coalesced-page events appear for Zen 2 and newer, and some L1 TLB access formulas are Zen 1-3 only. The script persists nothing itself; build rules redirect stdout into generated `metrics.json` or `metricgroups.json` files.

## Dependencies and Integration Points
The `Build` file invokes this script for each `pmu-events/arch/x86/amdzen*` directory. It depends on local modules `metric.py` and `common_metrics.py`, and on the event names present in the AMD Zen JSON inputs. `LoadEvents()` validates referenced event names across the selected model tree, while the generated JSON is later parsed by `jevents.py` into perf's generated `pmu-events.c` tables. Runtime integration is through `perf stat -M`, metric groups, MSR PMUs (`msr/mperf/`, `msr/tsc/`), RAPL `power/energy-pkg/`, and AMD core/uncore PMU events.

## Risks and Test Signals
Risks include event-name drift across Zen generations, model gating that silently drops or includes invalid formulas, SMT scaling assumptions in `smt_cycles`, division by unavailable or zero-count events, RAPL scaling accuracy, and metric semantics changing when AMD event aliases change. Test signals include running the script for every `amdzen*` model, comparing generated JSON diffs, executing `metric_test.py`, running `jevents.py`, checking `perf list --metrics` for generated names, and smoke-testing representative `perf stat -M lpm_*` groups on matching AMD hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/amd_metrics.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/branch.json

## Purpose
This JSON file defines 5 Ampere ampereone branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 18-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`, `BR_MIS_PRED`, `BR_PRED`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/bus.json

## Purpose
This JSON file defines 10 Ampere ampereone CPU cycle, bus cycle, and core-to-uncore access events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 33-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (10). It contains 10 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `CPU_CYCLES`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`, `BUS_ACCESS_SHARED`, `BUS_ACCESS_NOT_SHARED`, `BUS_ACCESS_NORMAL`, `BUS_ACCESS_PERIPH`, `BUS_ACCESS`, `CNT_CYCLES`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 10 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/cache.json

## Purpose
This JSON file defines 33 Ampere ampereone cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 104-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (33), `Errata` (1), `BriefDescription` (1). It contains 33 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `L1D_CACHE_RD`, `L1D_CACHE_WR`, `L1D_CACHE_REFILL_RD`, `L1D_CACHE_INVAL`, `L1D_TLB_REFILL_RD`, `L1D_TLB_REFILL_WR`, `L2D_CACHE_RD`, `L2D_CACHE_WR`, `L2D_CACHE_REFILL_RD`, `L2D_CACHE_REFILL_WR`, `L2D_CACHE_WB_VICTIM`, `L2D_CACHE_WB_CLEAN`, and 21 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 1 entries carry errata notes: `Errata AC03_CPU_41`; 32 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/core-imp-def.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/core-imp-def.json

## Purpose
This JSON file defines 96 Ampere ampereone implementation-defined core events for front-end, back-end, cache, branch, MMU, and microarchitectural analysis for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 579-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (96), `EventCode` (96), `EventName` (96), `BriefDescription` (96). It contains 0 `ArchStdEvent` aliases, 96 named implementation-defined events, and 96 encoded events. Event or alias names include `L2_PREFETCH_REFILL`, `L2_PREFETCH_UPGRADE`, `BPU_HIT_BTB`, `BPU_CONDITIONAL_BRANCH_HIT_BTB`, `BPU_HIT_INDIRECT_PREDICTOR`, `BPU_HIT_RSB`, `BPU_UNCONDITIONAL_BRANCH_MISS_BTB`, `BPU_BRANCH_NO_HIT`, `BPU_HIT_BTB_AND_MISPREDICT`, `BPU_CONDITIONAL_BRANCH_HIT_BTB_AND_MISPREDICT`, `BPU_INDIRECT_BRANCH_HIT_BTB_AND_MISPREDICT`, `BPU_HIT_RSB_AND_MISPREDICT`, and 84 more. Implementation-defined codes run from `0x10A` to `0xD90D` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/core-imp-def.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/exception.json

## Purpose
This JSON file defines 14 Ampere ampereone exception, interrupt, abort, trap, and return events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 45-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (14). It contains 14 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, `EXC_HVC`, `EXC_TRAP_PABORT`, `EXC_TRAP_DABORT`, `EXC_TRAP_OTHER`, `EXC_TRAP_IRQ`, `EXC_TRAP_FIQ`, and 2 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 14 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/instruction.json

## Purpose
This JSON file defines 27 Ampere ampereone retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 87-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (26), `PublicDescription` (1), `EventCode` (1), `EventName` (1), `BriefDescription` (1). It contains 26 `ArchStdEvent` aliases, 1 named implementation-defined events, and 1 encoded events. Event or alias names include `SW_INCR`, `ST_RETIRED`, `OP_SPEC`, `LD_SPEC`, `ST_SPEC`, `LDST_SPEC`, `DP_SPEC`, `ASE_SPEC`, `VFP_SPEC`, `PC_WRITE_SPEC`, `BR_IMMED_RETIRED`, `BR_RETURN_RETIRED`, and 15 more. Implementation-defined codes run from `0x100` to `0x100` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 26 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/intrinsic.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/intrinsic.json

## Purpose
This JSON file defines 4 Ampere ampereone exclusive load/store intrinsic events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 15-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (4). It contains 4 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `LDREX_SPEC`, `STREX_PASS_SPEC`, `STREX_FAIL_SPEC`, `STREX_SPEC`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/intrinsic.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/memory.json

## Purpose
This JSON file defines 14 Ampere ampereone load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 47-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (14), `Errata` (1), `BriefDescription` (1). It contains 14 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `LD_RETIRED`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`, `LD_ALIGN_LAT`, `ST_ALIGN_LAT`, `MEM_ACCESS`, `MEMORY_ERROR`, `LDST_ALIGN_LAT`, `MEM_ACCESS_CHECKED`, and 2 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 1 entries carry errata notes: `Errata AC03_CPU_52`; 13 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/metrics.json

## Purpose
This JSON file defines 56 derived perf metrics for Ampere ampereone. The expressions cover derived perf metrics built from event expressions and are consumed by the `pmu-events` generator as metric rows rather than raw counter encodings. The source was read as a complete 387-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `MetricExpr` (55), `MetricName` (54), `BriefDescription` (54), `MetricGroup` (54), `ScaleUnit` (51), `ArchStdEvent` (2), `DefaultMetricgroupName` (2). Metric names include `branch_miss_pred_rate`, `bus_utilization`, `l1d_cache_miss_ratio`, `l1i_cache_miss_ratio`, `Miss_Ratio;l1d_cache_read_miss`, `l2_cache_miss_ratio`, `l1i_cache_read_miss_rate`, `l2d_cache_read_miss_rate`, `l1d_cache_miss_mpki`, `l1i_cache_miss_mpki`, `simd_percentage`, `crypto_percentage`, and 44 more. Metric groups include `branch`, `Bus`, `Miss_Ratio;L1D_Cache_Effectiveness`, `Miss_Ratio;L1I_Cache_Effectiveness`, `Cache`, `Miss_Ratio;L2_Cache_Effectiveness`, `Operation_Mix`, `InstructionMix`, `General`, `PEutilization`, and 7 more. `MetricExpr` references raw events such as architectural aliases, `duration_time`, and model-defined event names; `ScaleUnit` controls perf's display scaling.

## Control Flow, State, and Persistence
`jevents.py` parses each `MetricExpr` through `metric.ParsePerfJson()`, simplifies it, and emits generated `pmu-events.c` metric tables. At runtime `perf list` and metricgroup code expose these names and evaluate the expressions from simultaneously counted events. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include stale event names inside expressions, denominator-zero or multiplexing-sensitive ratios, wrong scale units, metrics that depend on events omitted from this CPU directory, and semantic drift when a raw event definition changes. Test signals include `metric_test.py`, `jevents.py` generation, `perf list --metrics`, and sample `perf stat -M` runs on the matching CPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/pipeline.json

## Purpose
This JSON file defines 7 Ampere ampereone front-end, back-end, resource, TLB, and pipeline stall events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 30-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (7), `Errata` (3), `BriefDescription` (3). It contains 7 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 3 entries carry errata notes: `Errata AC03_CPU_29`, `Errata AC03_CPU_29`, `Errata AC03_CPU_29`; 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/spe.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/spe.json

## Purpose
This JSON file defines 4 Ampere ampereone Statistical Profiling Extension sampling events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 15-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (4). It contains 4 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereone/spe.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/branch.json

## Purpose
This JSON file defines 23 Ampere ampereonex branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 126-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (18), `EventCode` (18), `EventName` (18), `BriefDescription` (18), `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 18 named implementation-defined events, and 18 encoded events. Event or alias names include `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`, `BR_MIS_PRED`, `BR_PRED`, `BR_SKIP_RETIRED`, `BR_IMMED_TAKEN_RETIRED`, `BR_INDNR_TAKEN_RETIRED`, `BR_IMMED_PRED_RETIRED`, `BR_IMMED_MIS_PRED_RETIRED`, `BR_IND_PRED_RETIRED`, `BR_IND_MIS_PRED_RETIRED`, and 11 more. Implementation-defined codes run from `0x8107` to `0x811f` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/bus.json

## Purpose
This JSON file defines 6 Ampere ampereonex CPU cycle, bus cycle, and core-to-uncore access events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 21-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (6). It contains 6 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `CPU_CYCLES`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`, `BUS_ACCESS`, `CNT_CYCLES`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 6 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/cache.json

## Purpose
This JSON file defines 54 Ampere ampereonex cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 209-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (40), `BriefDescription` (15), `PublicDescription` (14), `EventCode` (14), `EventName` (14), `Errata` (1). It contains 40 `ArchStdEvent` aliases, 14 named implementation-defined events, and 14 encoded events. Event or alias names include `L1D_CACHE_RD`, `L1D_CACHE_WR`, `L1D_CACHE_REFILL_RD`, `L1D_CACHE_INVAL`, `L1D_TLB_REFILL_RD`, `L1D_TLB_REFILL_WR`, `L2D_CACHE_RD`, `L2D_CACHE_WR`, `L2D_CACHE_REFILL_RD`, `L2D_CACHE_REFILL_WR`, `L2D_CACHE_WB_VICTIM`, `L2D_CACHE_WB_CLEAN`, and 42 more. Implementation-defined codes run from `0x8140` to `0xD703` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 1 entries carry errata notes: `Errata AC04_CPU_1`; 39 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/core-imp-def.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/core-imp-def.json

## Purpose
This JSON file defines 77 Ampere ampereonex implementation-defined core events for front-end, back-end, cache, branch, MMU, and microarchitectural analysis for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 465-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (77), `EventCode` (77), `EventName` (77), `BriefDescription` (77). It contains 0 `ArchStdEvent` aliases, 77 named implementation-defined events, and 77 encoded events. Event or alias names include `L2_PREFETCH_REFILL`, `L2_PREFETCH_UPGRADE`, `BPU_HIT_BTB`, `BPU_CONDITIONAL_BRANCH_HIT_BTB`, `BPU_HIT_INDIRECT_PREDICTOR`, `BPU_HIT_RSB`, `BPU_UNCONDITIONAL_BRANCH_MISS_BTB`, `BPU_BRANCH_NO_HIT`, `BPU_HIT_BTB_AND_MISPREDICT`, `BPU_CONDITIONAL_BRANCH_HIT_BTB_AND_MISPREDICT`, `BPU_INDIRECT_BRANCH_HIT_BTB_AND_MISPREDICT`, `BPU_HIT_RSB_AND_MISPREDICT`, and 65 more. Implementation-defined codes run from `0x10A` to `0xda00` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/core-imp-def.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/exception.json

## Purpose
This JSON file defines 15 Ampere ampereonex exception, interrupt, abort, trap, and return events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 48-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (15). It contains 15 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, `EXC_HVC`, `EXC_TRAP_PABORT`, `EXC_TRAP_DABORT`, `EXC_TRAP_OTHER`, `EXC_TRAP_IRQ`, `EXC_TRAP_FIQ`, and 3 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 15 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/instruction.json

## Purpose
This JSON file defines 34 Ampere ampereonex retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 129-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (26), `PublicDescription` (8), `EventCode` (8), `EventName` (8), `BriefDescription` (8). It contains 26 `ArchStdEvent` aliases, 8 named implementation-defined events, and 8 encoded events. Event or alias names include `SW_INCR`, `ST_RETIRED`, `LD_SPEC`, `ST_SPEC`, `LDST_SPEC`, `DP_SPEC`, `ASE_SPEC`, `VFP_SPEC`, `PC_WRITE_SPEC`, `BR_IMMED_RETIRED`, `BR_RETURN_RETIRED`, `CRYPTO_SPEC`, and 22 more. Implementation-defined codes run from `0xd210` to `0xd10a` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 26 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/intrinsic.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/intrinsic.json

## Purpose
This JSON file defines 4 Ampere ampereonex exclusive load/store intrinsic events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 15-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (4). It contains 4 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `LDREX_SPEC`, `STREX_PASS_SPEC`, `STREX_FAIL_SPEC`, `STREX_SPEC`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/intrinsic.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/memory.json

## Purpose
This JSON file defines 12 Ampere ampereonex load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 44-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (11), `BriefDescription` (2), `Errata` (1), `PublicDescription` (1), `EventCode` (1), `EventName` (1). It contains 11 `ArchStdEvent` aliases, 1 named implementation-defined events, and 1 encoded events. Event or alias names include `LD_RETIRED`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `LD_ALIGN_LAT`, `ST_ALIGN_LAT`, `MEM_ACCESS`, `MEMORY_ERROR`, `LDST_ALIGN_LAT`, `MEM_ACCESS_CHECKED`, `MEM_ACCESS_CHECKED_RD`, `MEM_ACCESS_CHECKED_WR`, `BPU_FLUSH_MEM_FAULT`. Implementation-defined codes run from `0x121` to `0x121` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 1 entries carry errata notes: `Errata AC04_CPU_21`; 10 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/metrics.json

## Purpose
This JSON file defines 64 derived perf metrics for Ampere ampereonex. The expressions cover derived perf metrics built from event expressions and are consumed by the `pmu-events` generator as metric rows rather than raw counter encodings. The source was read as a complete 443-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `MetricExpr` (63), `MetricName` (62), `BriefDescription` (62), `MetricGroup` (62), `ScaleUnit` (59), `ArchStdEvent` (2), `DefaultMetricgroupName` (2). Metric names include `branch_miss_pred_rate`, `bus_utilization`, `l1d_cache_miss_ratio`, `l1i_cache_miss_ratio`, `Miss_Ratio;l1d_cache_read_miss`, `l2_cache_miss_ratio`, `l1i_cache_read_miss_rate`, `l2d_cache_read_miss_rate`, `l1d_cache_miss_mpki`, `l1i_cache_miss_mpki`, `simd_percentage`, `crypto_percentage`, and 52 more. Metric groups include `branch`, `Bus`, `Miss_Ratio;L1D_Cache_Effectiveness`, `Miss_Ratio;L1I_Cache_Effectiveness`, `Cache`, `Miss_Ratio;L2_Cache_Effectiveness`, `Operation_Mix`, `InstructionMix`, `General`, `PEutilization`, and 8 more. `MetricExpr` references raw events such as architectural aliases, `duration_time`, and model-defined event names; `ScaleUnit` controls perf's display scaling.

## Control Flow, State, and Persistence
`jevents.py` parses each `MetricExpr` through `metric.ParsePerfJson()`, simplifies it, and emits generated `pmu-events.c` metric tables. At runtime `perf list` and metricgroup code expose these names and evaluate the expressions from simultaneously counted events. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include stale event names inside expressions, denominator-zero or multiplexing-sensitive ratios, wrong scale units, metrics that depend on events omitted from this CPU directory, and semantic drift when a raw event definition changes. Test signals include `metric_test.py`, `jevents.py` generation, `perf list --metrics`, and sample `perf stat -M` runs on the matching CPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/mmu.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/mmu.json

## Purpose
This JSON file defines 28 Ampere ampereonex MMU page-table-walk and translation-cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 171-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `EventCode` (28), `EventName` (28), `BriefDescription` (28), `PublicDescrition` (16), `PublicDescription` (12). It contains 0 `ArchStdEvent` aliases, 28 named implementation-defined events, and 28 encoded events. Event or alias names include `MMU_D_OTB_ALLOC`, `MMU_D_TRANS_CACHE_HIT_S1L2_WALK`, `MMU_D_TRANS_CACHE_HIT_S1L1_WALK`, `MMU_D_TRANS_CACHE_HIT_S1L0_WALK`, `MMU_D_TRANS_CACHE_HIT_S2L2_WALK`, `MMU_D_TRANS_CACHE_HIT_S2L1_WALK`, `MMU_D_TRANS_CACHE_HIT_S2L0_WALK`, `MMU_D_S1_WALK_CACHE_LOOKUP`, `MMU_D_S1_WALK_CACHE_REFILL`, `MMU_D_S2_WALK_CACHE_LOOKUP`, `MMU_D_S2_WALK_CACHE_REFILL`, `MMU_D_S1_WALK_FAULT`, and 16 more. Implementation-defined codes run from `0xD800` to `0xD90D` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include the file uses the misspelled `PublicDescrition` key on some entries. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/mmu.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/pipeline.json

## Purpose
This JSON file defines 9 Ampere ampereonex front-end, back-end, resource, TLB, and pipeline stall events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 42-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (7), `BriefDescription` (5), `Errata` (3), `PublicDescription` (2), `EventCode` (2), `EventName` (2). It contains 7 `ArchStdEvent` aliases, 2 named implementation-defined events, and 2 encoded events. Event or alias names include `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`, `STALL_FRONTEND_TLB`, `STALL_BACKEND_TLB`. Implementation-defined codes run from `0x815c` to `0x8167` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 3 entries carry errata notes: `Errata AC03_CPU_29`, `Errata AC03_CPU_29`, `Errata AC03_CPU_29`; 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/spe.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/spe.json

## Purpose
This JSON file defines 4 Ampere ampereonex Statistical Profiling Extension sampling events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 15-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (4). It contains 4 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/ampereonex/spe.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/branch.json

## Purpose
This JSON file defines 5 Ampere emag branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 20-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (5), `BriefDescription` (2). It contains 5 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`, `BR_MIS_PRED`, `BR_PRED`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 3 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/bus.json

## Purpose
This JSON file defines 7 Ampere emag CPU cycle, bus cycle, and core-to-uncore access events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 24-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (7). It contains 7 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `BUS_ACCESS_RD`, `BUS_ACCESS_WR`, `BUS_ACCESS_SHARED`, `BUS_ACCESS_NOT_SHARED`, `BUS_ACCESS_NORMAL`, `BUS_ACCESS_PERIPH`, `BUS_ACCESS`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 7 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/cache.json

## Purpose
This JSON file defines 38 Ampere emag cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 162-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (24), `PublicDescription` (16), `BriefDescription` (15), `EventCode` (14), `EventName` (14). It contains 24 `ArchStdEvent` aliases, 14 named implementation-defined events, and 14 encoded events. Event or alias names include `L1D_CACHE_RD`, `L1D_CACHE_WR`, `L1D_CACHE_REFILL_RD`, `L1D_CACHE_INVAL`, `L1D_TLB_REFILL_RD`, `L1D_TLB_REFILL_WR`, `L2D_CACHE_RD`, `L2D_CACHE_WR`, `L2D_CACHE_REFILL_RD`, `L2D_CACHE_REFILL_WR`, `L2D_CACHE_WB_VICTIM`, `L2D_CACHE_WB_CLEAN`, and 26 more. Implementation-defined codes run from `0x34` to `0x116` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 23 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/clock.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/clock.json

## Purpose
This JSON file defines 3 Ampere emag core and implementation-defined clock or wait-cycle events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 19-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (3), `EventCode` (2), `EventName` (2), `BriefDescription` (2), `ArchStdEvent` (1). It contains 1 `ArchStdEvent` aliases, 2 named implementation-defined events, and 2 encoded events. Event or alias names include `CPU_CYCLES`, `FSU_CLOCK_OFF_CYCLES`, `Wait_CYCLES`. Implementation-defined codes run from `0x101` to `0x110` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 1 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/clock.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/exception.json

## Purpose
This JSON file defines 14 Ampere emag exception, interrupt, abort, trap, and return events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 45-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (14). It contains 14 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, `EXC_HVC`, `EXC_TRAP_PABORT`, `EXC_TRAP_DABORT`, `EXC_TRAP_OTHER`, `EXC_TRAP_IRQ`, `EXC_TRAP_FIQ`, and 2 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 14 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/instruction.json

## Purpose
This JSON file defines 21 Ampere emag retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 74-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (20), `PublicDescription` (4), `BriefDescription` (3), `EventCode` (1), `EventName` (1). It contains 20 `ArchStdEvent` aliases, 1 named implementation-defined events, and 1 encoded events. Event or alias names include `LD_SPEC`, `ST_SPEC`, `LDST_SPEC`, `DP_SPEC`, `ASE_SPEC`, `VFP_SPEC`, `PC_WRITE_SPEC`, `CRYPTO_SPEC`, `ISB_SPEC`, `DSB_SPEC`, `DMB_SPEC`, `RC_LD_SPEC`, and 9 more. Implementation-defined codes run from `0x100` to `0x100` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 18 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/intrinsic.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/intrinsic.json

## Purpose
This JSON file defines 4 Ampere emag exclusive load/store intrinsic events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 15-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (4). It contains 4 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `LDREX_SPEC`, `STREX_PASS_SPEC`, `STREX_FAIL_SPEC`, `STREX_SPEC`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/intrinsic.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/memory.json

## Purpose
This JSON file defines 7 Ampere emag load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 25-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (7), `PublicDescription` (1). It contains 7 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`, `MEM_ACCESS`, `MEMORY_ERROR`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 7 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/pipeline.json

## Purpose
This JSON file defines 8 Ampere emag front-end, back-end, resource, TLB, and pipeline stall events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 51-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (8), `EventCode` (8), `EventName` (8), `BriefDescription` (8). It contains 0 `ArchStdEvent` aliases, 8 named implementation-defined events, and 8 encoded events. Event or alias names include `DECODE_STALL`, `DISPATCH_STALL`, `IXA_STALL`, `IXB_STALL`, `BX_STALL`, `LX_STALL`, `SX_STALL`, `FX_STALL`. Implementation-defined codes run from `0x108` to `0x10f` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/ampere/emag/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cmn/sys/cmn.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cmn/sys/cmn.json

## Purpose
This JSON file defines 33 Arm CMN uncore mesh events for the system PMU. It maps HN-F, RN-I/D, SBSX, HN-I, and related node events to `arm_cmn` event IDs and compatibility filters. The source was read as a complete 267-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `EventName` (33), `EventidCode` (33), `NodeType` (33), `BriefDescription` (33), `Unit` (33), `Compat` (33). Event names include `hnf_cache_miss`, `hnf_slc_sf_cache_access`, `hnf_cache_fill`, `hnf_pocq_retry`, `hnf_pocq_reqs_recvd`, `hnf_sf_hit`, `hnf_sf_evictions`, `hnf_dir_snoops_sent`, `hnf_brd_snoops_sent`, `hnf_slc_eviction`, `hnf_slc_fill_invalid_way`, `hnf_mc_retries`, and 21 more. Event ID values range from 0x1 to 0x30 in file order. Units are `arm_cmn`; compat patterns are `(434|436|43c|43a).*`.

## Control Flow, State, and Persistence
`jevents.py` handles `EventidCode`, `NodeType`, `Unit`, and `Compat` as uncore PMU metadata rather than core PMU event aliases. Generated tables let perf match the running CMN PMU implementation and expose node-specific events only when the compatible hardware is present. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include wrong node type encodings, compatibility regexes that hide valid CMN revisions or expose unsupported ones, and bandwidth/retry events whose units are misread as core events. Test signals include JSON parsing, `jevents.py` output inspection, `perf list arm_cmn`, and hardware smoke tests on supported CMN revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cmn/sys/cmn.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cmn/sys/metric.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cmn/sys/metric.json

## Purpose
This JSON file defines 8 derived perf metrics for Arm cmn. The expressions cover derived CMN uncore perf metrics built from event expressions and are consumed by the `pmu-events` generator as metric rows rather than raw counter encodings. The source was read as a complete 75-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `MetricName` (8), `BriefDescription` (8), `MetricGroup` (8), `MetricExpr` (8), `ScaleUnit` (8), `Unit` (8), `Compat` (8). Metric names include `slc_miss_rate`, `hnf_message_retry_rate`, `sf_hit_rate`, `mc_message_retry_rate`, `rni_actual_read_bandwidth.all`, `rni_actual_write_bandwidth.all`, `rni_retry_rate`, `sbsx_actual_write_bandwidth.all`. Metric groups include `cmn`. `MetricExpr` references raw events such as architectural aliases, `duration_time`, and model-defined event names; `ScaleUnit` controls perf's display scaling.

## Control Flow, State, and Persistence
`jevents.py` parses each `MetricExpr` through `metric.ParsePerfJson()`, simplifies it, and emits generated `pmu-events.c` metric tables. At runtime `perf list` and metricgroup code expose these names and evaluate the expressions from simultaneously counted events. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include stale event names inside expressions, denominator-zero or multiplexing-sensitive ratios, wrong scale units, metrics that depend on events omitted from this CPU directory, and semantic drift when a raw event definition changes. Test signals include `metric_test.py`, `jevents.py` generation, `perf list --metrics`, and sample `perf stat -M` runs on the matching CPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cmn/sys/metric.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/branch.json

## Purpose
This JSON file defines 3 Arm cortex-a34 branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 12-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (3). It contains 3 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `BR_MIS_PRED`, `BR_PRED`, `BR_INDIRECT_SPEC`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 3 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/bus.json

## Purpose
This JSON file defines 5 Arm cortex-a34 CPU cycle, bus cycle, and core-to-uncore access events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 18-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/cache.json

## Purpose
This JSON file defines 10 Arm cortex-a34 cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 33-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (10). It contains 10 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 10 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/exception.json

## Purpose
This JSON file defines 4 Arm cortex-a34 exception, interrupt, abort, trap, and return events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 15-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (4). It contains 4 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_IRQ`, `EXC_FIQ`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/instruction.json

## Purpose
This JSON file defines 9 Arm cortex-a34 retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 30-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (9). It contains 9 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `SW_INCR`, `LD_RETIRED`, `ST_RETIRED`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `PC_WRITE_RETIRED`, `BR_IMMED_RETIRED`, `BR_RETURN_RETIRED`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 9 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/memory.json

## Purpose
This JSON file defines 2 Arm cortex-a34 load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 9-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (2). It contains 2 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `UNALIGNED_LDST_RETIRED`, `MEM_ACCESS`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 2 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a34/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/branch.json

## Purpose
This JSON file defines 3 Arm cortex-a35 branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 12-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (3). It contains 3 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `BR_MIS_PRED`, `BR_PRED`, `BR_INDIRECT_SPEC`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 3 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/bus.json

## Purpose
This JSON file defines 5 Arm cortex-a35 CPU cycle, bus cycle, and core-to-uncore access events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 18-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/cache.json

## Purpose
This JSON file defines 10 Arm cortex-a35 cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 33-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (10). It contains 10 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 10 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/exception.json

## Purpose
This JSON file defines 4 Arm cortex-a35 exception, interrupt, abort, trap, and return events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 15-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (4). It contains 4 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_IRQ`, `EXC_FIQ`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/instruction.json

## Purpose
This JSON file defines 14 Arm cortex-a35 retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 45-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (14). It contains 14 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `SW_INCR`, `LD_RETIRED`, `ST_RETIRED`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `PC_WRITE_RETIRED`, `BR_IMMED_RETIRED`, `BR_RETURN_RETIRED`, `INST_SPEC`, `DP_SPEC`, `ASE_SPEC`, and 2 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 14 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/memory.json

## Purpose
This JSON file defines 2 Arm cortex-a35 load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 9-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (2). It contains 2 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `UNALIGNED_LDST_RETIRED`, `MEM_ACCESS`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 2 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a35/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/branch.json

## Purpose
This JSON file defines 12 Arm cortex-a510 branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 60-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (7), `EventCode` (7), `EventName` (7), `BriefDescription` (7), `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 7 named implementation-defined events, and 7 encoded events. Event or alias names include `BR_MIS_PRED`, `BR_PRED`, `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`, `BR_COND_PRED`, `BR_INDIRECT_MIS_PRED`, `BR_INDIRECT_ADDR_MIS_PRED`, `BR_COND_MIS_PRED`, `BR_INDIRECT_ADDR_PRED`, `BR_RETURN_ADDR_PRED`, `BR_RETURN_ADDR_MIS_PRED`. Implementation-defined codes run from `0xC9` to `0xCF` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/bus.json

## Purpose
This JSON file defines 5 Arm cortex-a510 CPU cycle, bus cycle, and core-to-uncore access events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 18-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/cache.json

## Purpose
This JSON file defines 48 Arm cortex-a510 cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 183-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (36), `PublicDescription` (12), `EventCode` (12), `EventName` (12), `BriefDescription` (12). It contains 36 `ArchStdEvent` aliases, 12 named implementation-defined events, and 12 encoded events. Event or alias names include `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_ALLOCATE`, `L1D_TLB`, and 36 more. Implementation-defined codes run from `0xC1` to `0xD6` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 36 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/exception.json

## Purpose
This JSON file defines 4 Arm cortex-a510 exception, interrupt, abort, trap, and return events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 15-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (4). It contains 4 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_IRQ`, `EXC_FIQ`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/instruction.json

## Purpose
This JSON file defines 31 Arm cortex-a510 retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 96-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (31). It contains 31 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `LD_RETIRED`, `ST_RETIRED`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `PC_WRITE_RETIRED`, `BR_IMMED_RETIRED`, `BR_RETURN_RETIRED`, `INST_SPEC`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, `BR_MIS_PRED_RETIRED`, and 19 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 31 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/memory.json

## Purpose
This JSON file defines 10 Arm cortex-a510 load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 33-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (10). It contains 10 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `MEM_ACCESS`, `REMOTE_ACCESS_RD`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `LDST_ALIGN_LAT`, `LD_ALIGN_LAT`, `ST_ALIGN_LAT`, `MEM_ACCESS_CHECKED`, `MEM_ACCESS_CHECKED_RD`, `MEM_ACCESS_CHECKED_WR`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 10 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/pipeline.json

## Purpose
This JSON file defines 21 Arm cortex-a510 front-end, back-end, resource, TLB, and pipeline stall events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 108-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (14), `EventCode` (14), `EventName` (14), `BriefDescription` (14), `ArchStdEvent` (7). It contains 7 `ArchStdEvent` aliases, 14 named implementation-defined events, and 14 encoded events. Event or alias names include `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_FRONTEND_CACHE`, `STALL_FRONTEND_TLB`, `STALL_FRONTEND_PDERR`, `STALL_BACKEND_ILOCK`, `STALL_BACKEND_ILOCK_ADDR`, `STALL_BACKEND_ILOCK_VPU`, and 9 more. Implementation-defined codes run from `0xE1` to `0xEE` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 7 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/trace.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/trace.json

## Purpose
This JSON file defines 10 Arm cortex-a510 trace buffer and cross-trigger interface events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 33-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (10). It contains 10 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `TRB_WRAP`, `TRB_TRIG`, `TRCEXTOUT0`, `TRCEXTOUT1`, `TRCEXTOUT2`, `TRCEXTOUT3`, `CTI_TRIGOUT4`, `CTI_TRIGOUT5`, `CTI_TRIGOUT6`, `CTI_TRIGOUT7`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 10 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a510/trace.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/branch.json

## Purpose
This JSON file defines 5 Arm cortex-a53 branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 26-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `EventCode` (4), `EventName` (4), `BriefDescription` (4), `ArchStdEvent` (1). It contains 1 `ArchStdEvent` aliases, 4 named implementation-defined events, and 4 encoded events. Event or alias names include `BR_INDIRECT_SPEC`, `BR_COND`, `BR_INDIRECT_MISPRED`, `BR_INDIRECT_MISPRED_ADDR`, `BR_COND_MISPRED`. Implementation-defined codes run from `0xC9` to `0xCC` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 1 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/bus.json

## Purpose
This JSON file defines 2 Arm cortex-a53 CPU cycle, bus cycle, and core-to-uncore access events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 9-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (2). It contains 2 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 2 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/cache.json

## Purpose
This JSON file defines 5 Arm cortex-a53 cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 28-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `EventCode` (5), `EventName` (5), `BriefDescription` (5). It contains 0 `ArchStdEvent` aliases, 5 named implementation-defined events, and 5 encoded events. Event or alias names include `PREFETCH_LINEFILL`, `PREFETCH_LINEFILL_DROP`, `READ_ALLOC_ENTER`, `READ_ALLOC`, `EXT_SNOOP`. Implementation-defined codes run from `0xC2` to `0xC8` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/memory.json

## Purpose
This JSON file defines 2 Arm cortex-a53 load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 13-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `EventCode` (2), `EventName` (2), `BriefDescription` (2). It contains 0 `ArchStdEvent` aliases, 2 named implementation-defined events, and 2 encoded events. Event or alias names include `EXT_MEM_REQ`, `EXT_MEM_REQ_NC`. Implementation-defined codes run from `0xC0` to `0xC1` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/other.json

## Purpose
This JSON file defines 6 Arm cortex-a53 miscellaneous error and exception-style PMU events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 29-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `EventCode` (4), `EventName` (4), `BriefDescription` (4), `ArchStdEvent` (2). It contains 2 `ArchStdEvent` aliases, 4 named implementation-defined events, and 4 encoded events. Event or alias names include `EXC_IRQ`, `EXC_FIQ`, `PRE_DECODE_ERR`, `L1I_CACHE_ERR`, `L1D_CACHE_ERR`, `TLB_ERR`. Implementation-defined codes run from `0xC6` to `0xD2` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 2 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/pipeline.json

## Purpose
This JSON file defines 10 Arm cortex-a53 front-end, back-end, resource, TLB, and pipeline stall events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 53-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `EventCode` (10), `EventName` (10), `BriefDescription` (10). It contains 0 `ArchStdEvent` aliases, 10 named implementation-defined events, and 10 encoded events. Event or alias names include `STALL_SB_FULL`, `OTHER_IQ_DEP_STALL`, `IC_DEP_STALL`, `IUTLB_DEP_STALL`, `DECODE_DEP_STALL`, `OTHER_INTERLOCK_STALL`, `AGU_DEP_STALL`, `SIMD_DEP_STALL`, `LD_DEP_STALL`, `ST_DEP_STALL`. Implementation-defined codes run from `0xC7` to `0xE8` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a53/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/branch.json

## Purpose
This JSON file defines 12 Arm cortex-a55 branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 60-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (7), `EventCode` (7), `EventName` (7), `BriefDescription` (7), `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 7 named implementation-defined events, and 7 encoded events. Event or alias names include `BR_MIS_PRED`, `BR_PRED`, `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`, `BR_COND_PRED`, `BR_INDIRECT_MIS_PRED`, `BR_INDIRECT_ADDR_MIS_PRED`, `BR_COND_MIS_PRED`, `BR_INDIRECT_ADDR_PRED`, `BR_RETURN_ADDR_PRED`, `BR_RETURN_ADDR_MIS_PRED`. Implementation-defined codes run from `0xC9` to `0xCF` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/bus.json

## Purpose
This JSON file defines 5 Arm cortex-a55 CPU cycle, bus cycle, and core-to-uncore access events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 18-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/cache.json

## Purpose
This JSON file defines 48 Arm cortex-a55 cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 189-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (34), `PublicDescription` (14), `EventCode` (14), `EventName` (14), `BriefDescription` (14). It contains 34 `ArchStdEvent` aliases, 14 named implementation-defined events, and 14 encoded events. Event or alias names include `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_ALLOCATE`, `L1D_TLB`, and 36 more. Implementation-defined codes run from `0xC0` to `0xD6` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 34 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/exception.json

## Purpose
This JSON file defines 5 Arm cortex-a55 exception, interrupt, abort, trap, and return events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 21-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (4), `PublicDescription` (1), `EventCode` (1), `EventName` (1), `BriefDescription` (1). It contains 4 `ArchStdEvent` aliases, 1 named implementation-defined events, and 1 encoded events. Event or alias names include `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_IRQ`, `EXC_FIQ`, `PREDECODE_ERROR`. Implementation-defined codes run from `0xC6` to `0xC6` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/instruction.json

## Purpose
This JSON file defines 21 Arm cortex-a55 retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 66-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (21). It contains 21 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `SW_INCR`, `LD_RETIRED`, `ST_RETIRED`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `PC_WRITE_RETIRED`, `BR_IMMED_RETIRED`, `BR_RETURN_RETIRED`, `INST_SPEC`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, and 9 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 21 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/memory.json

## Purpose
This JSON file defines 5 Arm cortex-a55 load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 18-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `UNALIGNED_LDST_RETIRED`, `MEM_ACCESS`, `REMOTE_ACCESS_RD`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/pipeline.json

## Purpose
This JSON file defines 14 Arm cortex-a55 front-end, back-end, resource, TLB, and pipeline stall events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 81-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (12), `EventCode` (12), `EventName` (12), `BriefDescription` (12), `ArchStdEvent` (2). It contains 2 `ArchStdEvent` aliases, 12 named implementation-defined events, and 12 encoded events. Event or alias names include `STALL_FRONTEND`, `STALL_BACKEND`, `STALL_FRONTEND_CACHE`, `STALL_FRONTEND_TLB`, `STALL_FRONTEND_PDERR`, `STALL_BACKEND_ILOCK`, `STALL_BACKEND_ILOCK_AGU`, `STALL_BACKEND_ILOCK_FPU`, `STALL_BACKEND_LD`, `STALL_BACKEND_ST`, `STALL_BACKEND_LD_CACHE`, `STALL_BACKEND_LD_TLB`, and 2 more. Implementation-defined codes run from `0xE1` to `0xEC` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 2 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a55/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/branch.json

## Purpose
This JSON file defines 5 Arm cortex-a57-a72 branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 18-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `BR_MIS_PRED`, `BR_PRED`, `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/bus.json

## Purpose
This JSON file defines 9 Arm cortex-a57-a72 CPU cycle, bus cycle, and core-to-uncore access events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 30-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (9). It contains 9 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`, `BUS_ACCESS_SHARED`, `BUS_ACCESS_NOT_SHARED`, `BUS_ACCESS_NORMAL`, `BUS_ACCESS_PERIPH`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 9 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/cache.json

## Purpose
This JSON file defines 26 Arm cortex-a57-a72 cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 81-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (26). It contains 26 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L1D_CACHE_RD`, `L1D_CACHE_WR`, and 14 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 26 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/exception.json

## Purpose
This JSON file defines 15 Arm cortex-a57-a72 exception, interrupt, abort, trap, and return events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 48-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (15). It contains 15 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, `EXC_SMC`, `EXC_HVC`, `EXC_TRAP_PABORT`, `EXC_TRAP_DABORT`, and 3 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 15 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/instruction.json

## Purpose
This JSON file defines 22 Arm cortex-a57-a72 retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 69-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (22). It contains 22 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, `TTBR_WRITE_RETIRED`, `LDREX_SPEC`, `STREX_PASS_SPEC`, `STREX_FAIL_SPEC`, `LD_SPEC`, `ST_SPEC`, `LDST_SPEC`, and 10 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 22 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/memory.json

## Purpose
This JSON file defines 6 Arm cortex-a57-a72 load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 21-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (6). It contains 6 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `MEM_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 6 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a57-a72/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/branch.json

## Purpose
This JSON file defines 5 Arm cortex-a65-e1 branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 18-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `BR_MIS_PRED`, `BR_PRED`, `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/bus.json

## Purpose
This JSON file defines 5 Arm cortex-a65-e1 CPU cycle, bus cycle, and core-to-uncore access events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 18-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/cache.json

## Purpose
This JSON file defines 56 Arm cortex-a65-e1 cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 237-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (34), `PublicDescription` (22), `EventCode` (22), `EventName` (22), `BriefDescription` (22). It contains 34 `ArchStdEvent` aliases, 22 named implementation-defined events, and 22 encoded events. Event or alias names include `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_ALLOCATE`, `L1D_TLB`, and 44 more. Implementation-defined codes run from `0xC0` to `0xF7` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 34 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/dpu.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/dpu.json

## Purpose
This JSON file defines 5 Arm cortex-a65-e1 data-processing-unit branch and memory error events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 33-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (5), `EventCode` (5), `EventName` (5), `BriefDescription` (5). It contains 0 `ArchStdEvent` aliases, 5 named implementation-defined events, and 5 encoded events. Event or alias names include `DPU_BR_IND_MIS`, `DPU_BR_COND_MIS`, `DPU_MEM_ERR_IFU`, `DPU_MEM_ERR_DCU`, `DPU_MEM_ERR_TLB`. Implementation-defined codes run from `0xE9` to `0xED` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/dpu.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/exception.json

## Purpose
This JSON file defines 4 Arm cortex-a65-e1 exception, interrupt, abort, trap, and return events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 15-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (4). It contains 4 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_IRQ`, `EXC_FIQ`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/ifu.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/ifu.json

## Purpose
This JSON file defines 20 Arm cortex-a65-e1 instruction-fetch-unit wait, micro-TLB, micro-op cache, and linefill events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 123-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (20), `EventCode` (20), `EventName` (20), `BriefDescription` (20). It contains 0 `ArchStdEvent` aliases, 20 named implementation-defined events, and 20 encoded events. Event or alias names include `IFU_IC_MISS_WAIT`, `IFU_IUTLB_MISS_WAIT`, `IFU_MICRO_COND_MISPRED`, `IFU_MICRO_CADDR_MISPRED`, `IFU_MICRO_HIT`, `IFU_MICRO_NEG_HIT`, `IFU_MICRO_CORRECTION`, `IFU_MICRO_NO_INSTR1`, `IFU_MICRO_NO_PRED`, `IFU_FLUSHED_TLB_MISS`, `IFU_FLUSHED_EXCL_TLB_MISS`, `IFU_ALL_THRDS_RDY`, and 8 more. Implementation-defined codes run from `0xD0` to `0xE4` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/ifu.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/instruction.json

## Purpose
This JSON file defines 22 Arm cortex-a65-e1 retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 72-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (21), `PublicDescription` (1), `EventCode` (1), `EventName` (1), `BriefDescription` (1). It contains 21 `ArchStdEvent` aliases, 1 named implementation-defined events, and 1 encoded events. Event or alias names include `SW_INCR`, `LD_RETIRED`, `ST_RETIRED`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `PC_WRITE_RETIRED`, `BR_IMMED_RETIRED`, `BR_RETURN_RETIRED`, `INST_SPEC`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, and 10 more. Implementation-defined codes run from `0xE8` to `0xE8` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 21 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/memory.json

## Purpose
This JSON file defines 9 Arm cortex-a65-e1 load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 36-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (7), `PublicDescription` (2), `EventCode` (2), `EventName` (2), `BriefDescription` (2). It contains 7 `ArchStdEvent` aliases, 2 named implementation-defined events, and 2 encoded events. Event or alias names include `MEM_ACCESS`, `REMOTE_ACCESS_RD`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`, `BIU_EXT_MEM_REQ`, `BIU_EXT_MEM_REQ_NC`. Implementation-defined codes run from `0xC1` to `0xC2` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 7 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/pipeline.json

## Purpose
This JSON file defines 2 Arm cortex-a65-e1 front-end, back-end, resource, TLB, and pipeline stall events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 9-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (2). It contains 2 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `STALL_FRONTEND`, `STALL_BACKEND`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 2 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a65-e1/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/branch.json

## Purpose
This JSON file defines 5 Arm cortex-a710 branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 18-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `BR_MIS_PRED`, `BR_PRED`, `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/bus.json

## Purpose
This JSON file defines 6 Arm cortex-a710 CPU cycle, bus cycle, and core-to-uncore access events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 21-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (6). It contains 6 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`, `CNT_CYCLES`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 6 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/cache.json

## Purpose
This JSON file defines 51 Arm cortex-a710 cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 156-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (51). It contains 51 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_ALLOCATE`, `L1D_TLB`, and 39 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 51 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/exception.json

## Purpose
This JSON file defines 15 Arm cortex-a710 exception, interrupt, abort, trap, and return events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 48-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (15). It contains 15 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, `EXC_SMC`, `EXC_HVC`, `EXC_TRAP_PABORT`, `EXC_TRAP_DABORT`, and 3 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 15 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/instruction.json

## Purpose
This JSON file defines 44 Arm cortex-a710 retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 135-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (44). It contains 44 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, `BR_MIS_PRED_RETIRED`, `OP_RETIRED`, `OP_SPEC`, `LDREX_SPEC`, `STREX_PASS_SPEC`, and 32 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 44 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/memory.json

## Purpose
This JSON file defines 13 Arm cortex-a710 load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 42-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (13). It contains 13 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`, `LDST_ALIGN_LAT`, `LD_ALIGN_LAT`, `ST_ALIGN_LAT`, `MEM_ACCESS_CHECKED`, `MEM_ACCESS_CHECKED_RD`, and 1 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 13 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/pipeline.json

## Purpose
This JSON file defines 7 Arm cortex-a710 front-end, back-end, resource, TLB, and pipeline stall events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 24-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (7). It contains 7 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 7 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/trace.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/trace.json

## Purpose
This JSON file defines 9 Arm cortex-a710 trace buffer and cross-trigger interface events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 30-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (9). It contains 9 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `TRB_WRAP`, `TRCEXTOUT0`, `TRCEXTOUT1`, `TRCEXTOUT2`, `TRCEXTOUT3`, `CTI_TRIGOUT4`, `CTI_TRIGOUT5`, `CTI_TRIGOUT6`, `CTI_TRIGOUT7`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 9 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a710/trace.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/branch.json

## Purpose
This JSON file defines 3 Arm cortex-a73 branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 12-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (3). It contains 3 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `BR_MIS_PRED`, `BR_PRED`, `BR_INDIRECT_SPEC`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 3 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/bus.json

## Purpose
This JSON file defines 7 Arm cortex-a73 CPU cycle, bus cycle, and core-to-uncore access events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 24-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (7). It contains 7 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_SHARED`, `BUS_ACCESS_NOT_SHARED`, `BUS_ACCESS_NORMAL`, `BUS_ACCESS_PERIPH`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 7 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/cache.json

## Purpose
This JSON file defines 26 Arm cortex-a73 cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 108-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (17), `PublicDescription` (9), `EventCode` (9), `EventName` (9), `BriefDescription` (9). It contains 17 `ArchStdEvent` aliases, 9 named implementation-defined events, and 9 encoded events. Event or alias names include `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L1D_CACHE_RD`, `L1D_CACHE_WR`, and 14 more. Implementation-defined codes run from `0xC2` to `0xEC` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 17 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/etm.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/etm.json

## Purpose
This JSON file defines 2 Arm cortex-a73 Embedded Trace Macrocell external output events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 15-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (2), `EventCode` (2), `EventName` (2), `BriefDescription` (2). It contains 0 `ArchStdEvent` aliases, 2 named implementation-defined events, and 2 encoded events. Event or alias names include `ETM_EXT_OUT0`, `ETM_EXT_OUT1`. Implementation-defined codes run from `0xDE` to `0xDF` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/etm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/exception.json

## Purpose
This JSON file defines 3 Arm cortex-a73 exception, interrupt, abort, trap, and return events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 15-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (2), `PublicDescription` (1), `EventCode` (1), `EventName` (1), `BriefDescription` (1). It contains 2 `ArchStdEvent` aliases, 1 named implementation-defined events, and 1 encoded events. Event or alias names include `EXC_TAKEN`, `EXC_HVC`, `EXC_TRAP_HYP`. Implementation-defined codes run from `0xDC` to `0xDC` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 2 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/instruction.json

## Purpose
This JSON file defines 21 Arm cortex-a73 retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 66-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (21). It contains 21 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `PC_WRITE_RETIRED`, `BR_IMMED_RETIRED`, `BR_RETURN_RETIRED`, `INST_SPEC`, `TTBR_WRITE_RETIRED`, `LDREX_SPEC`, `STREX_FAIL_SPEC`, `LD_SPEC`, and 9 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 21 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/memory.json

## Purpose
This JSON file defines 4 Arm cortex-a73 load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 15-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (4). It contains 4 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `MEM_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LDST_SPEC`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 4 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/mmu.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/mmu.json

## Purpose
This JSON file defines 7 Arm cortex-a73 MMU page-table-walk and translation-cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 45-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (7), `EventCode` (7), `EventName` (7), `BriefDescription` (7). It contains 0 `ArchStdEvent` aliases, 7 named implementation-defined events, and 7 encoded events. Event or alias names include `MMU_PTW`, `MMU_PTW_ST1`, `MMU_PTW_ST2`, `MMU_PTW_LSU`, `MMU_PTW_ISIDE`, `MMU_PTW_PLD`, `MMU_PTW_CP15`. Implementation-defined codes run from `0xE0` to `0xE6` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/mmu.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/pipeline.json

## Purpose
This JSON file defines 6 Arm cortex-a73 front-end, back-end, resource, TLB, and pipeline stall events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 39-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (6), `EventCode` (6), `EventName` (6), `BriefDescription` (6). It contains 0 `ArchStdEvent` aliases, 6 named implementation-defined events, and 6 encoded events. Event or alias names include `LF_STALL`, `PTW_STALL`, `D_LSU_SLOT_FULL`, `LS_IQ_FULL`, `DP_IQ_FULL`, `DE_IQ_FULL`. Implementation-defined codes run from `0xC0` to `0xDA` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a73/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/branch.json

## Purpose
This JSON file defines 3 Arm cortex-a75 branch prediction, branch speculation, and misprediction events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 12-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (3). It contains 3 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `BR_MIS_PRED`, `BR_PRED`, `BR_INDIRECT_SPEC`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 3 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/bus.json

## Purpose
This JSON file defines 5 Arm cortex-a75 CPU cycle, bus cycle, and core-to-uncore access events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 18-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/cache.json

## Purpose
This JSON file defines 45 Arm cortex-a75 cache access, refill, miss, writeback, prefetch, and TLB-adjacent cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 165-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (36), `PublicDescription` (9), `EventCode` (9), `EventName` (9), `BriefDescription` (9). It contains 36 `ArchStdEvent` aliases, 9 named implementation-defined events, and 9 encoded events. Event or alias names include `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L1D_CACHE_ALLOCATE`, `L2D_CACHE_ALLOCATE`, and 33 more. Implementation-defined codes run from `0xC2` to `0xEC` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 36 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/etm.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/etm.json

## Purpose
This JSON file defines 2 Arm cortex-a75 Embedded Trace Macrocell external output events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 15-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (2), `EventCode` (2), `EventName` (2), `BriefDescription` (2). It contains 0 `ArchStdEvent` aliases, 2 named implementation-defined events, and 2 encoded events. Event or alias names include `ETM_EXT_OUT0`, `ETM_EXT_OUT1`. Implementation-defined codes run from `0xDE` to `0xDF` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/etm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/exception.json

## Purpose
This JSON file defines 4 Arm cortex-a75 exception, interrupt, abort, trap, and return events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 18-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (3), `PublicDescription` (1), `EventCode` (1), `EventName` (1), `BriefDescription` (1). It contains 3 `ArchStdEvent` aliases, 1 named implementation-defined events, and 1 encoded events. Event or alias names include `EXC_TAKEN`, `EXC_UNDEF`, `EXC_HVC`, `EXC_TRAP_HYP`. Implementation-defined codes run from `0xDC` to `0xDC` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 3 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/instruction.json

## Purpose
This JSON file defines 24 Arm cortex-a75 retired, speculative, SIMD, crypto, barrier, and instruction-mix events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 75-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (24). It contains 24 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `PC_WRITE_RETIRED`, `BR_IMMED_RETIRED`, `BR_RETURN_RETIRED`, `INST_SPEC`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, `LDREX_SPEC`, `STREX_PASS_SPEC`, and 12 more. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 24 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/memory.json

## Purpose
This JSON file defines 5 Arm cortex-a75 load/store, memory access, unaligned access, and memory-system events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 18-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `ArchStdEvent` (5). It contains 5 `ArchStdEvent` aliases, 0 named implementation-defined events, and 0 encoded events. Event or alias names include `MEM_ACCESS`, `REMOTE_ACCESS_RD`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LDST_SPEC`. This table relies entirely on `ArchStdEvent` aliases rather than local event codes.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include 5 entries lack explicit brief descriptions. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/mmu.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/mmu.json

## Purpose
This JSON file defines 7 Arm cortex-a75 MMU page-table-walk and translation-cache events for the perf PMU event database. It is static input to the perf event-table generator, not runtime code. The source was read as a complete 45-line JSON file.

## Important APIs, Types, and Functions
Schema fields are `PublicDescription` (7), `EventCode` (7), `EventName` (7), `BriefDescription` (7). It contains 0 `ArchStdEvent` aliases, 7 named implementation-defined events, and 7 encoded events. Event or alias names include `MMU_PTW`, `MMU_PTW_ST1`, `MMU_PTW_ST2`, `MMU_PTW_LSU`, `MMU_PTW_ISIDE`, `MMU_PTW_PLD`, `MMU_PTW_CP15`. Implementation-defined codes run from `0xE0` to `0xE6` in file order.

## Control Flow, State, and Persistence
`jevents.py` loads this file from the CPU model directory, resolves `ArchStdEvent` entries against common architecture-standard definitions, and serializes named `EventCode` entries into generated `pmu-events.c`. Runtime perf commands then discover the generated table through the PMU events APIs. There is no mutable in-file state or control flow. State is declarative: event names, encodings, descriptions, units, compat selectors, and metric formulas. The generated C tables are the durable build artifact, while runtime counter values live in perf sessions.

## Dependencies and Integration Points
Dependencies and integration points are the perf `pmu-events` JSON schema, `tools/perf/pmu-events/Build`, `jevents.py`, `metric.py` for metric expressions when present, architecture-standard event definitions for `ArchStdEvent` rows, and the kernel perf PMU drivers that expose the underlying counters. The file has no standalone persistence; its data persists by being compiled into the generated perf event tables.

## Risks and Test Signals
Risks include schema or event-code drift would be the main failure mode. Also watch for event-code collisions, aliases unsupported by this CPU, category placement that affects `perf list` discoverability, and stale descriptions. Test signals include JSON syntax validation, `jevents.py` generation, generated-table diffs, `perf list` visibility, and counter smoke tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/mmu.json -->
