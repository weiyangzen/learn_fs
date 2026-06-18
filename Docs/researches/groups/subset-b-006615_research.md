# subset-b-006615 research

Grouped research for POWER8 perf PMU event metadata under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8`. The files are data inputs to the kernel perf `jevents` generator, not runtime Ceph logic.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/metrics.json

## Purpose
`metrics.json` defines 385 derived POWER8 performance metrics for Linux `perf`. Each row gives a user-facing metric name, arithmetic `MetricExpr`, optional `MetricGroup`, and short description. These metrics sit above the raw POWER8 PMU events from the same `power8` directory and let `perf stat -M ...` report higher-level ratios such as CPI components, cache locality, miss latency, branch prediction quality, translation behavior, LSU rejects, SMT mode share, and memory-source distribution.

The file is declarative JSON. It has no functions or mutable state of its own, but its contents become part of generated perf PMU metadata when `tools/perf/pmu-events/jevents.py` scans `arch/powerpc/power8`.

## Important schema and data surface
- Schema: array of objects with `MetricName`, `MetricExpr`, `BriefDescription`, and sometimes `MetricGroup`.
- Count: 385 metric rows.
- Grouped rows cover `branch_prediction`, `bus_stats`, `cpi_breakdown`, `dl1_reloads_percent_per_inst`, `dl1_reloads_percent_per_ref`, `estimated_dcache_miss_cpi`, `general`, `instruction_misses_percent_per_inst`, `instruction_mix`, `instruction_stats_percent_per_ref`, `l2_stats`, `latency`, `lsu_rejects`, `memory`, `pteg_reloads_percent_per_inst`, `pteg_reloads_percent_per_ref`, and `translation`.
- 64 rows are intentionally ungrouped. They include hit ratios, local/remote/distant Centaur memory ratios, L2/L3 machine usage estimates, store-forward ratios, store latency, sync stall CPI, and L3 prefetch waste.
- Three CPI rows lack `BriefDescription`: `mem_ecc_delay_stall_cpi`, `ntcg_all_fin_cpi`, and `ntcg_flush_cpi`.
- Expressions reference 269 unique `PM_*` raw events. A full-directory check across all POWER8 JSON files found all referenced events present in the same CPU directory, even though many dependencies live in sibling files such as `cache.json`, `memory.json`, `marked.json`, `frontend.json`, and `translation.json`.

## Control flow and integration
Build-time flow:
1. `jevents.py` traverses `tools/perf/pmu-events/arch/powerpc`.
2. `arch/powerpc/mapfile.csv` maps POWER8 PVR patterns, including `0x004[bcd][[:xdigit:]]{4}` and `0x0066[[:xdigit:]]{4}`, to the `power8` directory as `core` PMU metadata.
3. `metrics.json` is parsed with the other topic JSON files and encoded into generated perf PMU tables.
4. The generated tables are linked into `perf`; at runtime perf resolves the host CPU to the POWER8 table and exposes symbolic metrics.

Runtime flow is expression evaluation by perf. Users request metric names or groups, perf schedules the needed raw events subject to PMU constraints, reads counts, and evaluates the `MetricExpr` arithmetic.

## State and persistence behavior
The file is persistent source metadata. It does not write state, allocate resources, or hold runtime counters. The persistent effect is indirect: changing a metric name, expression, or group changes generated perf metadata and the user-facing metrics available in built perf binaries.

## Dependencies
- Depends on `jevents.py` and perf PMU-events schema support for metric objects.
- Depends on raw POWER8 event names in the same CPU directory. Local source checks show all referenced `PM_*` names resolve somewhere under `power8/*.json`.
- Depends on POWER8 event semantics such as marked load latency counters, L1/L2/L3 data-source counters, branch predictor counters, GCT occupancy, completion stall counters, and translation reload counters.

## Risks and edge cases
- Division by zero is common in low-sample or filtered workloads because expressions divide by events such as `PM_RUN_INST_CMPL`, `PM_L1_DCACHE_RELOAD_VALID`, `PM_DTLB_MISS`, or marked-event counts. Consumers need perf's metric handling to render unavailable values rather than treating them as source errors.
- Some metrics are difference formulas, for example "other" CPI buckets. Counter skid, multiplexing, or incompatible sampling windows can make those results negative or misleading.
- Several descriptions are missing, terse, or contain typos, and a few formulas encode domain assumptions that deserve scrutiny, such as `l3_no_conflict_latency` dividing `PM_MRK_DATA_FROM_L3_NO_CONFLICT_CYC` by `PM_MRK_DATA_FROM_L2`.
- Metrics rely on sibling raw-event files. Editing only this file can silently break metrics if event names are renamed elsewhere.
- The file has no explicit unit field. Units are implied by names and expressions (`percent`, `cpi`, `latency`, `ratio`), so naming consistency is part of the contract.

## Test signals
- JSON validity: parse as an array and require all rows to contain `MetricName` and `MetricExpr`; separately flag rows missing `BriefDescription`.
- Dependency check: extract `PM_*` tokens from every `MetricExpr` and verify each token appears as an `EventName` in `power8/*.json`.
- Build check: rebuild perf PMU events so `jevents.py` accepts every metric expression.
- Runtime smoke check on POWER8 or compatible fixture: `perf list` should show the metric aliases/groups, and representative `perf stat -M cpi,ipc,run_cpi` style commands should resolve.
- Regression tests should cover representative formulas from each group, especially CPI breakdown, memory locality, marked latency, branch prediction, and translation reload metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/other.json

## Purpose
`other.json` is the broad catch-all POWER8 raw PMU event table for perf. It defines 574 event aliases that do not fit cleanly into the smaller topic files. The events cover LPAR cycle modes, pump prediction, branch prediction internals, dispatch and flush causes, data and instruction reload sources, marked events, LSU queues, VSU/FPU/DFU execution, L2/L3 machines, transactional memory, interrupts, prefetch behavior, and assorted microarchitectural signals.

This file lets users and metrics refer to names like `PM_BR_MPRED_CCACHE`, `PM_DATA_ALL_FROM_L3`, `PM_GCT_NOSLOT_CYC`, or `PM_VSU1_VECTOR_SP_ISSUED` rather than raw event encodings.

## Important schema and data surface
- Schema: array of objects with `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`.
- Count: 574 raw event rows.
- Dominant event-name families include marked events (`PM_MRK_*`), instruction-source events (`PM_INST_*`), data-source events (`PM_DATA_*`), LSU events, VSU0/VSU1 events, branch events, L3 events, GCT events, dispatch/flush events, transactional-memory events, and pump prediction events.
- Event codes are hex strings, including simple encodings such as `0x5084` and wider encodings such as `0x61c050`.
- Many `PublicDescription` fields are empty, while some contain longer hardware notes about demand-only versus prefetch-included counting controlled by MMCR bits.

## Control flow and integration
Build-time flow:
1. `jevents.py` treats `other.json` as one PMU topic file because it has a `.json` extension inside the POWER8 model directory.
2. The generator lowercases event names for perf aliases and converts event codes into generated table entries such as `event=0x...`.
3. POWER8 PVR patterns in `arch/powerpc/mapfile.csv` select the whole `power8` directory, so these aliases are available together with the other topic files.
4. Higher-level metrics in `metrics.json` consume many of these event names, especially branch, GCT, data-source, marked-latency, and machine-usage signals.

At runtime, perf exposes these aliases through `perf list` and accepts them in event selectors such as `perf stat -e pm_br_bc_8_conv`. The kernel PMU driver owns actual counter scheduling and sampling.

## State and persistence behavior
`other.json` is static source metadata. It persists symbolic event definitions in the repository and contributes to generated perf tables at build time. It has no runtime state, but changing an `EventCode` changes what hardware signal an alias measures, and changing an `EventName` can break metrics and user scripts.

## Dependencies
- Depends on perf PMU-events JSON schema and `jevents.py`.
- Depends on POWER8 PMU hardware encodings and the powerpc PMU driver understanding the encoded event values.
- Integrates with `metrics.json`; several derived metrics use event families defined here, including branch-prediction and GCT signals.
- Integrates with sibling topic files by sharing one CPU directory selected by `arch/powerpc/mapfile.csv`.

## Risks and edge cases
- The file is a large catch-all table, so duplicate names, mistyped codes, or stale descriptions are easy to miss without automated checks.
- Some descriptions are truncated, typo-heavy, or conflict with `BriefDescription`; downstream help text quality depends on preserving or improving these strings.
- Empty `PublicDescription` fields are accepted but reduce discoverability in `perf list --details`.
- Several events describe mode-dependent semantics, such as prefetch inclusion controlled by MMCR bits. Users can misinterpret counts unless descriptions remain precise.
- Event aliases can be referenced by metrics in other files. Renames require full-directory dependency checks.

## Test signals
- JSON parse and schema validation for all 574 rows.
- Uniqueness checks for `EventName` within the full `power8` directory.
- Event-code format checks for hex strings.
- Build `tools/perf` or at least run the PMU-events generator path to ensure `jevents.py` accepts the file.
- Cross-file metric dependency check should include this file when resolving `MetricExpr` event names.
- Runtime smoke checks on POWER8 should verify a representative set from major families: branch prediction, data source, marked latency, GCT, LSU, VSU, transactional memory, and pump prediction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/pipeline.json

## Purpose
`pipeline.json` defines 58 POWER8 raw PMU events focused on pipeline progress, stalls, dispatch, completion, run cycles, flushes, transactional run cycles, synchronization, frequency slewing, and load/store completion. It supplies core aliases used directly by users and heavily by CPI and throughput metrics.

Representative events include `PM_CYC`, `PM_RUN_CYC`, `PM_RUN_INST_CMPL`, `PM_CMPLU_STALL`, `PM_CMPLU_STALL_LSU`, `PM_CMPLU_STALL_DCACHE_MISS`, `PM_1PLUS_PPC_CMPL`, `PM_1PLUS_PPC_DISP`, `PM_FLUSH`, `PM_DISP_HELD`, `PM_LD_CMPL`, and SMT mode run-cycle counters.

## Important schema and data surface
- Schema: array of objects with `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`.
- Count: 58 raw event rows.
- Main families: 19 completion-stall events, 6 LSU events, 5 run-cycle events, 3 store events, 2 transactional-memory events, 2 load-linked/store-conditional related events, dispatch-held events, flush events, power-management frequency events, hypervisor cycles, interrupts, and tablewalk cycles.
- Event codes are POWER8 PMU hex encodings such as `0x100f2`, `0x4000a`, `0x600f4`, and `0x500fa`.

## Control flow and integration
Build-time flow mirrors other PMU event files: `jevents.py` scans the file, emits generated PMU event records, and links them into perf for POWER8 CPU mappings from `arch/powerpc/mapfile.csv`.

Runtime integration is central for derived metrics. `metrics.json` uses these pipeline events as denominators and accounting buckets for IPC, CPI, run-cycle percentages, completion stalls, GCT and dispatch analyses, SMT mode percentages, sync stalls, LSU stalls, dcache-miss stall attribution, and transactional memory cycle accounting.

## State and persistence behavior
The file has no runtime mutation. It persists canonical symbolic names and event encodings for pipeline counters. Because many metrics divide by `PM_RUN_INST_CMPL`, `PM_CYC`, or `PM_RUN_CYC`, changing these event definitions has broad generated-metric impact.

## Dependencies
- Depends on perf's PMU event generator and the POWER8 PMU driver.
- Feeds `metrics.json` for high-level formulas such as `cpi`, `ipc`, `run_cpi`, `stall_cpi`, `thread_block_stall_cpi`, `lsu_stall_*_cpi`, and SMT cycle percentages.
- Complements `other.json`, which contains additional GCT, dispatch, branch, and stall subcauses used to build richer pipeline breakdowns.

## Risks and edge cases
- Pipeline counters are common denominators. Bad event codes or renamed aliases here can invalidate many unrelated-looking metrics.
- Some `PublicDescription` values intentionally clarify or correct short descriptions; losing them would reduce `perf list --details` quality.
- Several stall categories overlap or are used in subtractive "other" metrics. In multiplexed runs or short sampling windows, derived values can look inconsistent even when raw event definitions are correct.
- Events such as frequency up/down and SMT mode cycles are sensitive to platform state and may be absent or low-count depending on firmware and workload.

## Test signals
- JSON/schema validation for 58 rows.
- Full-directory uniqueness validation for all `EventName` values.
- Cross-file metric dependency validation, emphasizing that `PM_CYC`, `PM_RUN_CYC`, `PM_RUN_INST_CMPL`, `PM_CMPLU_STALL*`, `PM_1PLUS_PPC_*`, and `PM_FLUSH` resolve.
- Generator/build validation through `jevents.py` or a perf build.
- Runtime smoke tests: `perf stat -e pm_cyc,pm_run_cyc,pm_run_inst_cmpl,pm_cmplu_stall sleep 1`; metric smoke tests for `cpi`, `ipc`, `run_cpi`, and representative `cpi_breakdown` metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/pmc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/pmc.json

## Purpose
`pmc.json` defines 23 POWER8 raw PMU events related to performance monitor counter control and threshold behavior. It covers PMC overflow aliases, PMC rewind/save events, run PURR/SPURR accounting, a suspended counter marker, and threshold met/not-met or threshold-exceeded encodings.

These are lower-level control/status events rather than workload-domain counters. They are useful for diagnosing counter overflow, threshold configuration, sampling control, and run-timebase accounting.

## Important schema and data surface
- Schema: array of objects with `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`.
- Count: 23 raw event rows.
- Counter events: `PM_PMC1_OVERFLOW` through `PM_PMC6_OVERFLOW`, plus PMC2/PMC4 rewind and saved events.
- Run accounting events: `PM_RUN_PURR` and `PM_RUN_SPURR`.
- Counter-off marker: `PM_SUSPENDED` with code `0x0`.
- Threshold events: `PM_THRESH_EXC_32`, `PM_THRESH_EXC_64`, `PM_THRESH_EXC_128`, `PM_THRESH_EXC_256`, `PM_THRESH_EXC_512`, `PM_THRESH_EXC_1024`, `PM_THRESH_EXC_2048`, `PM_THRESH_EXC_4096`, `PM_THRESH_MET`, and `PM_THRESH_NOT_MET`.

## Control flow and integration
At build time, `jevents.py` ingests `pmc.json` with the rest of the POWER8 directory and emits perf aliases for these hardware events. At runtime, perf users can select the aliases directly. The file is not a major dependency for `metrics.json`; its role is more diagnostic and control-oriented than high-level metric computation.

## State and persistence behavior
This is static metadata only. The actual overflow, rewind, saved, suspended, and threshold states are hardware/runtime PMU behavior. The JSON persists names, codes, and descriptions that perf exposes to users.

## Dependencies
- Depends on POWER8 PMU support for PMC overflow, rewind, saved-value, PURR/SPURR, and threshold encodings.
- Depends on perf PMU-events generation and the powerpc mapfile selecting the `power8` directory for matching PVRs.
- Integrates with perf event selection and listing; it has little direct coupling to derived metrics compared with `pipeline.json` and `other.json`.

## Risks and edge cases
- `PM_SUSPENDED` uses event code `0x0`; validation should allow this even though many event-code checks assume nonzero hex.
- Threshold descriptions are inconsistent in detail, and `PM_THRESH_EXC_64` has a `BriefDescription` that appears unrelated (`IFU non-branch finished`) while the public description states threshold exceeded by 64. That should be treated as a documentation risk.
- Overflow and rewind events may be platform- or configuration-sensitive; availability in `perf list` does not guarantee useful counts in arbitrary sessions.
- Counter-control aliases are easy to misuse as workload metrics; documentation should keep them clearly separated from architectural performance ratios.

## Test signals
- JSON/schema validation for all 23 rows, allowing `EventCode` `0x0`.
- Full-directory uniqueness validation for `EventName`.
- Generator/build validation through the perf PMU-events path.
- Runtime smoke tests can list/select representative events: `pm_pmc1_overflow`, `pm_run_purr`, `pm_run_spurr`, `pm_thresh_met`, and `pm_suspended`.
- Manual review of threshold descriptions is warranted, especially `PM_THRESH_EXC_64`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/pmc.json -->
