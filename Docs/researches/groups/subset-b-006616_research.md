# Research: subset-b-006616

This grouped report covers the POWER8 and POWER9 Linux perf PMU event JSON files assigned to `subset-b-006616`. Each section is source-tree aligned and wrapped for reconciliation into its final per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/translation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/translation.json

## Purpose

This JSON file defines POWER8 translation-related core PMU events for Linux perf. It contains 29 event objects, all with unique `EventName` values, `EventCode` values, and descriptions. The events focus on data-side translation behavior: data ERAT misses by page size, DTLB misses by page size, general TLB misses, and PTEG reload sources for data-side page table entries. It is selected for POWER8-compatible processors through `arch/powerpc/mapfile.csv`, where POWER8 PVR patterns map to the `power8` model directory.

## APIs, types, and schema

The file is declarative data consumed by `tools/perf/pmu-events/jevents.py`. Each object maps into a `JsonEvent`: `EventName` becomes a lower-case perf event name, `EventCode` becomes the generated `event=...` encoding, `BriefDescription` becomes the short description, and `PublicDescription`, present in this file, becomes the long description unless it duplicates the short one. There are no functions or exported symbols in the JSON itself; its public API is the stable PMU-event schema expected by perf.

## Control flow and integration

During a perf build, `pmu-events/Build` includes JSON and CSV inputs under `pmu-events/arch`, then runs `jevents.py` to generate `pmu-events.c`. `jevents.py` loads the array with `json.load(..., object_hook=JsonEvent)`, normalizes descriptions, converts the event code with base auto-detection, and appends the entries to the model event table. At runtime, perf commands such as `perf list` and event selection resolve these generated entries through the PMU event tables for the matching PowerPC model.

## State, persistence, and dependencies

There is no runtime mutable state in this file. Its contents persist as source-controlled JSON and are compiled into generated C tables. It depends on valid JSON syntax, the perf PMU event schema, the POWER8 model mapping, and event names that match IBM POWER PMU documentation and kernel PMU encodings.

## Risks and test signals

The primary risks are incorrect event codes, ambiguous translation-source descriptions, or schema drift that prevents `JsonEvent` conversion. Because formulas do not reference this file directly, failures are most likely to appear as missing or misencoded `perf list` events rather than metric parse failures. Useful test signals are `jq empty` for syntax, a perf build that regenerates `pmu-events.c`, generated-table duplicate checks from `jevents.py`, and manual `perf list` verification on a POWER8 or compatible system.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/translation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/cache.json

## Purpose

This file contributes 21 POWER9 core PMU events to the `cache` topic. The contents are broader than simple cache-hit counters: they include completion stalls attributed to load misses and load miss queue pressure, instruction-cache reload sources, marked-load reload latency, branch misprediction completion, threshold events, and a thread-concurrency instruction counter. All event names and event codes are unique within the file.

## APIs, types, and schema

Each array entry uses the event schema consumed by `jevents.py`: `EventName`, `EventCode`, and `BriefDescription`. The generated `JsonEvent` stores the lower-case event name, `default_core` PMU target, normalized description, and `event=<code>` encoding. This file contains no metrics; it exposes raw events that can be selected directly by perf and referenced by POWER9 metric formulas in `metrics.json`.

## Control flow and integration

`arch/powerpc/mapfile.csv` maps POWER9 PVRs to the `power9` directory. The perf build includes this JSON with the other POWER9 files, then `jevents.py` sorts and emits compact PMU event rows into `pmu-events.c`. These entries integrate with the generated POWER9 table used by perf listing, raw event lookup, and metric expression resolution. They also provide raw inputs for higher-level CPI and cache/memory-source metrics.

## State, persistence, and dependencies

The file is source data only; runtime state lives in perf's generated tables and the kernel PMU counters. It depends on the POWER9 PMU event schema, valid hexadecimal event encodings, and consistent naming with metric expressions such as `PM_BR_MPRED_CMPL`, `PM_CMPLU_STALL_FXLONG`, and `PM_CMPLU_STALL_LMQ_FULL`.

