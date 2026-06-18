# subset-b-006742

Grouped research for Westmere EX perf PMU event metadata and the shared ARM64 metric generator helpers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/cache.json

Purpose: declares 324 Westmere EX core PMU event rows for cache, cache-coherency, retired memory-load source, offcore request, and offcore response analysis. It is declarative perf metadata rather than executable code; each JSON object is an event definition consumed by perf's pmu-events/jevents pipeline to expose symbolic event names such as `L2_RQSTS.LOADS` and `OFFCORE_RESPONSE.DEMAND_DATA_RD.LOCAL_CACHE_DRAM`.

Important APIs/types/functions: the file uses the perf PMU event JSON schema. Key fields are `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`; selected rows add `PEBS`, `CounterMask`, `MSRIndex`, and `MSRValue`. The high-risk API surface is the pair of filter MSRs: 203 `OFFCORE_RESPONSE.*` rows program `MSRIndex` `0x1A6` with request/response filter values, while 15 `MEM_INST_RETIRED.LATENCY_ABOVE_THRESHOLD_*` rows program `MSRIndex` `0x3F6` for PEBS load-latency thresholds. Counter constraints vary: most generic events allow `0,1,2,3`, offcore responses are constrained to counter `2`, load-latency threshold events are constrained to counter `3`, and a few lock/L1 events use `0,1` or `0`.

Control flow: there is no runtime control flow in this file. Build-time control flow is data ingestion: the perf build enumerates JSON files under `pmu-events/arch/x86/westmereex`, validates/compacts them through jevents, and emits C tables used by `perf list`, `perf stat`, and `perf record`. Runtime selection happens when a user asks for an event name; perf translates this row into raw event code, unit mask, counter restrictions, PEBS capability, sample period, and optional MSR programming.

State and persistence: the source file is static repository data. The only mutable state it influences is kernel/perf PMU programming while a measurement is active, especially offcore response MSR state and load-latency threshold MSR state. No measurements or counters persist back to the file.

Dependencies: depends on the x86 PMU JSON schema and Westmere EX architectural event encodings. It integrates with the sibling category files in the same model directory and with perf's event parser, jevents generator, and x86 PMU driver support for offcore-response and PEBS events.

Integration points: cache events provide user-facing names for L1D/L1I/L2 behavior, LLC/longest-latency cache references, store blocks, offcore queues, remote/local cache and DRAM source attribution, and precise retired memory-source events. Higher-level metrics in `intel_metrics.py` can reference these event names via `Event(...)` once the model event set is loaded by `metric.py`.

Risks: offcore rows are easy to corrupt because each `MSRValue` encodes both request type and response source; a typo can silently report the wrong locality or request class. Counter restrictions matter because many offcore rows only work on counter `2` and load-latency rows only on counter `3`. PEBS markings must remain aligned with hardware support or sampling can fail or degrade to non-precise behavior. The table is large and repetitive, so duplicate names, malformed hex values, or missing commas would break generation or hide individual events.

Test signals: `python3 -m json.tool` should parse the file. Structural checks should assert unique `EventName` values, required fields on each event row, valid hex strings for `EventCode`/`UMask`/`MSRValue`, expected counts for `MSRIndex` `0x1A6` and `0x3F6`, and no offcore response rows without counter `2`. Integration tests are perf build/jevents generation and smoke checks with `perf list` on a tree containing Westmere EX events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/counter.json

Purpose: declares the Westmere EX core PMU counter inventory for perf's event metadata system. It tells perf that the `core` PMU has four fixed counters and four generic programmable counters.

Important APIs/types/functions: the file contains a single JSON object with `Unit: "core"`, `CountersNumFixed: "4"`, and `CountersNumGeneric: "4"`. These fields are schema-level metadata rather than event definitions; there is no `EventName`, `EventCode`, or `BriefDescription` because the row describes the PMU unit itself.

