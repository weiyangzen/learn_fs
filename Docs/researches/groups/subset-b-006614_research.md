# subset-b-006614 grouped research

This grouped report covers the POWER10 and POWER8 perf PMU event metadata files listed for work item `subset-b-006614`. Each section is delimited for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/metrics.json

## Purpose

This file defines 168 derived perf metrics for IBM POWER10 core PMU analysis. It is metadata, not executable code: each array entry names a metric and provides a `MetricExpr` that perf can parse into counter expressions. The metrics cover run-cycle rate, CPI and IPC, dispatch/issue/execution/completion stalls, instruction fetch misses, dL1 reload source attribution, memory locality, branch behavior, DERAT/DTLB translation behavior, and per-instruction operation rates.

## APIs, types, and schema

The effective API is the perf PMU JSON metric schema consumed by `tools/perf/pmu-events/jevents.py`. Entries use `MetricName`, `MetricExpr`, `MetricGroup`, `BriefDescription`, and `ScaleUnit`. There are no `EventCode` fields because this file does not define raw events; it defines formulas over event names such as `PM_RUN_CYC`, `PM_INST_CMPL`, `PM_EXEC_STALL_*`, `PM_DATA_FROM_*`, `PM_DERAT_MISS_*`, and `PM_INST_FROM_*`. Metric groups include `General`, `CPI`, `CPI;CPI_STALL_RATIO`, `Others`, `dL1_Reloads`, `Memory`, `Instruction_Stats`, `Instruction_Misses`, and `Translation`.

## Control flow and integration

At build time, perf's PMU event generation scans the `pmu-events/arch/powerpc` tree, parses metric expressions through the metric parser, and emits generated `pmu-events.c`. At runtime, perf list and metricgroup code expose these metrics by `MetricName` and group, and metric evaluation schedules the referenced raw events. The ordering is declarative: base metrics such as `CYCLES_PER_INSTRUCTION`, `IPC`, `RUN_CPI`, and `RUN_IPC` sit next to decompositions that divide stall counters by `PM_RUN_INST_CMPL` or miss counters by completed instructions.

## State and persistence

The file has no runtime state. Its persistent effect is compiled into generated perf event tables. Any change to metric names, groups, formulas, or scale units changes user-visible perf metric names and calculated values for POWER10 systems. The file also has one duplicate `MetricName`, `DISPATCH_STALL_FETCH_CPI`, appearing in the CPI group with the same expression pattern as part of two nearby stall lists; this is a persistence risk because generated lookup behavior may depend on duplicate-name handling.

## Dependencies

The formulas depend on corresponding POWER10 raw event definitions in sibling files such as `pipeline.json`, `pmc.json`, `translation.json`, and `others.json`, plus broader POWER PMU event availability. The metric parser must accept infix arithmetic, parentheses, percentages, and semicolon-separated metric groups. Consumers include `pmu-events/jevents.py`, `pmu-events/metric.py`, `util/metricgroup.h`, `util/pmu.c`, `builtin-list.c`, and the Python perf bindings that expose `MetricName` and `MetricExpr`.

## Risks

Many expressions divide by counters such as `PM_RUN_INST_CMPL`, `PM_LD_REF_L1`, `PM_L1_ICACHE_MISS`, `PM_LD_DEMAND_MISS_L1`, and `PM_DERAT_MISS` without the `1 + denominator` guard seen in some nest metrics. Short or filtered workloads can produce zero denominators. Spelling is part of the API, so typos such as `EXEC_STALL_UNKOWN_CPI` are user-visible even if historically intentional. Formula correctness also depends on every referenced event being present for POWER10 and correctly categorized in raw event JSON.

## Test signals

Useful checks are `jq` validity, uniqueness checks for `MetricName`, perf's PMU generation target, `pmu-events/metric_test.py`, and runtime `perf list --metrics` or `perf stat -M <MetricName>` on POWER10 hardware. Regression tests should verify expression parse success, referenced event resolution, group membership, and stable scale-unit behavior for percent metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/nest_metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/nest_metrics.json

