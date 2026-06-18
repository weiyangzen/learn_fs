# Research: subset-b-006720

Grouped research for perf PMU event metadata under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/`. These files are declarative JSON inputs consumed by perf's PMU event generation pipeline, not executable runtime code.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/skl-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/skl-metrics.json

## Purpose

This file defines the Skylake client metric catalog used by Linux perf for symbolic `perf stat -M ...` style analysis. It is a JSON array of 222 metric objects. Every object has `MetricName`, `MetricExpr`, `MetricGroup`, and `BriefDescription`; optional fields add display units, public descriptions, metric constraints, threshold expressions, and grouping suppressors.

The catalog covers package and core C-state residency, uncore frequency, SMI accounting, TSX transaction ratios, and a large Intel topdown microarchitecture-analysis hierarchy. The dominant metric namespace is `tma_*`, with level/group tags such as `TopdownL1`, `TopdownL2`, `TopdownL3`, `TopdownL4`, `TopdownL5`, `TopdownL6`, `tma_L*_group`, and domain tags including `Backend`, `Frontend`, `BadSpec`, `Retire`, `Mem`, `MemoryBW`, `MemoryLat`, `MemoryTLB`, `Flops`, `Pipeline`, `PortsUtil`, `Power`, `Summary`, `SMT`, `OS`, and `transaction`.

## Important Schema Fields and APIs

The main external API is the perf PMU JSON schema parsed by `tools/perf/pmu-events/jevents.py`. For metric rows, `jevents.py` reads `MetricName`, `MetricGroup`, `MetricgroupNoGroup`, `MetricConstraint`, `MetricExpr`, `MetricThreshold`, `BriefDescription`, `PublicDescription`, and `ScaleUnit`. `MetricExpr` is parsed through `metric.ParsePerfJson(...).Simplify()`, so formulas must use perf's metric-expression grammar and event aliases visible to the selected CPU model.

Important fields:

- `MetricName`: public symbolic metric identifier, for example `tma_backend_bound`, `tma_info_thread_ipc`, `tma_mem_latency`, `UNCORE_FREQ`, and `tsx_transactional_cycles`.
- `MetricExpr`: expression over raw events, other metrics, constants, helper functions, and scaling terms. This is the behavioral core of the file.
- `MetricGroup`: semicolon-delimited group membership used by perf list/stat filtering and topdown presentation.
- `ScaleUnit`: optional rendering unit such as percentages, cycles, bandwidth, IPC-like ratios, or time/power units.
- `MetricConstraint`: optional grouping/scheduling constraint. Present on 53 rows and used by `jevents.py` as `event_grouping`.
- `MetricThreshold`: optional display threshold string. Present on 139 rows; unlike `MetricExpr`, `jevents.py` keeps thresholds as strings because boolean operator precedence is not parsed the same way.
- `MetricgroupNoGroup`: optional flag present on 12 rows to avoid automatic grouping behavior.

## Control Flow and Data Flow

There is no imperative control flow in this file. Build-time control flow is:

1. The perf build scans `tools/perf/pmu-events/arch/x86/skylake/` as the model directory selected by `arch/x86/mapfile.csv`.
2. `jevents.py` loads this JSON array, validates each object as either an event or a metric row, and parses each `MetricExpr`.
3. The generator emits C tables in generated `pmu-events.c`, with metric names, expressions, groups, descriptions, units, and constraints embedded in `struct pmu_event`/metric metadata.
4. At runtime, perf matches the running CPU to the Skylake map entry, exposes the metric aliases, and evaluates formulas by scheduling the referenced PMU events.

Data dependencies flow from metric names to lower-level event names in neighboring Skylake JSON files such as `cache.json`, `frontend.json`, `memory.json`, `pipeline.json`, `virtual-memory.json`, and uncore event files. Some metrics also depend on common perf aliases, fixed counters, topdown slot events, package C-state events, RAPL/power events, and synthetic perf helper terms.

## State and Persistence

The file is static source metadata. Its only persistent effect is through generated perf build artifacts: generated `pmu-events.c`, compiled `pmu-events.o`, and the resulting perf binary's embedded PMU tables. It does not store runtime state. Runtime metric values are computed from current PMU counter samples; no sampled state is persisted back into this JSON.

## Dependencies and Integration Points

This file integrates with:

- `tools/perf/pmu-events/Build`, which regenerates Intel metric files and then drives `jevents.py`.
- `tools/perf/pmu-events/jevents.py`, which parses the JSON and emits generated C.
- `tools/perf/pmu-events/metric.py` and `metric_test.py`, which parse and test metric-expression syntax.
- `tools/perf/builtin-list.c`, which can print metric metadata back out for `perf list` JSON/text views.
- The x86 mapfile, which controls when the Skylake directory is selected.
- Adjacent raw event JSON files whose `EventName` values are referenced by `MetricExpr`.

Because this is a client Skylake metric set, it should not be mixed with Skylake-X server metrics unless the mapfile explicitly maps a CPU model to that directory. The formulas encode microarchitecture-specific topdown assumptions, counter availability, and event meanings.

## Risks

The highest risk is expression drift: a renamed, removed, or architecture-mismatched raw event breaks metric evaluation even when the JSON remains syntactically valid. Metric formulas are also sensitive to counter multiplexing, SMT assumptions, frequency scaling, offcore response encodings, and kernel/perf support for fixed counters and topdown slots.

Threshold strings are not parsed by the same path as `MetricExpr`, so syntax problems may evade expression-parser coverage. `MetricConstraint` rows can reduce schedulability; incorrect constraints may produce inaccurate multiplexed values or prevent metric groups from running together. Scale-unit mistakes are presentation bugs but can lead users to misread ratios as percentages or bandwidth as counts.

## Test Signals

Useful validation signals include `jq` parsing, `metric_test.py` coverage for expression grammar, perf build regeneration of `pmu-events.c`, and perf tests under `tools/perf/tests/pmu-events.c` and `tools/perf/tests/parse-metric.c`. Runtime smoke tests should include `perf list --json` for representative `MetricName` values and `perf stat -M` for topdown, memory, power, TSX, and SMI metrics on actual Skylake client hardware or a compatible perf test fixture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/skl-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/uncore-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/uncore-cache.json

## Purpose

This file defines 15 Skylake client uncore cache events. The events expose last-level cache/coherency behavior through C-box style uncore counters and socket clock accounting. Event names include `UNC_CBO_CACHE_LOOKUP.*`, `UNC_CBO_XSNP_RESPONSE.*`, and `UNC_CLOCK.SOCKET`.

The file lets perf users name cache-slice/coherency events symbolically rather than programming raw uncore event codes and unit masks. It is especially relevant to system-level cache-hit, invalid-state lookup, write/read MESI-state, cross-core snoop hit, hit-modified, miss, eviction, and socket-cycle analysis.

## Important Schema Fields and APIs

Each object follows the PMU event descriptor schema:

- `EventName`: public alias, lowercased by `jevents.py` for generated perf aliases.
- `EventCode`: raw event selector, for example the CBO lookup or snoop-response selector.
- `UMask`: subevent selector for MESI state, read/write class, or snoop response.
- `Unit`: uncore PMU unit name, here primarily CBO/cache-box units plus the socket clock unit.
- `Counter`: allowed hardware counter selector list for the uncore unit.
- `PerPkg`: marks package-scoped accounting for socket/uncore events.
- `BriefDescription` and optional `PublicDescription`: text surfaced through `perf list`.

These fields are consumed by `jevents.py` into generated `event=...`, `umask=...`, `counter=...`, `perpkg=...`, and PMU/unit mapping strings.

## Control Flow and Data Flow

The file is read at build time as part of the Skylake model directory. The generation flow is JSON array -> `JsonEvent` objects in `jevents.py` -> generated C PMU event table -> runtime perf alias table. At runtime, a user selecting `UNC_CBO_CACHE_LOOKUP.READ_MESI` or similar causes perf to program the matching uncore PMU event code and mask on the package CBO units.

No event in this file calls another event. Higher-level data flow is from these raw events into user commands and potentially into metrics in `skl-metrics.json` that reference uncore cache or socket-clock behavior.

## State and Persistence

This is static metadata. It persists only in generated perf build outputs and in the installed perf binary. Runtime counter state lives in CPU uncore PMU registers and perf's sampling/stat aggregation buffers; it is not written back to this file.

## Dependencies and Integration Points

The file depends on the Skylake uncore PMU naming understood by perf and the kernel PMU drivers. The `Unit` and `PerPkg` fields are important because uncore counters are package-scoped rather than per-thread core counters. Integration points include `jevents.py`, the x86 mapfile's Skylake model mapping, `perf list` alias display, `perf stat -e` uncore event programming, and any Skylake metrics that combine uncore cache counts with core or clock events.

## Risks

Raw uncore encodings are hardware-specific. A wrong `EventCode`, `UMask`, `Counter`, or `Unit` can silently count a different event or fail to schedule. Package-level aggregation can be misinterpreted as per-core data, especially on multi-socket systems. The names encode MESI/snoop semantics; inaccurate descriptions may cause users to confuse lookup state, read/write state, and cross-core snoop response classes.

## Test Signals

Validation should include JSON parsing, generated `pmu-events.c` inspection for the 15 aliases, `perf list` visibility for `UNC_CBO_CACHE_LOOKUP` and `UNC_CBO_XSNP_RESPONSE`, and runtime `perf stat -e` tests on Skylake hardware with uncore PMU support. Tests should verify package aggregation and that restricted `Counter` values are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/uncore-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/uncore-interconnect.json

## Purpose

This file defines 8 Skylake client uncore interconnect/arbitration events. The event set covers arbitration tracker request counts and occupancy, including all requests, data reads, direct DRD requests, writes, coherent tracker requests, and cycles with any request.

The public aliases are `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_TRK_OCCUPANCY.*`, and `UNC_ARB_TRK_REQUESTS.*`. They allow perf users to observe uncore arbitration pressure and request mix without specifying raw codes.

## Important Schema Fields and APIs

The JSON objects use the perf event descriptor schema:

- `EventName`: symbolic alias exposed by perf.
- `EventCode`: uncore arbitration event selector.
- `UMask`: request/occupancy subtype selector.
- `CounterMask`: present on occupancy cycle-style rows to require a minimum condition before counting.
- `Unit`: the uncore arbitration/interconnect PMU unit.
- `Counter`: allowed uncore counter selector.
- `PerPkg`: package-scoped accounting flag.
- `BriefDescription`: surfaced by `perf list`.

`CounterMask` maps through `jevents.py` to `cmask=...`, which changes the event from simple occurrence counting to thresholded cycle counting for the relevant rows.

## Control Flow and Data Flow

The generation flow is the standard perf PMU path: JSON -> `jevents.py` parsing -> generated PMU event table -> runtime alias lookup. At runtime, selecting an `UNC_ARB_*` alias programs the uncore arbitration unit with the given event code, mask, and optional counter mask.

These raw counters can feed manual performance investigations or higher-level metrics that need interconnect occupancy/request rates. There is no internal branching or call graph inside the file.

## State and Persistence

The file is immutable source metadata. Persistent generated state exists only in build artifacts and the perf binary. Live counter state is held in package uncore PMU registers and perf aggregation structures during a profiling run.

## Dependencies and Integration Points

Dependencies are the Skylake uncore arbitration PMU model, kernel support for the listed unit, and perf's JSON event parser. Integration points are `arch/x86/mapfile.csv`, `jevents.py`, generated `pmu-events.c`, `perf list`, and `perf stat` event scheduling. Because all events are package-scoped uncore events, they integrate differently from core PMU events and may require system-wide permissions or root/kernel `perf_event_paranoid` settings.

## Risks

The main risk is semantic ambiguity between request counts and occupancy/cycle counts. `CounterMask` rows are especially easy to misread because they count cycles satisfying a condition rather than requests. Uncore availability varies by SKU, firmware, kernel driver, and virtualization environment; aliases may list but fail to run if the PMU is absent or blocked. Incorrect `PerPkg` handling can lead to double-counting or undercounting in aggregate reports.

## Test Signals

Build-time signals are valid JSON and successful `jevents.py` generation. Runtime signals include `perf list UNC_ARB`, `perf stat -a -e` for each alias on Skylake hardware, and sanity checks that request events increase under memory/interconnect load while occupancy cycle events respond to sustained traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/virtual-memory.json

## Purpose

This file defines 28 Skylake client virtual-memory/TLB events. It covers data-TLB load misses, data-TLB store misses, instruction-TLB misses, EPT walk pending, ITLB flushes, and TLB flush events. The events distinguish STLB hits, page-walk starts/completions, walk-active cycles, walk-pending counts, and page sizes such as 4K, 2M/4M, and 1G.

The event names include `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, `ITLB_MISSES.*`, `EPT.WALK_PENDING`, `ITLB.ITLB_FLUSH`, and `TLB_FLUSH.*`. They provide the raw event layer used for memory-translation analysis and for topdown metrics involving TLB pressure.