Control flow: there is no executable flow. During pmu-events generation, the row is loaded alongside event rows and becomes model metadata used by perf tooling when displaying or reasoning about available counters.

State and persistence: static source metadata only. It does not store measurements or alter persistent system state.

Dependencies: depends on perf's PMU JSON parser recognizing unit rows with `Unit` and counter-count fields. It must stay consistent with counter constraints in sibling event files, especially fixed-counter rows in `pipeline.json` and counter-specific offcore/load-latency events in `cache.json` and `memory.json`.

Integration points: integrates with all Westmere EX event categories under the same directory by defining the counter capacity those events target. It also complements perf's runtime PMU discovery; mismatches between this static metadata and kernel PMU capabilities can cause confusing event scheduling or display behavior.

Risks: an incorrect generic or fixed counter count would skew perf's generated metadata and may lead users or tooling to expect unsupported counter scheduling. Because the row has no event name, validators must distinguish it from malformed event rows.

Test signals: JSON parsing is the primary syntax check. Schema tests should verify exactly one unit row for `core`, numeric string values for both counter counts, and consistency with event `Counter` references such as `Fixed counter 1`, `Fixed counter 2`, `Fixed counter 3`, and generic `0,1,2,3`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/floating-point.json

Purpose: declares 28 Westmere EX floating-point, MMX, SSE, and SIMD integer PMU events for perf. The file covers x87/FP assists, FP-to-MMX transition behavior, computational FP operations, and 64-bit/128-bit SIMD integer operation classes.