## Purpose

This file defines 70 POWER10 nest and fabric metrics derived from `hv_24x7` counters. It focuses on PowerBus pump retries, local/group/remote/near node pump traffic, XLink and ALink utilization, PCI data transfer, memory-controller read/write bandwidth, aggregate memory bandwidth per chip, and PowerBus frequency.

## APIs, types, and schema

Entries use the perf metric schema with `MetricName`, `MetricExpr`, `ScaleUnit`, and `AggregationMode`; all entries have `AggregationMode: PerChip`. Some entries also include `MetricGroup`, but the dominant contract is chip-scoped nest aggregation. Expressions reference `hv_24x7@EVENT\,chip\=?@`, which binds events from the hypervisor 24x7 PMU with a wildcard or supplied chip selector. The file does not define raw events or descriptions.

## Control flow and integration

`jevents.py` parses this JSON during perf build and emits metric table entries. Runtime evaluation differs from core metrics because formulas read `hv_24x7` event syntax rather than ordinary core PMU events. Pump retry ratios divide retry counters by pump counters, total pump metrics normalize pump counts by `PM_PAU_CYC`, link utilization metrics combine odd/even data or total utilization lanes and divide by available cycles, and bandwidth metrics expose raw or summed MCS and PCI transfer counters.

## State and persistence

The file has no local mutable state. Persistent behavior is the set of named chip-level metrics available to perf users on POWER10 systems with the `hv_24x7` PMU. The `chip=?` selector is part of the persistent query contract: it allows perf to aggregate per chip, but it also means incorrect selector parsing would break all metrics in this file.

## Dependencies

The metrics depend on kernel and hypervisor support for `hv_24x7`, chip-scoped PMU events such as `PM_PB_*`, `PM_XLINK*_OUT_*`, `PM_ALINK*_OUT_*`, `PM_MCS_*`, `PM_PCI*_32B_INOUT`, and `PM_PAU_CYC`, plus perf metric parsing for escaped commas and `@...@` event syntax. Integration points are `pmu-events/jevents.py`, `pmu-events/metric.py`, and metricgroup/runtime event scheduling code.

## Risks

Most ratio denominators are raw event counts; some utilization and retry formulas add `1` to avoid division by zero, while several local/group pump ratios do not. Metrics without `BriefDescription` place more burden on metric names for user understanding. All formulas are `PerChip`, so accidental system-wide aggregation can mislead users. Syntax is fragile because escaped commas and `chip=?` selectors must survive JSON parsing, metric parsing, and runtime event opening.

## Test signals

Validation should include `jq`, metric parser tests for escaped `hv_24x7@...\,chip\=?@` syntax, perf PMU event generation, and runtime `perf stat -M` checks on POWER10 systems with accessible `hv_24x7` counters. Specific tests should cover zero or missing chip counters, per-chip aggregation, and formulas that combine odd/even link counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/nest_metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/others.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/others.json

## Purpose

This file defines 14 miscellaneous POWER10 raw PMU events that do not fit cleanly into the pipeline, PMC, translation, or metric formula files. The events cover adjunct cycles and completions, instruction dispatch, load demand L1 miss, all L1 instruction-cache reloads, `isync` completion, load/store 32-byte finish slots, unaligned load/store finishes, strided prefetch conflict, and cycles blocked by a full instruction buffer.

## APIs, types, and schema

The file uses the raw PMU event JSON schema: each entry has `EventCode`, `EventName`, and `BriefDescription`. There is no `PublicDescription`. The stable API is the event name to event code mapping, for example `PM_ADJUNCT_CYC`, `PM_ADJUNCT_INST_CMPL`, `PM_INST_DISP`, `PM_LD_DEMAND_MISS_L1`, `PM_L1_ICACHE_RELOADED_ALL`, and `PM_NO_FETCH_IBUF_FULL_CYC`.

## Control flow and integration

