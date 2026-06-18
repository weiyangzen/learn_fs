# Research: subset-b-006613 PMU event JSON files

This grouped report covers perf PMU event and metric JSON files under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch`. These files are declarative data, not runtime code, but they are build inputs to `tools/perf/pmu-events/jevents.py`, which resolves `ArchStdEvent`, parses `MetricExpr`, converts event/config fields into generated C tables, and exposes aliases through perf's PMU lookup and Python bindings.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/misc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/misc.json

## Purpose
This 130-entry NVIDIA T410 Arm64 PMU topic table captures miscellaneous architectural and implementation-defined events that do not fit cleanly into cache, TLB, retired, or stall files. It mixes standard Arm events such as `SW_INCR`, trace/CTI events, and many T410-specific prefetch, translation, SMT transition, interrupt latency, and GPT lookup events. The first event tracks software increments of `PMSWINC_EL0`; the last event, `GPT_PG_HIT`, counts GPT lookup hits in the TLB.

## Important Data Fields
Entries use `ArchStdEvent` when the event is defined in the architecture-standard catalog and `EventCode` plus `EventName` for T410-specific encodings. Every entry carries `PublicDescription`; most implementation events depend on numeric encodings such as `0x0252`. There are no functions or classes here; the effective API is the perf PMU event schema consumed by `jevents.py`.

## Control Flow And Integration
At build time, `jevents.py` walks the T410 directory selected by the Arm64 `mapfile.csv` CPUID `0x000000004e0f0100`, resolves `ArchStdEvent` names against architecture-root JSON definitions, and emits generated `pmu-events.c` rows. At runtime, perf selects the matching T410 table and exposes aliases like `L1_PF_HIT` or `INTR_LATENCY`.

## State, Dependencies, Risks, And Tests
The file is static source state with no persistence other than generated build artifacts. It depends on valid JSON, unique event names, correct Arm standard-event references, and NVIDIA event-code accuracy. Main risks are mistyped `EventCode`, duplicated or ambiguous names, stale standard-event references, and descriptions whose semantics diverge from hardware manuals. Test signals include `jq empty`, `jevents.py` generation, `perf test pmu-events`, and `perf list`/`perf stat -e <event>` on T410 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/misc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/retired.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/retired.json

## Purpose
This 23-entry T410 Arm64 table defines architecturally executed or retired instruction and branch events. It includes `INST_RETIRED`, register-write retirement events, branch-retired families, and prediction/misprediction variants for immediate, indirect, return, taken, skipped, and non-return indirect branches.

## Important Data Fields
All entries use `ArchStdEvent` with `PublicDescription`, so this file is a T410 selection layer over Arm architecture-standard event definitions rather than a local encoding table. The event names become perf aliases after resolution by the PMU event generator.

## Control Flow And Integration
`jevents.py` dereferences each `ArchStdEvent` using the architecture root catalog, carries the local public descriptions into generated C data, and attaches the generated table to the T410 CPU mapping. These events feed perf commands that need architected counts, branch-retirement analysis, and topdown-style retired-work metrics.

## State, Dependencies, Risks, And Tests
There is no mutable runtime state. The file depends heavily on the architecture-standard event catalog being complete and semantically compatible with T410. Risks are missing standard definitions, mismatch between Arm architectural retirement semantics and NVIDIA implementation behavior, or alias collisions with other topic files. Useful test signals are JSON validity, `jevents.py` reference resolution, generated-table inspection, and branch-heavy `perf stat` runs on T410.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/retired.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/spe.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/spe.json

## Purpose
This 10-entry T410 Arm64 topic file exposes Statistical Profiling Extension sample-feed events: sample population, feed, filtration, collision, and feeds by branch/load/store/op/event/latency class. It lets perf users count SPE sampling pipeline behavior in addition to recording SPE samples.

## Important Data Fields
Entries consist of `ArchStdEvent` plus `PublicDescription`. The names include `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`, and class-specific `SAMPLE_FEED_*` events. No local `EventCode` fields are present.

## Control Flow And Integration
During generation, these standard-event references resolve into PMU event encodings and descriptions. Runtime integration is through perf's selected T410 event table; users can list and count these aliases with the regular PMU event path, while detailed SPE tracing remains handled by perf's Arm SPE machinery outside this JSON.

## State, Dependencies, Risks, And Tests
The file has no persistence or control logic. It depends on Arm SPE architectural event definitions and T410 PMU support. Risks include exposing events on systems where SPE or the relevant filters are unavailable, or confusion between counting sample-feed events and collecting sampled records. Tests should include JSON validation, generated alias presence, and hardware checks comparing `perf list` with supported PMU capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/spe.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/spec_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/spec_operation.json

## Purpose
This 54-entry T410 Arm64 table describes speculatively executed operations. It spans architectural operation classes such as loads, stores, atomics, data-processing, SIMD/FP/SVE, barriers, branches, return-stack, MOPS, TLBI, and T410-specific vector-predicated load mismatch tracking.

## Important Data Fields
Most rows use `ArchStdEvent`; implementation-specific rows use `EventCode`, `EventName`, and `PublicDescription`, for example `VPRED_LD_SPEC_MISMATCH` at `0x022f`. The schema directly maps into perf event aliases and generated event encodings.

## Control Flow And Integration
`jevents.py` converts each row into a `pmu_event` entry, resolving architecture-standard events and preserving descriptions. These events integrate with T410 metrics and user workflows that compare speculative activity with retired work, branch behavior, and SVE effectiveness.

## State, Dependencies, Risks, And Tests
The file is immutable build input. Dependencies include Arm architectural standard-event definitions and correct NVIDIA codes for implementation-specific events. Risks include denominator/semantic mismatches in metrics that combine speculative and retired counts, event-name collisions across T410 topic files, and invalid event-code formats. Test signals are JSON parsing, successful `jevents.py` generation, metric-expression validation where these names are referenced, and representative `perf stat` collection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/spec_operation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/stall.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/stall.json

## Purpose
This 33-entry T410 Arm64 topic file defines frontend, backend, slot, memory-bound, CPU-bound, dispatch, issue-queue, and synchronization stall events. These entries are central to T410 topdown-style metrics and bottleneck diagnosis.

## Important Data Fields
The file combines `ArchStdEvent` rows such as `STALL_FRONTEND` and `STALL_BACKEND` with T410-specific `EventCode` rows such as `STALL_SLOT_FRONTEND_WITHOUT_MISPRED`. Every row has a `PublicDescription` explaining the stall source or accounting unit.

## Control Flow And Integration
Build-time flow is standard PMU JSON ingestion through `jevents.py`; runtime flow is perf alias lookup for the T410 CPU table. The events are integration points for `metrics.json` in the same CPU directory and generic topdown views because stall-slot names often appear in `MetricExpr` formulas.

## State, Dependencies, Risks, And Tests
There is no mutable state. The main dependencies are CPU slot accounting, T410 PMU event-code correctness, and compatibility with metric formulas. Risks are high because stall events are easy to misinterpret: slot events, cycle events, frontend/backend categories, and misprediction exclusions must not be mixed casually. Tests should include JSON validity, `metric_test.py`/parse-metric coverage for formulas that reference these names, and sanity checks that topdown percentages remain bounded under known workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/stall.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/tlb.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/tlb.json

## Purpose
This 38-entry T410 Arm64 file enumerates instruction/data TLB access, refill, walk, hardware update, step, page-size, read/write, and prefetch-related translation events. It covers L1I, L1D, L2D, DTLB, ITLB, and software-prefetch cases.

## Important Data Fields
Rows use `ArchStdEvent` for common Arm events and `EventCode`/`EventName` for T410-specific extensions such as `L1I_TLB_REFILL_PRFM` at `0x0224`. `PublicDescription` distinguishes demand, prefetch, refill, walk, and fault-exclusion semantics.

## Control Flow And Integration
`jevents.py` turns the table into generated T410 PMU aliases. Runtime consumers include direct perf commands, memory-system investigation workflows, and metrics that compare translation stalls with cache and memory activity.

## State, Dependencies, Risks, And Tests
The JSON is static state. It depends on standard Arm definitions for common TLB events and correct local codes for the implementation-defined set. Risks include duplicate-looking event families with subtly different units, fault-exclusion semantics, and metrics that combine walk-per-cycle with raw event counts. Test signals include JSON validation, generated alias presence, and hardware checks under TLB-pressure workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/tlb.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/recommended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/recommended.json

## Purpose
This 76-entry Arm64 architecture-root file defines recommended architectural event names and encodings for cache, TLB, bus, memory, unaligned/speculative operations, barriers, exceptions, release-consistency operations, and L3 cache activity. It provides common definitions that CPU-specific files can reference or align with.

## Important Data Fields
Rows use `PublicDescription`, `EventCode`, `EventName`, and `BriefDescription`. Unlike CPU-specific `ArchStdEvent` wrapper files, this file is the concrete catalog of recommended Arm event encodings, for example `L1D_CACHE_RD` at `0x40` and `L3D_CACHE_INVAL` at `0xa8`.

## Control Flow And Integration
`jevents.py` loads architecture-root JSON files as standard event sources. CPU model files use `ArchStdEvent` to dereference entries based on `EventName`, reducing duplication across Arm64 CPU directories. Generated perf tables inherit these names, encodings, and descriptions into model-specific maps.

## State, Dependencies, Risks, And Tests
The file is shared static build input. Its blast radius is broad: an incorrect encoding or renamed event can affect every Arm64 model that dereferences it. Risks include breaking `ArchStdEvent` resolution, altering alias semantics across vendors, and accidentally changing generic recommended behavior to match one implementation. Test signals are full Arm64 `jevents.py` generation, `perf test pmu-events`, JSON schema checks, and spot checks of CPU-specific generated aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/recommended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/sbsa.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/sbsa.json

## Purpose
This 4-entry Arm64 metric file defines SBSA topdown level-1 metrics: `frontend_bound`, `bad_speculation`, `retiring`, and `backend_bound`. These formulas express percentages of total slots using common Arm counters such as stall slots, branch mispredictions, operation retirement, CPU cycles, and `#slots`.