## Risks and test signals

Risks include topic mismatch, event-code mistakes, or descriptions that imply a different scope than the hardware counter actually measures. Several entries describe shared core behavior or marked-instruction latency, so consumers can misinterpret per-thread versus core-wide counts. Test signals include JSON parsing, a successful `pmu-events.c` generation, no duplicate event assertions, and metric tests proving any formulas that use these event names still parse and resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/floating-point.json

## Purpose

This small POWER9 topic file defines 6 PMU events assigned to the floating-point JSON partition. The entries are mixed: one marked-load L2 dispatch-conflict latency counter, one IFU memory locality threshold counter, one radix page-walk cache reload counter, one completion flush counter, one marked DERAT miss page-size counter, and one threshold-not-met counter. The file therefore behaves more like a topic shard from the upstream PMU catalog than a pure floating-point-only event set.

## APIs, types, and schema

The JSON entries use `EventName`, `EventCode`, and `BriefDescription`. `jevents.py` maps these fields into `JsonEvent` instances and ultimately compact C event rows. No `MetricName` or `MetricExpr` objects are present, so this file contributes raw selectable events only.

## Control flow and integration

POWER9 model selection comes from `arch/powerpc/mapfile.csv`; the build then treats every JSON file under `power9` as part of the same generated PMU model. This file's events are read by `read_json_events`, assigned the topic derived from the file name, sorted with other `default_core` events, and emitted into the generated `pmu-events.c`. At runtime, perf can list and select the lower-case versions of these event names.

## State, persistence, and dependencies

The file stores static PMU metadata. It depends on the perf JSON schema and the POWER9 event encodings remaining valid. Because it includes threshold and marked-event semantics, correct use also depends on kernel PMU support for the relevant POWER9 counter modes.

## Risks and test signals

The main risk is semantic discoverability: the filename suggests floating-point, but several events relate to translation, threshold, and flush behavior. Automated users should rely on event names and descriptions rather than the file topic alone. Test signals are `jq empty`, successful `jevents.py` generation, no duplicate generated event names, and targeted `perf list` checks for the six event names on POWER9.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/frontend.json

## Purpose

This POWER9 file defines 71 frontend-adjacent PMU events. It covers instruction-side PTEG reload sources, dispatch and issue holds, instruction fetch pump-scope prediction, branch completion and synchronization markers, L1 instruction-cache reloads, and several load/store or data-source counters that interact with frontend or pipeline flow. Within the file all event names are unique and each event has an event code and short description.

## APIs, types, and schema

The file exports event metadata through the standard perf PMU JSON schema: `EventName`, `EventCode`, and `BriefDescription`. `JsonEvent` lower-cases the name for generated lookup, normalizes the description, assigns the default core PMU, and emits an `event=<hex>` string into the compact generated table. It contains no metric objects, but several event names are used by POWER9 derived metrics.

## Control flow and integration

The POWER9 model path is selected by the PowerPC mapfile. During build, `pmu-events/Build` includes this file in `SRC_JSON`; with an output directory it may copy it into the generated `pmu-events/arch` tree before invoking `jevents.py`. The generator adds the entries to the pending POWER9 event table, groups them by PMU name, and writes compact rows into `pmu-events.c`. Runtime consumers are perf event lookup, `perf list`, and metric expression evaluation.

## State, persistence, and dependencies

State is static source JSON plus generated C output. Dependencies include valid JSON, stable POWER9 counter encodings, kernel support for POWER9 PMU events, and consistency with formula references such as instruction-fetch, branch, and dispatch-stall metrics.

## Risks and test signals

Risks are split across hardware semantics and catalog consistency. Many counters include core-shared resources, marked events, or pump-scope speculation, so bad descriptions can lead to incorrect performance interpretation. Formula consumers can also break if event names are renamed. Test signals include JSON validation, a full perf build with `pmu-events.c` regeneration, metric parsing, duplicate-name assertions in `jevents.py`, and hardware spot checks for representative instruction-fetch, branch, and dispatch-hold events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/marked.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/marked.json