Important APIs/types/functions: each row uses the perf event JSON schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`; three `FP_ASSIST.*` rows also carry `PEBS: "1"`. Event families are `FP_ASSIST`, `FP_COMP_OPS_EXE`, `FP_MMX_TRANS`, `SIMD_INT_128`, and `SIMD_INT_64`. All events allow generic counters `0,1,2,3`.

Control flow: no code executes here. The perf generator loads the rows, and runtime perf commands map symbolic event names to raw event code/unit-mask pairs. PEBS-capable assist events can be used for precise sampling when supported by the kernel and hardware.

State and persistence: static metadata only. At measurement time it affects PMU programming and, for precise assist events, PEBS sampling configuration; no state is persisted in the repository.

Dependencies: depends on Westmere EX event encodings and perf's event JSON schema. It also indirectly supports generated metric scripts that validate `Event(...)` names against loaded JSON events.

Integration points: these events are exposed to `perf list` and can be used by `perf stat`, `perf record`, or higher-level metric definitions for FP/SIMD workload characterization. The file complements `pipeline.json`, which also includes `SSEX_UOPS_RETIRED.*` precise SIMD uop retirement events.

Risks: FP and SIMD terminology overlaps with pipeline events, so event names and descriptions must stay precise enough to avoid users mixing executed operations with retired uops. PEBS flags on assist events are semantically important; removing them loses precise sampling. Incorrect `UMask` values can merge or split operation classes incorrectly.

Test signals: parse with `python3 -m json.tool`; verify all 28 rows have unique `EventName` values and required fields; verify all counters are `0,1,2,3`; verify only `FP_ASSIST.*` rows carry `PEBS` in this file. Integration signal is successful pmu-events generation and visibility of representative names such as `FP_COMP_OPS_EXE.SSE_FP` and `SIMD_INT_128.PACKED_ARITH` in generated event lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/frontend.json

Purpose: declares three Westmere EX frontend decode PMU events: decoded macro-instructions, decoded macro-fusions, and decoded two-uop instructions.

Important APIs/types/functions: the rows use `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`. All three use generic counters `0,1,2,3`, `UMask` `0x1`, and a default sample-after value of `2000000`.

Control flow: no local execution. The rows are consumed by perf's PMU event generation and later selected by symbolic names such as `MACRO_INSTS.DECODED` or `TWO_UOP_INSTS_DECODED`.

State and persistence: static event metadata only. Runtime perf sessions program counters based on these rows; no persistent state is modified.

Dependencies: depends on Westmere EX frontend event encodings and the perf PMU JSON schema. It is intentionally narrow and complements broader branch, uop, and instruction queue coverage in `pipeline.json`.

Integration points: integrates with `perf list` and perf event lookup for frontend decode analysis. Higher-level metrics may combine these frontend counts with instruction-retired or uop events from `pipeline.json` to reason about decode efficiency and macro-fusion behavior.

Risks: because the file is tiny, accidental deletion or renaming of one row would remove a substantial fraction of Westmere EX frontend coverage. The events have similar field shapes, so copy/paste changes to `EventCode` or `EventName` are the main risk.

Test signals: JSON parse, exactly three rows, unique names, all required fields present, and successful generated perf event listing for the three names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/memory.json

Purpose: declares 68 Westmere EX memory-locality PMU events for perf. It focuses on misaligned stores and offcore response classifications for DRAM, LLC miss, local DRAM, and remote DRAM outcomes across request types.

Important APIs/types/functions: most rows are `OFFCORE_RESPONSE.*` events with `EventCode` `0xB7`, `UMask` `0x1`, `Counter` `2`, `MSRIndex` `0x1A6`, and a request/response-specific `MSRValue`. The lone non-offcore row is `MISALIGN_MEM_REF.STORE` using `EventCode` `0x5`, `UMask` `0x2`, generic counters `0,1,2,3`, and sample-after `200000`.

Control flow: there is no executable control flow. Perf's event-generation path reads the JSON objects and produces event tables. At runtime, selecting an offcore event causes perf to program the raw event plus the offcore response MSR filter so the counter observes the requested memory outcome.

State and persistence: static metadata in the repository. Runtime state is limited to transient PMU counter programming and offcore MSR configuration during perf measurements.

Dependencies: depends on the x86 offcore response programming model for Westmere EX and perf support for `MSRIndex`/`MSRValue` fields. It overlaps intentionally with `cache.json`, which contains broader offcore response categories including cache, IO/MMIO, and combined cache/DRAM outcomes.

Integration points: exposed as `perf` event aliases for memory locality and NUMA-like analysis on Westmere EX. Request classes include data reads, instruction fetches, RFOs, writebacks, demand/prefetch splits, and aggregate request groups. These event names can also be referenced by generated metrics after `metric.py` loads model events.

Risks: every offcore row is counter-specific and MSR-specific; wrong `MSRValue` values would produce plausible but false locality data. The `OTHER.LOCAL_DRAM` combination is absent while related combinations exist, so validators should avoid assuming a complete 4-way matrix for every request prefix. Moving rows between `memory.json` and `cache.json` without preserving names may break metric references.

Test signals: JSON parse; 68 rows; 67 rows with `MSRIndex` `0x1A6`; all offcore rows constrained to counter `2`; unique event names; valid hex `MSRValue` strings. Integration checks should build the pmu-events tables and inspect generated `perf list` output for representative local/remote DRAM aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/other.json

Purpose: declares 23 miscellaneous Westmere EX PMU events that do not fit the cache, frontend, FP, memory, pipeline, or virtual-memory buckets. It covers segment renames, I/O transactions, load dispatch/blocking, store-buffer drain behavior, snoop queue requests/outstanding cycles, snoop responses, and super-queue full stalls.

Important APIs/types/functions: rows use the standard perf PMU JSON fields `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`; three outstanding-cycle rows add `CounterMask: "1"`. Six `SNOOPQ_REQUESTS_OUTSTANDING.*` rows are constrained to counter `0`; most other rows allow `0,1,2,3`.

Control flow: declarative only. The perf generator reads the rows and runtime perf uses them to program counters for miscellaneous memory-ordering, snoop, and queue-pressure conditions.

State and persistence: no persistent runtime state. PMU configuration is transient during measurement.

Dependencies: depends on Westmere EX event encodings and perf's support for counter masks and counter constraints. Snoop events are semantically tied to the cache-coherency/offcore coverage in `cache.json` and `memory.json`.

Integration points: exposed through generated perf event tables. The file gives users access to events such as `LOAD_DISPATCH.ANY`, `PARTIAL_ADDRESS_ALIAS`, `SNOOP_RESPONSE.HITM`, and `SQ_FULL_STALL_CYCLES` for diagnosing queue pressure, false dependencies, and coherency behavior.

Risks: the category is heterogeneous, so broad automated edits are risky. Counter `0` restrictions on outstanding snoop queue events and `CounterMask` usage must be preserved. Descriptions are the main user documentation surfaced by `perf list`; vague or incorrect text can lead to misinterpretation.

Test signals: parse as JSON; verify 23 unique event names; verify the six `SNOOPQ_REQUESTS_OUTSTANDING.*` rows use counter `0`; verify `CounterMask` appears only where intended; build-generated event tables and spot-check miscellaneous aliases in `perf list`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/pipeline.json

Purpose: declares 111 Westmere EX pipeline, branch, instruction, uop, stall, and fixed-counter PMU events for perf. It is the main model table for execution pipeline analysis.

Important APIs/types/functions: rows use standard event fields plus several hardware qualifiers: `PEBS` for precise retired events, `AnyThread` for all-thread fixed/programmed cycle and instruction counts, `CounterMask`, `Invert`, and `EdgeDetect` for cycle/threshold-style events. Event families include `ARITH`, `BACLEAR`, `BPU_CLEARS`, `BR_INST_EXEC`, `BR_MISP_EXEC`, `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `ILD_STALL`, `INST_RETIRED`, `MACHINE_CLEARS`, `RAT_STALLS`, `RESOURCE_STALLS`, `SSEX_UOPS_RETIRED`, `UOPS_DECODED`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`.

Control flow: no executable code. Build-time generation transforms these JSON rows into perf event tables. Runtime control is in perf and the kernel PMU driver, which interpret event code, unit mask, fixed/generic counter selection, precise-event flags, any-thread flags, and counter-mask/invert/edge settings.

State and persistence: static metadata only. During measurement it controls transient PMU programming, including fixed counters `Fixed counter 1`, `Fixed counter 2`, and `Fixed counter 3`, PEBS setup for precise events, and threshold/cycle qualification.

Dependencies: depends on Westmere EX PMU semantics and perf's parser for fixed counters, any-thread counting, PEBS, edge detect, invert, and counter masks. It also depends on `counter.json` being consistent with the fixed/generic counter inventory.

Integration points: these events are the core aliases for `perf stat`/`perf record` pipeline diagnosis. They complement `frontend.json` for decode, `floating-point.json` for operation classes, and `virtual-memory.json` for TLB behavior. Metric-generation scripts can validate and reference these names through `metric.Event` after loading the model directory.

Risks: this file has the densest mix of special qualifiers. Losing `AnyThread` changes count scope; losing `PEBS` changes sampling precision; wrong `CounterMask`/`Invert`/`EdgeDetect` changes event meaning for cycle and occurrence counts. Fixed-counter labels must remain exactly in the syntax perf expects. Some descriptions are absent from two rows, so validators should distinguish known sparse metadata from parse failures.

Test signals: JSON parse; 111 unique event names; expected fixed-counter rows for `CPU_CLK_UNHALTED` and `INST_RETIRED`; qualifier checks for 10 `AnyThread` rows, PEBS-marked retired events, and intended `CounterMask`/`Invert`/`EdgeDetect` usage. Full integration signal is successful pmu-events generation and representative `perf list` coverage for branch, uop, stall, and fixed-counter aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/virtual-memory.json

Purpose: declares 22 Westmere EX virtual-memory and TLB PMU events for perf. It covers DTLB load misses, general DTLB misses, ITLB misses and flushes, EPT walk cycles, large ITLB hits, and retired load/store DTLB misses.

Important APIs/types/functions: rows use `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`; three retired DTLB miss rows carry `PEBS: "1"`. Families include `DTLB_LOAD_MISSES`, `DTLB_MISSES`, `ITLB_MISSES`, `EPT`, `ITLB_FLUSH`, `ITLB_MISS_RETIRED`, `LARGE_ITLB`, `MEM_LOAD_RETIRED`, and `MEM_STORE_RETIRED`. All rows allow generic counters `0,1,2,3`.

Control flow: declarative only. The perf PMU event generator ingests the rows, and runtime perf maps symbolic aliases to event code/unit-mask programming. PEBS-capable retired memory rows can be used for precise sampling of DTLB-miss-causing memory operations.

State and persistence: static metadata. Runtime PMU state is temporary and bound to active perf measurements.

Dependencies: depends on Westmere EX DTLB/ITLB/EPT event encodings and perf's JSON schema. It complements memory locality rows in `memory.json` and cache-source rows in `cache.json`.

Integration points: exposed to `perf list`, `perf stat`, and `perf record` for virtual-memory performance diagnosis. These aliases help separate page-walk count, page-walk cycles, STLB hits, large-page walks, instruction-side misses, and retired load/store DTLB misses.

Risks: DTLB family names are similar and easy to confuse (`DTLB_LOAD_MISSES` versus `DTLB_MISSES`). PEBS markings on retired load/store misses should not be copied to non-retired walk events. Incorrect `UMask` values can conflate STLB hits, walks, PDE misses, and large page walks.

Test signals: JSON parse; 22 unique event names; all counters `0,1,2,3`; PEBS only on the intended retired miss rows; generated perf event tables include representative aliases such as `DTLB_LOAD_MISSES.WALK_CYCLES`, `ITLB_MISSES.WALK_COMPLETED`, and `MEM_STORE_RETIRED.DTLB_MISS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arm64_metrics.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arm64_metrics.py