## Important Data Fields
Each row uses `MetricExpr`, `BriefDescription`, `DefaultMetricgroupName`, `MetricGroup`, `MetricName`, and `ScaleUnit`. The formulas use lower-case event aliases and perf metric constants, for example `100 * (stall_slot_backend / (#slots * cpu_cycles))`.

## Control Flow And Integration
`jevents.py` parses `MetricExpr` through the perf metric parser and emits generated metric tables. Runtime consumers include `perf stat -M` and Python metric export paths that expose `MetricName`, `MetricExpr`, `ScaleUnit`, and descriptions.

## State, Dependencies, Risks, And Tests
The file is static; runtime persistence is limited to generated perf objects. Dependencies are the availability and naming of the referenced Arm64 events, plus parser support for `#slots`. Risks include division by zero, formula drift when event aliases change, and CPU models that map SBSA metrics without the full counter set. Test signals include metric parser tests, `perf list --metrics`, and `perf stat -M TopdownL1` on SBSA-capable hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/sbsa.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/thead/yitian710/sys/ali_drw.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/thead/yitian710/sys/ali_drw.json

## Purpose
This 53-entry Yitian 710 system PMU table describes Alibaba DDR read/write controller events for the `ali_drw` unit. It covers HIF read/write/rmw traffic, DFI data cycles, critical read/write transactions, DRAM commands, precharge/refresh/power-state transitions, hazards, visible-window limits, CHI traffic, and DDR cycles.