Perf build tooling ingests these entries through `jevents.py`, emits them into generated event tables, and later resolves them when users run commands such as `perf stat -e PM_INST_DISP` or when metrics in `metrics.json` reference the same names. Several events are direct dependencies of derived POWER10 metrics, including load miss and instruction reload formulas.

## State and persistence

There is no runtime state. The persistent contract is the event-code mapping for POWER10. Event names become part of the generated PMU table and are consumed directly by users and indirectly by metrics. Event codes are unique within this file.

## Dependencies

Dependencies are the POWER10 PMU encoding, perf's event table generator, and metric expressions that reference these counters. The file integrates with the same architecture mapfile path that selects the POWER10 event directory for POWER processors.

## Risks

Because descriptions are brief and there is no `PublicDescription`, ambiguous events such as slot-specific `PM_LD0_32B_FIN` and `PM_LD1_32B_FIN` rely on hardware documentation for full meaning. Any mismatch between `EventCode` and actual POWER10 PMU encoding would silently produce wrong measurements. The miscellaneous grouping can make ownership and coverage reviews harder than category-specific files.

## Test signals

Run JSON validation, unique event-code and event-name checks, perf PMU generation, and runtime event-open checks on POWER10. Metrics that reference `PM_INST_DISP`, `PM_LD_DEMAND_MISS_L1`, and `PM_L1_ICACHE_RELOADED_ALL` are useful integration smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/others.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/pipeline.json

## Purpose

This file defines 101 POWER10 raw PMU events for front-end, dispatch, issue, execution, load-store, branch, completion, synchronization, and L2 translation invalidation behavior. It is the main raw-event backing store for the CPI stall breakdowns in `metrics.json`.

## APIs, types, and schema

Each entry has `EventCode`, `EventName`, and `BriefDescription`. Event names include `PM_EXEC_STALL_*`, `PM_DISP_STALL_*`, `PM_CMPL_STALL_*`, `PM_LSU_*_FIN`, `PM_VSU*_ISSUE`, `PM_FLUSH*`, `PM_NTC_*`, `PM_BR_FIN`, `PM_FXU_ISSUE`, `PM_1PLUS_PPC_DISP`, and L2 TLB invalidation delay events. There are no functions or classes; the public contract is the raw PMU event namespace.

## Control flow and integration

`jevents.py` converts these event definitions into generated perf event tables. Runtime consumers either open these events directly or evaluate metrics that divide these counters by `PM_RUN_INST_CMPL` or other baseline counters. The control model is declarative: categories such as dispatch stalls, execution stalls, and completion stalls are represented as independent counters that metrics combine into CPI contributions.

## State and persistence

The file does not store mutable state. The event names and codes persist into the built perf binary. Because many `metrics.json` formulas refer to this file's names, renaming or deleting a pipeline event can break metric generation or produce unresolved runtime metrics.

## Dependencies

Dependencies include POWER10 PMU encodings, perf's PMU event generator, and related files that provide denominator counters such as `PM_RUN_INST_CMPL` and `PM_CYC`. Integration points include `metrics.json`, `pmc.json`, `pmu-events/metric.py`, and runtime PMU scheduling in `util/pmu.c`.

## Risks

This file has broad blast radius because it backs the central CPI model. Stall events with overlapping descriptions can be misinterpreted as exclusive when hardware may count them differently. Lack of `PublicDescription` limits user-facing detail. Event-code mistakes can corrupt multiple derived metrics. The source also contains specialized names such as `PM_EXEC_STALL_UNKNOWN`, `PM_DISP_STALL_HELD_HALT_CYC`, and L2 TLBIE/SLBIE delay events that need hardware-specific verification.

## Test signals

Test with JSON parsing, event-code uniqueness, generated `pmu-events.c` build, and `perf list` visibility for representative pipeline events. Metric parser tests should ensure all `PM_DISP_STALL_*`, `PM_EXEC_STALL_*`, and `PM_CMPL_STALL_*` references in `metrics.json` resolve. Hardware smoke tests should compare high-level CPI metrics against direct raw event counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/pmc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/pmc.json