## Purpose

This POWER9 file defines 125 PMU events centered on marked-instruction sampling, marked loads/stores, marked branch behavior, marked translation reloads, and related stall or cache-source attribution. It also includes unmarked supporting events such as radix page-walk cache reloads and data or instruction reload sources. The file is a key source for latency and attribution workflows because marked events let perf correlate selected sampled operations with memory, branch, or completion behavior.

## APIs, types, and schema

Each entry is a raw event object with `EventName`, `EventCode`, and `BriefDescription`. `jevents.py` parses the entries into `JsonEvent` objects, converts event codes to generated `event=...` strings, and emits compact event metadata. No metric formulas are declared here, but many entries provide raw event names used by POWER9 metrics and user-authored perf commands.

## Control flow and integration

The file participates in the normal POWER9 directory generation path. The generator reads all model JSON files, assigns the file-derived topic, normalizes names, checks duplicate event names within each generated PMU table, and stores strings in a shared compact string table. The generated table is linked through `libpmu-events.a` and used by perf at runtime when the current processor matches the POWER9 mapfile pattern.

## State, persistence, and dependencies

The file has no mutable state. It persists as PMU metadata and feeds generated code. It depends on the POWER9 PMU's marked-event semantics, sampling support, event-code accuracy, and naming stability across metric expressions and perf user interfaces.

## Risks and test signals

Marked events are easy to misuse because counts can represent sampled or marked subsets rather than all operations. Several descriptions also distinguish radix PTE reloads from PDE reloads, local versus remote cache hierarchy, and completion versus dispatch timing. Regression tests should include `jq empty`, `jevents.py` generation, duplicate-event detection, metric parse tests for formulas referencing marked names, and hardware validation of representative marked load, marked store, marked branch, and marked translation events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/marked.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/memory.json

## Purpose

This POWER9 file defines 25 memory-oriented PMU events. The set includes nest reference clock, PMC overflow and rewind events, dispatch address request queue occupancy, data reload sources from local and distant caches, run counters, DERAT miss reloads, completed loads, and synchronous marked events. It provides raw counters used for memory hierarchy analysis and for general denominator or control signals in POWER9 perf measurements.

## APIs, types, and schema

The entries use the raw event schema consumed by `JsonEvent`: `EventName`, `EventCode`, and `BriefDescription`. The generator maps each object to a default core PMU event and emits compact metadata in generated C. This file does not define `MetricExpr` objects, but its event names are relevant to broader POWER9 metric formulas.

## Control flow and integration

Build integration is the standard `pmu-events/Build` path: include POWER9 JSON sources, optionally copy them to the output tree, run metric syntax tests, and invoke `jevents.py` to generate `pmu-events.c`. Runtime integration is through the generated POWER9 PMU event table selected by the PowerPC PVR map. The event names become available to `perf list`, `perf stat -e`, and metric expressions.

## State, persistence, and dependencies

The file is static hardware metadata. It depends on valid POWER9 event codes, the perf JSON schema, and kernel PMU support for memory, run, and PMC-control counters. Some counters are core resources rather than purely per-thread measures, so the measurement context affects interpretation.

## Risks and test signals

Risks include confusing run-state counters with memory-source counters, misinterpreting queue occupancy as per-thread state, or breaking formulas by renaming event symbols. `PM_NEST_REF_CLK` is especially descriptive-sensitive because its description says to multiply by 4 to obtain PB cycles. Test signals are syntax validation, generated C regeneration, duplicate-name checks, metric parse coverage, and on-hardware comparison of memory-source counts against expected workload locality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/metrics.json

## Purpose