## Important Data Fields
Rows use `BriefDescription`, `ConfigCode`, `EventName`, `Unit`, and `Compat`. `Unit` is consistently `ali_drw`, while `Compat` is `ali_drw_pmu`; `jevents.py` maps this unit into an uncore PMU name. Event encodings range from `0x0` for `hif_rd_or_wr` to `0x80` for `ddr_cycles`.

## Control Flow And Integration
The Arm64 mapfile selects the broader Yitian 710 directory for the CPU, and this system PMU file contributes uncore event aliases. At runtime, perf PMU matching uses the `Unit`/`Compat` data with uncore name matching, including wildcard or suffix-insensitive paths in `perf_pmu__name_wildcard_match` and `perf_pmu__name_no_suffix_match`.

## State, Dependencies, Risks, And Tests
The file is declarative state. It depends on the kernel exposing an `ali_drw_pmu`-compatible PMU and on the hardware interpreting `ConfigCode` values as documented. Risks include PMU-name mismatch, unit scaling errors for 64B transactions, and metric breakage if `hif_rd`, `hif_wr`, `hif_rmw`, or `duration_time` aliases are absent. Test signals include JSON validation, generated alias inspection, `perf list ali_drw`, and bandwidth sanity checks under memory-copy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/thead/yitian710/sys/ali_drw.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/thead/yitian710/sys/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/thead/yitian710/sys/metrics.json