## Purpose

This file defines 42 POWER10 raw events for baseline PMU accounting, privilege-mode cycles and completions, PMC overflow/rewind/saved behavior, threshold exceptions, run latch accounting, interrupts, and marked probe/time-out events. It supplies many denominator and context counters used by POWER10 metrics.

## APIs, types, and schema

Entries use `EventCode`, `EventName`, and `BriefDescription`. Important names include `PM_INST_CMPL`, `PM_CYC`, `PM_RUN_CYC`, `PM_RUN_INST_CMPL`, `PM_INST_FIN`, `PM_HYPERVISOR_CYC`, `PM_PRIVILEGED_CYC`, `PM_ULTRAVISOR_CYC`, `PM_RUN_CYC_SMT2_MODE`, `PM_RUN_CYC_SMT4_MODE`, `PM_PMC*_OVERFLOW`, `PM_PMC*_REWIND`, and `PM_THRESH_EXC_*`.

## Control flow and integration

Perf generation treats these as raw events. Runtime metrics use them as bases for CPI, IPC, run-cycle rate, completed instruction set size, privilege accounting, threshold behavior, and operation-per-instruction ratios. The file is central to metric evaluation because `PM_CYC`, `PM_INST_CMPL`, `PM_RUN_CYC`, and `PM_RUN_INST_CMPL` are common denominators.

## State and persistence

The file is static metadata, but its generated event names are persistent user-facing identifiers. Counters such as PMC overflow and rewind describe hardware PMU state transitions, but the JSON itself does not persist runtime counter state.

## Dependencies

Dependencies include POWER10 PMU hardware semantics and perf's event parser. `metrics.json` depends heavily on the baseline counters in this file. Integration points include perf list output, metric evaluation, Python perf bindings, and tests that compare generated PMU event tables against JSON.

## Risks

Baseline counter mistakes have high impact because they skew many derived ratios. Privilege and ultravisor/hypervisor counters can be sensitive to execution context and availability. PMC overflow/rewind/saved events are low-level and can be confused with perf's own sampling overflow behavior. The lack of `PublicDescription` reduces detail for users diagnosing mode-specific measurements.

## Test signals

Use `jq`, uniqueness checks, perf PMU generation, and runtime direct event opens. Integration tests should evaluate `IPC`, `RUN_CPI`, `RUN_IPC`, `RUN_CYCLES_RATE`, and stall metrics that rely on `PM_RUN_INST_CMPL`. Mode-specific counters should be checked only on environments where privilege and ultravisor semantics are meaningful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/pmc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/translation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/translation.json

## Purpose

This small file defines three POWER10 raw PMU events for store forwarding and store completion behavior: `PM_ST_FWD`, `PM_ST_CMPL`, and `PM_ST_MISS_L1`. Despite the directory name, the visible events are store/cache related rather than broad address-translation events.

## APIs, types, and schema

The schema is the raw event contract: `EventCode`, `EventName`, and `BriefDescription`. `PM_ST_MISS_L1` is referenced by `metrics.json` for L1 store miss rate; `PM_ST_FWD` and `PM_ST_CMPL` are direct user-visible raw events.

## Control flow and integration

Perf build generation converts these three entries into the POWER10 event table. At runtime, users can select them directly, and metrics can reference them by name. The key integration is the `L1_ST_MISS_RATE` formula in `metrics.json`, which uses `PM_ST_MISS_L1`.

## State and persistence

There is no mutable state. Persistence is the stable event-name to event-code mapping compiled into perf. Because the file is tiny, omissions are easy to detect but misplacement under `translation.json` may surprise maintainers.

## Dependencies

Dependencies are POWER10 PMU encodings and perf's `jevents.py` raw event ingestion. `metrics.json` is a direct dependent for store miss rate.

## Risks