This file defines 318 POWER9 derived metrics. The metrics cover branch prediction, CPI breakdown, data-cache reload percentages by source, estimated data-cache miss CPI, general IPC/CPI and miss rates, instruction-source percentages, L2 stats, latency estimates, LSU rejects, memory locality, prefetch, PTEG reloads, and translation ratios. Metric groups include `branch_prediction`, `cpi_breakdown`, `general`, `memory`, `latency`, `translation`, and other focused groups.

## APIs, types, and schema

Each object uses the metric schema consumed by `JsonEvent`: `MetricName`, `MetricGroup`, `MetricExpr`, and usually `BriefDescription`. `jevents.py` parses `MetricExpr` with `metric.ParsePerfJson(...).Simplify()`, stores the result as a generated metric expression, and may rewrite metrics in terms of other metrics with `metric.RewriteMetricsInTermsOfOthers`. Unlike event files, there is no `EventCode`; the public API is the metric name and expression available to perf metric groups.

## Control flow and integration

The file is loaded with all other POWER9 JSON files. Metrics are collected into pending metric tables, deduplicated by metric name and PMU, sorted, and emitted into generated `pmu-events.c`. At runtime, perf metric commands resolve raw PMU events and derived metric names from these expressions. Cross-file integration is heavy: this file references 219 distinct `PM_*` raw events, and all direct `PM_*` references observed in the expressions are present in the POWER9 JSON directory.

## State, persistence, and dependencies

The file is static formula metadata persisted in source and generated C. It depends on raw event names from the POWER9 event JSON files, the perf metric expression parser, expression rewrite rules, and correct denominator semantics. Several formulas depend on other derived metrics, so the metric graph must remain acyclic and parseable.

## Risks and test signals

The major risks are formula drift, divide-by-zero behavior in low-count workloads, derived-metric dependency mistakes, and raw event renames. CPI breakdown formulas are particularly sensitive because some entries subtract other derived metrics and can produce misleading negative values if component events are unavailable or not mutually exclusive. Test signals include `jq empty`, `pmu-events/metric_test.py`, full `jevents.py` generation, checking unresolved `PM_*` references, and representative `perf stat -M` runs for branch, CPI, memory, latency, and translation groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/nest_metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/nest_metrics.json

## Purpose

This file defines 10 POWER9 nest and memory-bandwidth metrics. It covers chip-level read and write memory bandwidth, PowerBUS frequency, a core-domain 32 MHz cycle metric, per-MCS read/write bandwidth metrics, a powerbus frequency metric, and an aggregate MCS memory-bandwidth metric. Unlike the core metric file, these expressions target uncore-like PMUs such as `hv_24x7`, `nest_mcs01_imc`, `nest_mcs23_imc`, and `nest_powerbus0_imc`.

## APIs, types, and schema

Entries use metric fields: `MetricName`, `MetricGroup`, `MetricExpr`, `ScaleUnit`, and sometimes `AggregationMode`. `jevents.py` maps `AggregationMode` values such as `PerChip` and `PerCore` into generated aggregation enum values, uses `ScaleUnit` as the metric unit, and parses escaped perf PMU expressions. The file contains no raw `EventCode` entries.

## Control flow and integration

The file is part of the POWER9 model directory, but its expressions reference named events exposed by nest or hypervisor PMUs rather than by the default core event table. The generator treats the objects as metric rows and emits them into the POWER9 metric table. At runtime, perf must resolve the PMU-qualified expression syntax, including escaped commas and placeholder selectors such as `chip=?` or `core=?`.

## State, persistence, and dependencies

The file has no mutable state. It persists metric formulas that depend on platform PMU availability, hypervisor support for `hv_24x7`, nest IMC PMU names, scaling units, and aggregation semantics. Hardware topology and firmware exposure can affect whether these metrics are usable on a given POWER9 machine.

## Risks and test signals