## Purpose
This 2-entry Yitian 710 system PMU metrics file derives DDR read and write bandwidth metrics for the `ali_drw` PMU. `ddr_read_bandwidth.all` uses `hif_rd * 64 / 1e6 / duration_time`; `ddr_write_bandwidth.all` uses `(hif_wr + hif_rmw) * 64 / 1e6 / duration_time`.

## Important Data Fields
Each metric has `MetricName`, `BriefDescription`, `MetricGroup`, `MetricExpr`, `ScaleUnit`, `Unit`, and `Compat`. The formulas rely on `ali_drw.json` event aliases and the common tool event `duration_time`.

## Control Flow And Integration
`jevents.py` parses these expressions, keeps `Compat` and `Unit`, and emits metric rows associated with the ali_drw PMU. Runtime perf metric listing and `perf stat -M ali_drw` style use depend on PMU matching and event availability.

## State, Dependencies, Risks, And Tests
The file is static metric metadata. Dependencies are the `hif_*` events, correct 64-byte transaction semantics, `duration_time`, and the kernel PMU compatibility string. Risks include unit mistakes because `duration_time` is nanoseconds while the formula divides by `1e6`, zero-duration edge cases, and inaccurate bandwidth if events count transactions differently than assumed. Test signals are metric parser checks and comparison against external memory-bandwidth tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/thead/yitian710/sys/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/legacy-hardware.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/legacy-hardware.json

## Purpose
This 14-entry common table maps traditional perf hardware event aliases such as `cpu-cycles`, `instructions`, `cache-misses`, `branches`, `branch-misses`, frontend/backend stalled cycles, and `ref-cycles` to legacy hardware config codes. It preserves the familiar cross-architecture perf event names.

## Important Data Fields
Rows use `EventName`, `BriefDescription`, and `LegacyConfigCode`. `jevents.py` converts `LegacyConfigCode` into generated `legacy-hardware-config=<value>` event strings rather than ordinary raw PMU event encodings.

## Control Flow And Integration
This common file is included in the generated common PMU event tables and backs perf aliases used by user commands and metric formulas. It integrates with generic metrics in `arch/common/common/metrics.json`, which reference names like `instructions`, `cycles`, and cache miss events.

## State, Dependencies, Risks, And Tests
The file is stable declarative state with very broad consumers. Risks are severe for compatibility: renaming aliases, changing config codes, or altering descriptions can break existing commands, scripts, and metrics across architectures. Test signals include generated event validation, `perf list` for legacy aliases, `perf stat -e cycles,instructions`, and parser tests for formulas that depend on these aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/legacy-hardware.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/metrics.json

## Purpose
This 17-entry common metrics file defines generic perf-derived metrics: CPU utilization, context-switch/migration/page-fault rates, IPC, stalled cycles per instruction, frontend/backend idle percentages, cycle and branch frequency, branch miss rate, cache miss rates, TLB miss rates, and L1 prefetch miss rate.

## Important Data Fields
Rows use `MetricExpr`, `MetricGroup`, `MetricName`, `ScaleUnit`, and often `MetricConstraint`, `DefaultShowEvents`, and `MetricThreshold`. Some expressions use escaped event names and explicit PMU syntax, such as `software@cpu-clock,...@` for CPU utilization.

## Control Flow And Integration
`jevents.py` parses the formulas through `metric.ParsePerfJson`, simplifies them, and emits generated metric rows. Runtime consumers include `perf stat -M`, `perf list --metrics`, and Python binding export of metric metadata.

## State, Dependencies, Risks, And Tests
The file is shared static state. Dependencies include common software/tool events, legacy hardware aliases, cache/TLB aliases, expression parser syntax, and threshold handling. Risks include parser regressions from escaping, divide-by-zero for rates, unavailable events on some architectures, and thresholds that imply misleading health signals. Test signals are `metric_test.py`, `tests/parse-metric.c`, `perf list --metrics`, and representative `perf stat -M Default` runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/software.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/software.json

## Purpose
This 15-entry common file defines perf software event aliases: `cpu-clock`, `task-clock`, page faults, context switches, CPU migrations, minor/major faults, alignment/emulation faults, `dummy`, `bpf-output`, and `cgroup-switches`.