The filename suggests translation coverage, but the content is store forwarding, completion, and L1 store miss. That mismatch can cause maintainers to add or search for events in the wrong category. Missing `PublicDescription` limits context. If `PM_ST_MISS_L1` is wrong or unavailable, the derived store miss metric breaks.

## Test signals

Validate JSON, ensure unique event codes, run PMU event generation, and check that `L1_ST_MISS_RATE` resolves. Direct `perf stat -e PM_ST_MISS_L1` on POWER10 is the most direct runtime smoke test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/translation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/cache.json

## Purpose

This file defines 29 POWER8 raw PMU events for data-cache reload source attribution, demand load L1 behavior, data-side tablewalk and SLB misses, and store misses. It distinguishes local L2/L3 hits, L2/L3 misses, dispatch conflicts, MEPF state, local L4, on-chip cache, off-chip cache, remote and distant L2/L3 modified or shared sources, and data-side page-table-entry sourcing.

## APIs, types, and schema

POWER8 event entries use `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`. The public contract includes events such as `PM_DATA_FROM_L2`, `PM_DATA_FROM_L3`, `PM_DATA_FROM_L3MISS`, `PM_DATA_FROM_RL2L3_MOD`, `PM_DATA_FROM_DL2L3_SHR`, `PM_DATA_TABLEWALK_CYC`, `PM_DSLB_MISS`, `PM_L1_DCACHE_RELOADED_ALL`, `PM_LD_MISS_L1`, `PM_LD_REF_L1`, and `PM_ST_MISS_L1`.

## Control flow and integration

Perf's PMU generator turns these definitions into generated event tables. Runtime consumers use them directly for cache locality studies or indirectly through any POWER8 metric formulas in the broader PMU tree. The event taxonomy lets users decompose demand-load cache misses by cache level, conflict type, coherency state, and topology distance.

## State and persistence

The file is static. Event names, codes, and descriptions persist into perf output. The `PublicDescription` text provides longer user-facing semantics and is therefore part of the documentation contract as well as the generated event metadata.

## Dependencies

Dependencies include POWER8 PMU encodings, hardware definitions for MEPF, local/remote/distant topology, L4 cache behavior, SLB and tablewalk counters, and perf's JSON generation path. Integration points include generated `pmu-events.c`, `perf list`, direct `perf stat -e` use, and any cache-miss metric formulas.

## Risks

The file contains fine-grained topology and coherency categories that are easy to aggregate incorrectly. Some descriptions have historical wording issues, so tests cannot rely on prose equality alone. Event semantics may depend on POWER8 system topology and L4 availability. Mis-coded reload source events can lead to misleading NUMA/cache locality conclusions.

## Test signals