## Important Schema Fields and APIs

Each row exposes a core PMU event alias:

- `EventName`: symbolic perf event.
- `EventCode` and `UMask`: raw event selector and subevent mask.
- `Counter`: allowed programmable counters.
- `CounterMask`: present on cycle-thresholded rows such as active/pending walk conditions.
- `SampleAfterValue`: default sampling period for `perf record` style use.
- `BriefDescription` and `PublicDescription`: short and detailed descriptions surfaced to users.

Unlike uncore files, there is no `Unit` field here; these are core PMU events. The `CounterMask` field maps to `cmask=...` in perf event encoding. `SampleAfterValue` affects default sampling behavior but not `perf stat` counting semantics.

## Control Flow and Data Flow

At build time, `jevents.py` converts each descriptor into generated C metadata. At runtime, perf maps symbolic event names to event selectors when the CPU matches the Skylake model. Users can count the events directly or use them through `skl-metrics.json` formulas such as TLB miss ratios, STLB MPKI metrics, and topdown memory-TLB bottleneck nodes.

The data flow is raw PMU increments from TLB hardware -> perf event counts/samples -> direct output or metric-expression inputs. There is no internal control flow within the JSON file.

## State and Persistence

The JSON is source-time static metadata. Generated aliases persist in the perf binary. Runtime state is limited to PMU counters, perf buffers, and sampled records if a user runs a sampling command; no state is persisted by this descriptor file.