Purpose: command-line generator for ARM64 perf extra metric JSON. It loads an ARM64 vendor/model event directory and emits either metric definitions or metric-group descriptions. In the current implementation it emits the shared privilege-level cycle breakdown from `common_metrics.Cycles()`.

Important APIs/types/functions: imports `argparse`, `os`, `JsonEncodeMetric`, `JsonEncodeMetricGroupDescriptions`, `LoadEvents`, `MetricGroup`, and `Cycles`. The public executable entry point is `main()`. Inside `main`, nested `dir_path(path)` validates that the supplied events root is a directory for `argparse`. Command-line API: optional `-metricgroups`, positional `vendor`, positional `model`, and positional `events_path`. The script constructs `directory = f"{events_path}/arm64/{vendor}/{model}/"`, calls `LoadEvents(directory)`, wraps `Cycles()` in a root `MetricGroup("", [...])`, and prints either metric JSON or group-description JSON.

Control flow: module import initializes `_args = None`. When run as a script, `main()` builds and parses the CLI, validates the root directory, loads model event names for metric validation, constructs the metric tree, then chooses one of two JSON encoders based on `_args.metricgroups`. Output goes to stdout for the build system to redirect into `extra-metrics.json` or `extra-metricgroups.json`.

State and persistence: `_args` is a module-global copy of parsed arguments, but all generated content is derived from source JSON files and printed to stdout. Persistent output is created by the Make/Build rule that redirects stdout, not by this script opening output files.