Use JSON validation, event-name and event-code uniqueness checks, generated PMU build tests, and `perf list` inspection. Hardware validation should compare demand-load miss decomposition against broad counters such as `PM_LD_MISS_L1` and `PM_L1_DCACHE_RELOADED_ALL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/floating-point.json

## Purpose

This file defines two POWER8 raw PMU events, `PM_FXU_BUSY` and `PM_FXU_IDLE`. Despite the filename, the visible events describe fixed-point unit activity rather than floating-point/vector execution.

## APIs, types, and schema

Entries use `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`. The schema matches other POWER8 raw event files. The two public event names expose whether both FXU units are busy or idle.

## Control flow and integration

During perf build, `jevents.py` converts these entries into generated event tables. Runtime users select the raw events directly with perf. These counters can also be used by derived metrics or external scripts to reason about integer execution-unit pressure.

## State and persistence

There is no mutable state. The event-code mapping and descriptions persist into generated perf metadata. The mismatch between filename and fixed-point event names is also persistent source organization behavior that maintainers need to know.

## Dependencies

Dependencies are POWER8 PMU encodings, FXU hardware semantics, and perf's raw event generation. Integration points are generated PMU tables, `perf list`, and direct `perf stat` event selection.

## Risks

The file name can mislead maintainers looking for floating-point or VSU counters. With only two events, accidental deletion or misclassification would remove the entire category. Event descriptions are short and do not explain SMT, sampling, or attribution details.

## Test signals

Validate JSON, event-code uniqueness, perf PMU generation, and direct event-open behavior for `PM_FXU_BUSY` and `PM_FXU_IDLE` on POWER8. If a broader POWER8 metric references FXU activity, include it in integration checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/frontend.json

## Purpose

This file defines 78 POWER8 raw events for branch/front-end behavior, instruction dispatch and completion, instruction-cache reload source attribution, instruction-side page table entry sourcing, IERAT/ITLB/ISLB misses, pump prediction for instruction fetch, concurrent thread run instructions, and transactional-memory instruction accounting.

## APIs, types, and schema

Entries use `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`. Representative events include `PM_BR_CMPL`, `PM_BR_MPRED_CMPL`, `PM_IC_DEMAND_CYC`, `PM_IERAT_RELOAD_*`, `PM_INST_CMPL`, `PM_INST_DISP`, `PM_INST_FROM_*`, `PM_IPTEG_FROM_*`, `PM_ISLB_MISS`, `PM_ITLB_MISS`, `PM_L1_ICACHE_MISS`, `PM_L1_ICACHE_RELOADED_ALL`, `PM_THRD_CONC_RUN_INST`, `PM_TM_TRANS_RUN_INST`, and `PM_TM_TX_PASS_RUN_INST`.

## Control flow and integration

Perf build generation compiles these front-end events into PMU tables. Runtime users can select individual events or use them in metrics that analyze branch prediction, instruction sourcing, and translation. The instruction sourcing taxonomy mirrors the POWER8 data-cache source taxonomy but applies to instruction fetches and instruction-side PTE loads.

## State and persistence

The file has no mutable state. Event names, event codes, and descriptions persist into generated perf metadata. Because this file covers many front-end concepts, it is a major source for `perf list` output on POWER8.

## Dependencies

Dependencies include POWER8 front-end, branch, instruction cache, ERAT/TLB/SLB, pump prediction, and transactional-memory PMU semantics. Integration is through `jevents.py`, generated `pmu-events.c`, perf list/stat, and any scripts or metrics referencing these event names.

## Risks

The event taxonomy is broad and includes topology-specific sourcing, transaction state, and translation behavior; users can misinterpret overlapping categories. Some descriptions mention older POWER behavior or wording quirks, so hardware documentation remains necessary. Event-code errors can break branch-miss and instruction-cache investigations. Transactional-memory counters may be unavailable or uninteresting on configurations that do not exercise TM.

## Test signals

Use JSON validation, uniqueness checks, generated PMU builds, and runtime `perf list` checks. Hardware smoke tests should cover branch counters, `PM_L1_ICACHE_MISS`, `PM_INST_FROM_L2/L3/LMEM/RMEM/DMEM`, and translation misses such as `PM_ITLB_MISS` or `PM_ISLB_MISS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/marked.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/marked.json

## Purpose

This file defines 132 POWER8 raw PMU events for marked or sampled instruction behavior. It covers marked branch completion, marked load sourcing and latency cycles, marked data ERAT/DTLB misses by page size, marked data-side PTE sourcing, fabric response outcomes for stores, marked instruction lifecycle events, marked cache reload intervals, load miss exposure, store completion/drain timing, marked run cycles, and synchronization marker reasons.

## APIs, types, and schema

The schema is `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`. Event names are mostly prefixed with `PM_MRK_`, plus marker synchronization events such as `PM_SYNC_MRK_BR_LINK`, `PM_SYNC_MRK_BR_MPRED`, `PM_SYNC_MRK_FX_DIVIDE`, `PM_SYNC_MRK_L2HIT`, `PM_SYNC_MRK_L2MISS`, `PM_SYNC_MRK_L3MISS`, and `PM_SYNC_MRK_PROBE_NOP`. Pairs such as `PM_MRK_DATA_FROM_L2` and `PM_MRK_DATA_FROM_L2_CYC` expose both occurrence and duration.