## Dependencies and Integration Points

The file integrates with Skylake core PMU support in the kernel, `jevents.py`, the x86 mapfile, generated `pmu-events.c`, and perf metric evaluation. It is tightly coupled to TLB metrics in `skl-metrics.json`, especially metrics involving code STLB misses, load/store STLB misses, page-walk utilization, and memory-data-TLB bottlenecks.

## Risks

TLB event semantics are sensitive to page size, virtualization, EPT usage, and kernel/hypervisor behavior. Some rows count walks completed by page size while others count miss causes, active cycles, or pending cycles; mixing them incorrectly can produce invalid ratios. `CounterMask` and `SampleAfterValue` mistakes may create scheduling or sampling artifacts. Hardware errata or kernel event alias changes could make formulas in the metric file stale.

## Test Signals

Validation should include JSON syntax, generated alias output, `perf list` visibility for `DTLB_*`, `ITLB_*`, `EPT.*`, and `TLB_FLUSH.*`, and runtime tests using workloads with known TLB stress. Metric-level tests should run representative `tma_*tlb*` and `tma_info_memory_tlb_*` metrics to ensure referenced aliases resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/cache.json

## Purpose

This file defines 157 Skylake-X server cache and memory-hierarchy core PMU events. It covers L1D replacements and pending misses, L2 line movement and request classes, longest-latency cache references/misses, retired load/store categories, L3 hit/miss attribution, offcore requests/outstanding requests/responses, snoop/coherency responses, store queue pressure, split locks, software prefetch accesses, and IDI writeback transitions.