Dependencies: depends on `metric.py` for event loading, metric tree types, validation, and JSON encoding; depends on `common_metrics.py` for the shared `Cycles()` metric group; depends on a valid `pmu-events/arch/arm64/<vendor>/<model>/` directory. The build file invokes it for ARM model directories, excluding CMN directories, when `JEVENTS_ARCH` includes `arm64` or `all`.

Integration points: integrated by `tools/perf/pmu-events/Build` rules for `ARM_METRICS` and `ARM_METRICGROUPS`. The generated JSON is later consumed by perf's pmu-events generation and surfaced as extra ARM metrics. The `LoadEvents` call also validates that `Event("cpu\\-cycles:...")` references used by `Cycles()` are accepted by the loaded model event set or by the built-in generic events in `metric.py`.

Risks: `dir_path` validates only the root `events_path`, not the constructed vendor/model directory; a wrong vendor/model can fail later in `LoadEvents`. The script currently emits only cycle metrics, so ARM64 extra metrics are intentionally sparse. Because it prints to stdout, warnings or debug output added later would corrupt generated JSON. The global `_args` is harmless for script usage but makes repeated in-process calls stateful.

Test signals: run with a known ARM64 events tree and validate JSON parses for both default and `-metricgroups` modes. Unit-style checks can monkeypatch a small events directory and assert the output contains `lpm_cycles_total`, `lpm_cycles_user`, `lpm_cycles_kernel`, `lpm_cycles_guest`, and group description `lpm_cycles`. Build integration is covered by the `ARM_METRICS` and `ARM_METRICGROUPS` targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arm64_metrics.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/common_metrics.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/common_metrics.py