## Control flow and integration

Perf generation adds these marked events to the POWER8 PMU table. At runtime, they are used for sampled/marked instruction analysis where the PMU follows selected instructions and attributes latency, sourcing, stalls, or completion behavior. The control model is declarative but semantically tied to PMU marking configuration and sampling behavior.

## State and persistence

The JSON is static. The persistent output is a large set of generated event identifiers and descriptions. Runtime marking state is owned by the PMU and perf event configuration, not by this file, but these entries define the names that expose that state.

## Dependencies

Dependencies include POWER8 marked-event PMU semantics, fabric response definitions, cache and memory topology, ERAT/DTLB page-size classifications, store pipeline timing, and perf's raw event generator. Integration points are generated event tables, direct perf event selection, and any higher-level marked-event analysis tools.

## Risks

This is a dense, high-risk metadata file because many names differ only by source, coherency state, or `_CYC` suffix. Copy/paste mistakes can swap event codes or descriptions while still passing JSON syntax checks. Users may confuse marked events with aggregate events from `cache.json` or `memory.json`. Marked events also require correct sampling setup; direct counts without understanding PMU marking can be misleading.

## Test signals

Validation should include JSON parsing, event-name and event-code uniqueness, generated PMU build, and targeted runtime tests for representative marked data source, marked branch, marked DTLB/DERAT, and marked store events. Review tests should ensure `_CYC` duration events are paired correctly with non-cycle events where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/marked.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/memory.json

## Purpose

This file defines 35 POWER8 raw PMU events for memory and nest-facing behavior. It covers chip/group/system pump prediction and misprediction for demand loads and broader request classes, data reloads from local/remote/distant memory and L4, data-side PTE sourcing from distant or remote memory, L3 castout, memory reads, prefetches and RWITM, memory locality thresholds, and the nest reference clock.

## APIs, types, and schema

Entries use `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`. Representative names include `PM_DATA_FROM_LMEM`, `PM_DATA_FROM_RMEM`, `PM_DATA_FROM_DMEM`, `PM_DATA_FROM_RL4`, `PM_DATA_FROM_MEMORY`, `PM_DATA_*_PUMP_*`, `PM_*PUMP_*`, `PM_DPTEG_FROM_*`, `PM_MEM_READ`, `PM_MEM_PREF`, `PM_MEM_RWITM`, `PM_MEM_CO`, and `PM_NEST_REF_CLK`.

## Control flow and integration

Perf generation compiles these memory events into POWER8 PMU tables. Runtime users use them to study memory locality, pump prediction, coherence traffic, and memory-controller-facing activity. Some events are demand-load specific while others cover all data types excluding data prefetch, so correct selection depends on the analysis question.

## State and persistence

The file is static metadata. Event names, codes, and descriptions persist into generated perf metadata. The events measure runtime hardware state such as pump prediction and memory traffic, but that state is not persisted in the JSON.

## Dependencies

Dependencies include POWER8 memory hierarchy and nest PMU semantics, L4/cache topology, local/remote/distant node definitions, pump-scope prediction, and perf's event generation pipeline. Integration points are generated `pmu-events.c`, `perf list`, `perf stat`, and any external tooling that groups POWER8 memory events.

## Risks

Pump-scope names are similar and easy to confuse, especially demand-load-specific `PM_DATA_*` counters versus broader `PM_*` counters. `PM_NEST_REF_CLK` requires a documented multiplier to obtain PB cycles, so raw values can be misread. Topology-dependent local/remote/distant semantics vary by machine configuration. Description typos should not be treated as semantic changes but can affect user-facing docs.

## Test signals

Use JSON validation, event-code uniqueness, PMU generation, and runtime event-open checks. Hardware tests should compare broad memory reads with source-specific reload counters where feasible and should include representative pump prediction and misprediction events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/memory.json -->