Risks are mostly integration-related: missing nest PMUs, changed event names, bad escaping in PMU-qualified expressions, incorrect scale units, or aggregation mismatches. The chip-level bandwidth metrics use `AggregationMode`, so perf aggregation behavior should be checked explicitly. Test signals include JSON parsing, metric parser tests, generated C inspection for `aggr_mode`, and hardware `perf stat -M` runs on systems exposing `hv_24x7` and nest IMC PMUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/nest_metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/other.json

## Purpose

This is the largest POWER9 raw-event shard in the work item, defining 467 PMU events. It acts as a broad catch-all catalog for events not placed in the more focused topic files: issue-unit rejects, snoops, instruction-cache demand requests, transactional-memory instructions, queue occupancy, IERAT reloads, L3 retries, dispatch holds, branch predictors, prefetch streams, many marked events, translation events, memory hierarchy sources, and assorted pipeline or nest-adjacent counters.

## APIs, types, and schema

Every entry follows the raw PMU event schema with `EventName`, `EventCode`, and `BriefDescription`. `jevents.py` converts each entry into a compact generated event row under the default core PMU unless a `Unit` field says otherwise; this file uses the simple core-event shape. The generated names are lower-case, while metric formulas and source JSON retain the original `PM_*` names.

## Control flow and integration

The file is loaded with the rest of the POWER9 directory and contributes a large share of the generated POWER9 event table. It is also a dependency surface for `metrics.json`: many formulas rely on raw event names defined here rather than in the smaller topic files. Build flow is `pmu-events/Build` to `jevents.py` to generated `pmu-events.c`, then runtime lookup through perf's PMU event and metric APIs.

## State, persistence, and dependencies

The JSON is static metadata. It depends on POWER9 PMU encoding correctness, consistent event naming, valid descriptions, and the generator's ability to reject duplicate event names. Because it contains a wide semantic mix, users and metrics depend on the event name and description more than on the topic filename.

## Risks and test signals

The main risks are catalog sprawl and hidden coupling: a rename or deletion can break metric formulas far from this file, and a wrong event code can affect many user workflows. The catch-all topic also makes semantic review harder. Strong test signals include `jq empty`, full `jevents.py` generation, duplicate-name assertions, cross-checking `metrics.json` event references, and representative `perf list` or `perf stat -e` checks for issue, branch, transactional-memory, translation, and cache-source events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/pipeline.json

## Purpose

This POWER9 file defines 106 pipeline-oriented PMU events. It includes execution-unit busy and idle counters, IERAT and DERAT reloads, marked load misses, PMC overflow controls, completion stalls, data-source attribution for marked loads, PTEG reload sources, completed instructions, vector/scalar unit activity, dispatch behavior, and other pipeline flow signals. The file is important for CPI breakdown and bottleneck analysis.

## APIs, types, and schema

The file uses the raw event schema: `EventName`, `EventCode`, and `BriefDescription`. `jevents.py` creates `JsonEvent` objects, converts event codes, assigns descriptions, and emits compact C rows. No metric objects are declared in this file, but many events are building blocks for the POWER9 `metrics.json` CPI, execution-unit, translation, and memory formulas.

## Control flow and integration

The file is selected as part of the POWER9 model directory by the PowerPC mapfile. `pmu-events/Build` includes it in JSON inputs; `jevents.py` adds its events to the generated POWER9 table and validates against duplicate generated names. At runtime, perf exposes the lower-case event names and resolves formulas that reference the original `PM_*` event symbols.

## State, persistence, and dependencies

The file is static source metadata with generated C as the build artifact. It depends on POWER9 counter encoding, kernel PMU support, and stable names for metric references. Because pipeline events often count cycles, completion slots, or marked subsets, correct interpretation depends on workload context and perf aggregation mode.

## Risks and test signals

Risks include misclassifying events as pipeline-only when they reflect translation or memory hierarchy behavior, formula breakage from renames, and hardware semantic mismatches for marked or per-slice counters. Test signals include JSON validation, successful perf PMU event generation, duplicate-name checks, metric parser coverage, and on-hardware checks of representative completion, execution-unit, instruction-completion, and marked-load events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/pipeline.json -->