## Important Data Fields
Rows use `Unit` set to `software`, `EventName`, `BriefDescription`, `ConfigCode`, and sometimes `ScaleUnit`. `jevents.py` maps the `software` unit to the software PMU and produces config-based event aliases.

## Control Flow And Integration
These events become generated common aliases used directly by users and indirectly by metrics such as `CPUs_utilized`, context switches per second, migrations per second, and page faults per second. They integrate with kernel perf software counters rather than model-specific hardware PMUs.

## State, Dependencies, Risks, And Tests
The file is static but widely depended on. Risks include config-code mismatch with kernel `PERF_COUNT_SW_*`, duplicate aliases such as `faults`/`page-faults` and `cs`/`context-switches` being altered inconsistently, and unit scaling errors for clock events. Test signals are JSON validation, generated aliases, `perf stat -e task-clock,context-switches,page-faults`, and generic metric runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/software.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/tool.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/tool.json

## Purpose
This 14-entry common file defines perf tool-provided pseudo-events and constants, including `duration_time`, `user_time`, `system_time`, persistent-memory presence, CPU/core/package topology values, `slots`, SMT state, TSC frequency, `core_wide`, and `target_cpu`.

## Important Data Fields
Rows use `Unit` set to `tool`, `EventName`, `BriefDescription`, and `ConfigCode`. Unlike raw hardware PMU events, these names are supplied by perf/tooling context and are often used as metric formula inputs.

## Control Flow And Integration
`jevents.py` maps the `tool` unit into generated metadata. Runtime metric evaluation resolves these pseudo-events/constants when evaluating expressions in common, Arm64, and vendor metric files, for example `duration_time` in bandwidth metrics and `#slots`/`slots` in topdown calculations.

## State, Dependencies, Risks, And Tests
The file is static schema input, but values are populated at runtime by perf. Risks include breaking metric formulas by renaming tool values, config-code drift, topology values being unavailable in some collection modes, and confusion between event-like counters and constants. Test signals include metric parser tests, `perf list tool`, and metrics that exercise `duration_time`, topology, and target-mode predicates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/tool.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/nds32/n13/atcpmu.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/nds32/n13/atcpmu.json

## Purpose
This 48-entry NDS32 N13 ATCPMU file defines core event aliases for branch behavior, instruction classes, interrupts/exceptions, loads/stores, TLB access/miss, stalls, BIU cycles/requests, cache/DLM/ILM access, DMA, external events, and compact instruction forms such as `push25_inst` and `pop25_inst`.

## Important Data Fields
Rows use `PublicDescription`, `EventCode`, `EventName`, and `BriefDescription`. Encodings are hex strings such as `0x102` for `cond_br` and `0x21e` for `pop25_inst`. There are no standard-event references; this is a concrete N13 model table.

## Control Flow And Integration
The NDS32 `mapfile.csv` maps CPUID `0x0` version `v3` to the `n13` directory. `jevents.py` generates the event table from this file, and perf exposes the aliases for the matching N13 PMU.

## State, Dependencies, Risks, And Tests
The file is static input. Dependencies are NDS32 support in perf, the mapfile entry, kernel PMU exposure, and hardware-correct event codes. Risks include architecture bitrot, event-code transcription errors, and ambiguous brief descriptions for events whose precise semantics matter to performance diagnosis. Test signals include JSON validity, NDS32 `jevents.py` generation, generated C table inspection, and hardware or emulator `perf list` validation when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/nds32/n13/atcpmu.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/compat/generic-events.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/compat/generic-events.json

## Purpose
This 23-entry PowerPC compatibility table supplies generic event aliases for fallback PowerPC mappings. It includes cycles, completed instructions, FLOPs, TLB misses, frontend availability, loads/stores, dispatched instructions, run cycles, branches, L1 cache misses, L3/memory source events, and branch mispredictions.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. The PowerPC mapfile maps `0x00ffffff` to `compat`, so these encodings provide a generic core table when no more specific model table applies.

## Control Flow And Integration
`jevents.py` emits this table as a PowerPC core event table. PowerPC runtime CPU identification, including architecture-specific header support, chooses either exact model tables or this compatibility directory. The aliases also support generic metrics that expect names like `PM_RUN_INST_CMPL` and `PM_CYC`.