Purpose: defines shared perf metric groups that are reused by architecture-specific metric generators. The current file exposes `Cycles()`, a privilege-level cycle breakdown metric group used by ARM64, Intel, and AMD metric-generation scripts.

Important APIs/types/functions: imports `d_ratio`, `Event`, `Metric`, and `MetricGroup` from `metric.py`. `Cycles() -> MetricGroup` creates three event expressions: `cyc_k = Event("cpu\\-cycles:kHh")` for kernel/hypervisor-side host cycles excluding user and guest, `cyc_g = Event("cpu\\-cycles:G")` for guest cycles excluding host, and `cyc_u = Event("cpu\\-cycles:uH")` for user host cycles excluding kernel, hypervisor, and guest. It sums them into `cyc` and returns a `MetricGroup("lpm_cycles", [...])` containing four metrics: total cycles plus user, kernel, and guest percentages using `d_ratio(part, cyc)` with scale `100%`.

Control flow: no top-level work beyond imports. Calling `Cycles()` constructs expression objects, uses operator overloading from `metric.Expression` subclasses to sum events, creates metrics, and returns a metric group with description `cycles breakdown per privilege level (users, kernel, guest)`.

State and persistence: no module state and no persistence. The returned metric objects are later serialized by architecture-specific scripts through `JsonEncodeMetric` or `JsonEncodeMetricGroupDescriptions`.

Dependencies: tightly depends on `metric.py` expression semantics: `Event` validates event names/modifiers, `d_ratio` emits a perf metric expression, `Metric` normalizes scale units, and `MetricGroup` propagates metric group names. It also depends on perf's event modifier syntax for `cpu-cycles` privilege filters (`kHh`, `G`, `uH`) remaining valid across supported architectures.

Integration points: imported by `arm64_metrics.py`, `intel_metrics.py`, and `amd_metrics.py`. The build system lists it in `GEN_METRIC_DEPS`, so changes trigger regeneration of architecture extra metric JSON. Its metric names are part of the generated user-facing perf metric namespace: `lpm_cycles_total`, `lpm_cycles_user`, `lpm_cycles_kernel`, and `lpm_cycles_guest`.

Risks: event modifier mistakes would change privilege accounting without obvious JSON syntax failures. The denominator `cyc` is the sum of three filtered events; if an architecture or perf mode treats host/guest/hypervisor filters differently, percentages may be misleading. Renaming metric names or the `lpm_cycles` group can break users or tests that rely on stable metric aliases. Division-by-zero behavior is delegated to perf's `d_ratio` implementation.

Test signals: direct serialization test through an architecture generator should produce four metric objects with the expected names, group `lpm_cycles`, `MetricExpr` values containing the three `cpu\\-cycles` filtered events, and scale units `1cycles`/`100%` as normalized by `Metric`. Build-level signal is regeneration of extra metrics for ARM64, Intel, and AMD without validation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/common_metrics.py -->