The event inventory includes families such as `L1D.*`, `L1D_PEND_MISS.*`, `L2_LINES_*`, `L2_RQSTS.*`, `LONGEST_LAT_CACHE.*`, `MEM_INST_RETIRED.*`, `MEM_LOAD_RETIRED.*`, `MEM_LOAD_L3_HIT_RETIRED.*`, `MEM_LOAD_L3_MISS_RETIRED.*`, `OFFCORE_REQUESTS*`, `OFFCORE_RESPONSE*`, `CORE_SNOOP_RESPONSE.*`, `SQ_MISC.SPLIT_LOCK`, and `SW_PREFETCH_ACCESS.*`.

## Important Schema Fields and APIs

The file uses the perf raw event schema:

- `EventName`: public alias.
- `EventCode` and `UMask`: raw core event selector and subevent mask.
- `Counter`: allowed programmable counters.
- `CounterMask`: present on 7 rows for thresholded cycle/count behavior.
- `AnyThread`: present on one row for any-thread counting.
- `PEBS` and `Data_LA`: present on 24 rows, indicating precise sampling and load-address support.
- `MSRIndex` and `MSRValue`: present on 73 offcore-response rows. These program model-specific offcore response filter registers.
- `SampleAfterValue`: default sampling period for all 157 rows.
- `Deprecated`: present on one row, warning that the alias should not be preferred.
- `Errata`: present on 2 rows and appended by `jevents.py` to generated descriptions.
- `BriefDescription` and `PublicDescription`: user-facing descriptions.