## State, Dependencies, Risks, And Tests
The file is static but important for fallback behavior. Risks include overpromising event availability across PowerPC CPUs, using event codes that are not valid on older or unusual models, and breaking generic perf scripts that rely on these names. Test signals include PowerPC generation, mapfile matching tests, `perf list` on fallback systems, and representative `perf stat` runs for the generic names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/compat/generic-events.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/cache.json

## Purpose
This 4-entry POWER10 cache topic file defines a small set of cache and instruction-completion events: L1 reload for prefetch line miss, L1 I-cache miss, L1 I-cache reloaded by prefetch, and concurrent run instruction completion.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. Encodings include `0x1002C` for `PM_LD_PREFETCH_CACHE_LINE_MISS` and `0x300F4` for `PM_RUN_INST_CMPL_CONC`.

## Control Flow And Integration
PowerPC `mapfile.csv` maps POWER10 PVR patterns `0x0080...` and `0x0082...` to the `power10` directory. `jevents.py` emits these rows into the POWER10 event table, and perf exposes them with other POWER10 topic files.

## State, Dependencies, Risks, And Tests
The file is static model metadata. Risks are limited in size but include event-code transcription errors and topic overlap with larger POWER10 files such as datasource, frontend, and pmc. Test signals include JSON validity, generated table inclusion, `perf list PM_L1_ICACHE_MISS`, and workload checks that exercise instruction-cache and prefetch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/datasource.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/datasource.json

## Purpose
This 367-entry POWER10 datasource file is the largest table in this work item. It enumerates where instruction and data cache reloads came from: L1/L2/L3, local and remote memory, on-chip/off-chip cache, local/remote/distant regions, regent/non-regent sources, conflict/no-conflict/MEPF cases, and marked-instruction variants. Prefix analysis shows 129 `PM_DATA_FROM...`, 126 `PM_MRK_DATA...`, 53 `PM_INST_FROM...`, and 52 `PM_MRK_INST...` events.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. Encodings range from compact values such as `0x1505E` for `PM_LD_HIT_L1` to wide POWER10 selector encodings such as `0x095840000020C142` for `PM_MRK_DATA_FROM_ANY_MEMORY_ALL`.

## Control Flow And Integration
The PowerPC mapfile selects this file through the POWER10 directory. `jevents.py` parses the long hex event-code strings and emits generated C rows. Runtime perf users can count source-attribution events directly or use them as building blocks for memory hierarchy and marked-instruction analysis.

## State, Dependencies, Risks, And Tests
The file is static but high-risk due to size and encoding complexity. Dependencies are POWER10 PMU selector semantics, generated-code handling for wide hex values, and consistency between marked and unmarked event families. Risks include copy/paste mistakes, inconsistent `_ALL` variants, near-duplicate descriptions masking different encodings, and generated output size. Test signals include JSON validity, full PowerPC `jevents.py` generation, generated table spot checks for first/last and marked/unmarked pairs, and hardware sanity checks under local/remote memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/datasource.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/floating_point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/floating_point.json

## Purpose
This 13-entry POWER10 floating-point topic file defines completed floating-point operation counters. It distinguishes total FLOPs, 1/2/4/8-FLOP instructions, FMA and non-FMA, scalar and vector, single precision, math and non-math, and double/quad precision events.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. `PM_FLOP_CMPL` at `0x100F4` is the broad count; `PM_DPP_FLOP_CMPL` at `0x4D05C` covers double-precision or quad-precision instruction completion.

## Control Flow And Integration
These rows are ingested with other POWER10 PMU JSON files and emitted into the generated model table. Runtime integration is direct perf alias use for FLOP accounting and potential metric formulas that derive compute intensity.

## State, Dependencies, Risks, And Tests
The file is static. Dependencies are POWER10 FP/VSU PMU semantics and correct interpretation of multi-FLOP instruction accounting. Risks include users summing overlapping events, event-code transcription errors, and descriptions that do not fully explain vector-lane scaling. Test signals include JSON validity, `perf list PM_FLOP_CMPL`, and numeric sanity checks on FP-heavy microbenchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/floating_point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/frontend.json