`jevents.py` lowers `AnyThread` to `any=...`, `CounterMask` to `cmask=...`, `MSRIndex`/`MSRValue` to extra MSR programming metadata, `PEBS` to precise-event metadata, and `Data_LA` to an additional address-support note.

## Control Flow and Data Flow

The descriptor flow is JSON -> `JsonEvent` parsing in `jevents.py` -> generated C PMU table -> runtime perf alias matching for Skylake-X CPUs. For simple cache events, perf programs `EventCode`/`UMask` directly. For `OFFCORE_RESPONSE.*` aliases, perf must also program the offcore response MSR filter specified by `MSRIndex` and `MSRValue`; these aliases represent filtered offcore transaction classes rather than only the base event code.

The data feeds direct `perf stat -e` usage, sampling with PEBS-capable memory events, and Skylake-X metrics such as server memory bandwidth, latency, cache hit/miss, snoop, and topdown analyses in adjacent `skx-metrics.json` or generated metric files.

## State and Persistence

The file has no mutable state. Persistent output is generated perf metadata embedded in build artifacts. Runtime state includes core PMU counters, optional precise event records, data linear-address samples for `Data_LA` events, and offcore MSR filter state while perf owns the event.

## Dependencies and Integration Points

This file depends on Skylake-X server core PMU encodings, PEBS support, offcore response MSR definitions, and the kernel perf driver accepting the generated event configuration. Integration points include `jevents.py`, `metric.py` for metrics referencing these aliases, `arch/x86/mapfile.csv`, generated `pmu-events.c`, `perf list`, `perf stat`, and `perf record`.

It also integrates with Skylake-X `counter.json`: many events specify legal generic counters, and the platform has four generic core counters plus fixed counters according to that capacity file. Offcore events may contend for limited MSR/filter resources and cannot always be scheduled freely with other offcore filters.

## Risks

The largest risks are offcore filter correctness and schedulability. `MSRIndex`/`MSRValue` mistakes can silently select the wrong request/response class, and multiple offcore events may conflict on limited filter registers. PEBS/Data_LA rows have privilege, kernel, and hardware constraints; they may not sample addresses in all contexts. Counter restrictions, `AnyThread`, and `CounterMask` can alter meaning or prevent event groups from scheduling. Server Skylake-X cache/coherency semantics differ from client Skylake, so copying events between directories can produce invalid aliases or metrics.

## Test Signals

Build validation should parse JSON and regenerate `pmu-events.c` without duplicate or invalid aliases. Runtime tests should cover `perf list` for each major family, `perf stat -e` for simple L1/L2/L3 events, an offcore response alias with expected traffic, and PEBS sampling for a `MEM_LOAD_*` row. Metric smoke tests should run server cache/memory metrics that depend on these events and check that counter grouping does not fail due to offcore or PEBS constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/counter.json

## Purpose

This file defines the counter capacity table for Skylake-X PMU units. It has 10 rows mapping each PMU `Unit` to the number of fixed counters and generic programmable counters available. Units are `core`, `CHA`, `IIO`, `IRP`, `UPI`, `M2M`, `iMC`, `M3UPI`, `PCU`, and `UBOX`.

The table gives perf's generated metadata a model-specific view of counter resources. For example, `core` has 3 fixed counters and 4 generic counters, `iMC` and `UBOX` each have 1 fixed counter, and most uncore units expose 2 to 4 generic counters with no fixed counters.

## Important Schema Fields and APIs

Each row contains:

- `Unit`: PMU unit name.
- `CountersNumFixed`: count of fixed-function counters for that unit, stored as a string in the JSON.
- `CountersNumGeneric`: count of generic programmable counters for that unit, stored as a string.

This file is not an event list and has no `EventName`, `EventCode`, or `UMask`. It is a resource descriptor consumed by the perf PMU event generation and scheduling metadata path alongside the event JSON files.

## Control Flow and Data Flow

At build time, the Skylake-X directory is scanned and this table is parsed with the rest of the model metadata. The generated perf metadata can use the counts to describe or reason about how many counters exist for each PMU unit. At runtime, these counts inform whether groups of events are likely to fit and help represent PMU unit capabilities consistently with the event descriptors.

There is no internal control flow. The data flow is static resource metadata -> generated C tables -> perf scheduling/listing behavior.

## State and Persistence

The file stores static hardware capacity facts. It does not change at runtime and does not persist sampled state. Generated perf artifacts embed or derive from these values until perf is rebuilt.

## Dependencies and Integration Points

The table integrates with Skylake-X raw event files such as `cache.json`, `floating-point.json`, uncore cache/interconnect/I/O/memory/power files, and metrics that schedule groups across core and uncore PMUs. It depends on unit names matching the `Unit` values used in event descriptors and the kernel PMU names expected by perf.

## Risks

Wrong counter counts can lead to unrealistic metric grouping assumptions, poor scheduling diagnostics, or confusing perf output. Unit-name mismatches are especially risky because they break the relationship between event descriptors and capacity descriptors. Since values are encoded as strings, consumers must parse numeric content consistently; nonnumeric edits would likely fail generation or produce invalid metadata.

## Test Signals

Validation should parse JSON and compare unit names against units used by Skylake-X event files. Runtime signals include `perf list` visibility for unit-scoped events and successful scheduling of event groups that fit within the declared generic/fixed counter capacity. A useful static check is confirming exactly one row for each expected unit and nonnegative integer values in both counter fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/floating-point.json

## Purpose

This file defines 13 Skylake-X floating-point PMU events. It provides aliases for retired FP arithmetic instruction classes by vector width and precision, plus aggregate scalar/vector/floating-operation selectors and FP assist events.

The event names are `FP_ARITH_INST_RETIRED.128B_PACKED_DOUBLE`, `128B_PACKED_SINGLE`, `256B_PACKED_DOUBLE`, `256B_PACKED_SINGLE`, `512B_PACKED_DOUBLE`, `512B_PACKED_SINGLE`, `SCALAR_DOUBLE`, `SCALAR_SINGLE`, `SCALAR`, `VECTOR`, `4_FLOPS`, `8_FLOPS`, and `FP_ASSIST.ANY`. These are core inputs for FLOP-rate, vectorization, and assist-overhead metrics on Skylake-X.

## Important Schema Fields and APIs

Each object uses the core PMU event schema:

- `EventName`: public alias.
- `EventCode` and `UMask`: raw selector and subevent mask for FP arithmetic or assists.
- `Counter`: allowed programmable counters.
- `CounterMask`: present on aggregate FLOP-width style rows where thresholded behavior is needed.
- `SampleAfterValue`: default sampling period.
- `BriefDescription` and `PublicDescription`: short and detailed text shown by perf.

The file does not specify `Unit`, so events are core PMU events. `CounterMask` rows are lowered to `cmask=...` by `jevents.py`.

## Control Flow and Data Flow

Build-time control flow is standard PMU generation: parse JSON descriptors, emit generated C aliases, compile into perf, and expose aliases when the running CPU maps to Skylake-X. Runtime data flow is retired FP arithmetic/assist events from the core PMU into direct counts or into metrics that compute FLOPs, vector-width mix, FP utilization, and assist costs.

No event depends on another descriptor inside the file, but higher-level metrics may combine these events with instruction, cycle, slot, or frequency counters.

## State and Persistence

This is static metadata only. Runtime counts and samples exist in PMU registers and perf buffers. Generated aliases persist in perf build artifacts until the tool is rebuilt.

## Dependencies and Integration Points

The file integrates with `jevents.py`, generated `pmu-events.c`, `perf list`, `perf stat`, `perf record`, and Skylake-X metric definitions that include `Flops`, `HPC`, `Compute`, or topdown FP arithmetic groups. It depends on the Skylake-X core PMU encodings for AVX-512, AVX/packed, scalar, and assist events and on counter capacity defined in `counter.json`.

## Risks

FP event semantics can be misread as instruction counts, operation counts, or FLOP counts depending on the selector. The `4_FLOPS` and `8_FLOPS` aliases are especially sensitive to width/precision interpretation and `CounterMask` behavior. Workloads using mixed precision, masked AVX-512 operations, denormals, or assists may require careful interpretation. If metrics combine these aliases with frequency or instruction counts, counter multiplexing can skew derived GFLOP/s or utilization values.

## Test Signals

Build-time signals are JSON validity and generated aliases. Runtime tests should run scalar, AVX2, and AVX-512 microbenchmarks and verify the corresponding packed/scalar aliases increase as expected. `FP_ASSIST.ANY` should be tested with an assist-heavy workload if hardware and kernel permissions allow. Metric smoke tests should include Skylake-X FLOP and FP topdown metrics that depend on these aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/floating-point.json -->