## Purpose
This 24-entry POWER10 frontend file covers TLB hits/misses by page size, branch completion and prediction, dispatch/issue cancellation, instruction availability, L1 load miss, instruction-from-L3-miss, and vector load/store completion events relevant to frontend and dispatch analysis.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. The first event, `PM_DTLB_HIT_2M`, notes radix translation and MMCR1 behavior; the last event, `PM_PRED_BR_NTKN_COND_DIR`, counts correctly predicted not-taken conditional branches.

## Control Flow And Integration
`jevents.py` emits these rows for POWER10 CPUs selected by mapfile PVR patterns. Runtime consumers use them directly for branch/frontend diagnosis and indirectly when metrics reference branch or instruction-source events.

## State, Dependencies, Risks, And Tests
Static metadata depends on POWER10 MMCR semantics and page-size-specific PMU definitions. Risks include page-size naming drift, overlapping frontend and memory/TLB topics, and descriptions whose conditional MMCR behavior is easy to miss. Test signals are generated alias checks and perf runs under branch-heavy, TLB-heavy, and instruction-cache pressure workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/locks.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/locks.json

## Purpose
This 4-entry POWER10 locks file focuses on conditional store (`STCX`) behavior used in lock acquisition. It provides failed, total finished, pass finished, and nest-successfully completed STCX event aliases.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. The file distinguishes `PM_STCX_FAIL_FIN`, `PM_STCX_FIN`, `PM_STCX_PASS_FIN`, and `PM_STCX_SUCCESS_CMPL`, where the last specifically counts pass status returned from the nest.

## Control Flow And Integration
The POWER10 generated PMU table exposes these names for direct lock-contention analysis. They may be paired with load-reserve events from other files and with application-level synchronization profiling.

## State, Dependencies, Risks, And Tests
The file is static. Risks include confusing pass/finish/success semantics, assuming the four counters are mutually exclusive without checking PMU documentation, and event-code errors in a tiny table where every row matters. Test signals include JSON validity, generated alias checks, and lock-contention microbenchmarks comparing STCX failure and success counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/locks.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/marked.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/marked.json

## Purpose
This 54-entry POWER10 marked-instruction file defines events for PMU-marked instruction issue, decode, dispatch, completion, flush, transfer-source PMC events, marked branch/cache/TLB/load/store behavior, marked STCX/LARX/TLBIE, and marked data-source misses.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. Event names are consistently prefixed with `PM_MRK_`, making the table a focused bridge between ordinary counting and sampled/marked instruction analysis. The first row is `PM_MRK_INST_ISSUED`; the last is `PM_MRK_DATA_FROM_L2MISS`.

## Control Flow And Integration
`jevents.py` emits the table into POWER10 generated events. Runtime integration is through perf's marked-event support and workflows that correlate marked instruction samples with memory hierarchy, branch, and synchronization behavior.

## State, Dependencies, Risks, And Tests
The file is static. Dependencies include POWER10 marked-instruction PMU semantics and consistency with `datasource.json`, where many marked source-attribution variants also exist. Risks include duplication or semantic drift between marked tables, event-code transcription errors, and misleading analysis if marked sampling configuration is not active. Test signals include generated alias checks, sampling/counting comparisons, and POWER10 marked-instruction workload tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/marked.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/memory.json

## Purpose
This 28-entry POWER10 memory file covers reload source transfer PMCs, DERAT/DTLB misses by page size, load completion, load L3-miss pending cycles, TLBIE snoop cycles, PTESYNC, LARX, and LSU store finish behavior. It complements datasource and frontend files with MMU and memory-ordering detail.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. The first event, `PM_XFER_FROM_SRC_PMC1`, references MMCR3-selected source fields and MMCR1 demand/prefetch behavior; the final event, `PM_SNOOP_TLBIE_WAIT_MMU_CYC`, counts LSU wait cycles for MMU invalidation.

## Control Flow And Integration
`jevents.py` emits the entries for POWER10 model tables. Runtime perf users combine these aliases with datasource, marked, and frontend events to diagnose translation misses, reload sources, and TLB invalidation stalls.

## State, Dependencies, Risks, And Tests
The file is static. Dependencies are POWER10 MMCR field semantics, page-size naming, and kernel PMU access to complex encodings. Risks include MMCR-dependent descriptions being overlooked, overlap with `frontend.json` TLB events, and wide event-code formatting errors. Test signals include JSON validation, generated C table checks, and targeted memory/TLB invalidation benchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/memory.json -->
