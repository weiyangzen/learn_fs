# subset-b-006699 Research

Grouped research for Intel x86 perf PMU event metadata under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86`. These source files are declarative JSON inputs for perf's PMU event generator, so the relevant control flow is the `jevents.py` parse, code-generation, and runtime lookup path rather than executable logic inside the JSON files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/metricgroups.json

## Purpose

`metricgroups.json` is the Lunar Lake metric-group description table for perf. Unlike the event files in the same directory, it is a JSON object, not an array: 148 metric-group names map to human-readable descriptions. Most legacy group names such as `Backend`, `Frontend`, `MemoryBound`, `Pipeline`, `TopdownL1` through `TopdownL6`, and `TmaL*` use descriptions from Intel's Top-down Microarchitecture Analysis spreadsheet, while newer `tma_*_group` entries describe the category that a top-down metric contributes to. Issue-oriented groups such as `tma_issueL1`, `tma_issueTLB`, and `tma_issueSyncxn` preserve the spreadsheet issue tokens used by Intel's generated metric set.

## Important APIs, Types, And Data Shape

The data contract is a flat string-to-string JSON object. The important "API" is the exact key spelling because metric definitions in sibling generated metric files refer to these names via their `MetricGroup` strings. `tools/perf/pmu-events/jevents.py` treats files ending in `metricgroups.json` specially: `preprocess_one_file()` loads the object, appends C-string terminators, stores names and descriptions in the generator's big string table, and records them in `_metricgroups`. `print_metricgroups()` then emits a sorted C array and the generated `describe_metricgroup(const char *group)` binary-search helper.

## Control Flow

At build time, the PMU event generator walks model directories under `pmu-events/arch/x86`. When it reaches this file, it does not call the normal event parser. Instead it loads the mapping, records every group name and description, and returns before event-table processing. Later, generated perf code can answer `perf list metricgroups` or print group descriptions by calling `describe_metricgroup()`.

## State And Persistence

The source file contains static metadata only. Persistent runtime state is limited to generated C tables baked into the perf binary. Ordering in the source object is not semantically important because `jevents.py` sorts the generated table, but key identity is persistent and case-sensitive.

## Dependencies And Integration Points

The file depends on the perf PMU event generation schema and on metric definitions elsewhere using matching group names. Integration points include `jevents.py`, generated `pmu-events.c`, `builtin-list.c` metricgroup listing, and `util/metricgroup.c` top-down handling. It complements event files such as Lunar Lake `pipeline.json` and metric expression generators such as `intel_metrics.py`.

## Risks

The main risk is name drift: if a metric references a group name not present here, perf can still collect events but group descriptions and listing UX degrade. A second risk is shape drift: this file must remain an object, while most neighboring files are arrays. Duplicate JSON keys would be collapsed by the parser before generation. Descriptions containing unexpected escapes or embedded terminators would affect the generated big C string table.

## Test Signals

Useful checks are `jq type` returning `object`, a stable key count of 148 for this snapshot, successful `jevents.py` generation, and `perf list --raw-dump metricgroups` including the expected Lunar Lake group names. Runtime smoke tests should verify that `describe_metricgroup()` finds representative old and new names such as `Backend`, `TopdownL1`, `tma_backend_bound_group`, and `tma_issueTLB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/other.json

## Purpose

`other.json` defines 21 Lunar Lake PMU events that do not fit the main cache, pipeline, or virtual-memory topic files. It covers hardware assists and page-fault assists on `cpu_core`, bus-lock behavior on `cpu_atom`, dynamic L2 prefetch throttling levels on `cpu_atom`, offcore response request filters for streaming writes, a core `XQ.FULL` occupancy/stall event, and atom-side prefetch-to-demand promotion events.

## Important APIs, Types, And Data Shape

The file is a JSON array of event objects. Core schema keys are `EventName`, `Unit`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. Some entries add `CounterMask`, `MSRIndex`, and `MSRValue`. `OCR.*` events use `MSRIndex` values `0x1a6,0x1a7` to program offcore response filters, while `XQ.FULL` uses `CounterMask: "1"`. The same logical name `OCR.STREAMING_WR.ANY_RESPONSE` appears twice, once for `cpu_atom` with event `0xB7` and once for `cpu_core` with events `0x2A,0x2B`; `Unit` is therefore part of the identity.

## Control Flow

During build generation, `jevents.py` reads the array with `read_json_events()`, creates `JsonEvent` instances, lowercases event names, maps `Unit` to the perf PMU name, converts event fields to config strings, and emits rows into the Lunar Lake event table. At runtime, perf resolves user names such as `assists.hardware`, `bus_lock.split_locks`, or `ocr.streaming_wr.any_response` against the PMU exposed by the running hybrid CPU.

## State And Persistence

No mutable state exists in the JSON. Persistent effects are generated event aliases and encoded MSR filter values compiled into perf. Runtime collection state is held by perf and the kernel PMU driver when counters are opened.

## Dependencies And Integration Points

This file depends on hybrid PMU naming (`cpu_core` and `cpu_atom`), Intel offcore response MSR programming, and the generic perf JSON event schema. It integrates with `jevents.py`, generated `pmu-events.c`, `perf list`, `perf stat`, and tests that compare generated `struct pmu_event` records. The topic is inferred from the filename as `other`.

## Risks

The highest-risk entries are the `OCR.*` filters because a bad `MSRValue` silently changes the memory transaction class being counted. Duplicate names across units must remain intentionally separated. Bus-lock and prefetch-throttler entries are atom-only; exposing them as core events would produce invalid aliases on P-cores. `PublicDescription` wording for assists is broad and includes several hardware mechanisms, so downstream metrics should avoid treating it as a single root cause.

## Test Signals

Validation should include `jq type` returning `array`, length 21, all entries having `EventName` and `Unit`, and successful generator output. Runtime signals include `perf list other` on Lunar Lake, `perf stat -e cpu_atom/bus_lock.split_locks/` on an atom-capable system, and offcore filter smoke tests that confirm `ocr.streaming_wr.any_response` is present for both hybrid units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/pipeline.json

## Purpose

`pipeline.json` is the main Lunar Lake pipeline event catalog. It contains 239 event records spanning divider activity, retired branches and mispredictions, fixed and programmable clock counters, dependency and execution stalls, retired instructions and uops, integer vector events, load blocking, loop-stream detector activity, machine clears, memory stalls, serialization, top-down slots, frontend/backend slot breakdowns, and uop issue, dispatch, execution, and retirement. It is central to `perf stat` top-down analysis and low-level pipeline diagnosis on Lunar Lake hybrid systems.

## Important APIs, Types, And Data Shape

The array uses the standard perf event JSON object schema with keys such as `EventName`, `Unit`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, `Deprecated`, `MSRIndex`, `MSRValue`, `EdgeDetect`, and `Invert`. The file intentionally duplicates many event names by `Unit`, for example `ARITH.DIV_ACTIVE`, `BR_INST_RETIRED.ALL_BRANCHES`, `CPU_CLK_UNHALTED.THREAD`, `INST_RETIRED.ANY`, and `TOPDOWN.*` variants differ between `cpu_core` and `cpu_atom`. Fixed counters are represented by `Counter` strings such as `Fixed counter 0` through `Fixed counter 6`; programmable events list available counters.

## Control Flow

`jevents.py` parses each object into `JsonEvent`, converts the topic from the filename to `pipeline`, lowers the event name for perf alias lookup, and emits generated event table entries. At runtime, perf resolves aliases per PMU unit. Top-down metric code and `perf stat --topdown` use events such as `TOPDOWN.SLOTS`, `TOPDOWN.BAD_SPEC_SLOTS`, `TOPDOWN_BE_BOUND.*`, `TOPDOWN_FE_BOUND.*`, `TOPDOWN_RETIRING.*`, and `UOPS_RETIRED.SLOTS` as building blocks for derived metrics.

## State And Persistence

The file is static build-time input. Persistent state is the generated event table and any downstream metric expressions that rely on these names. Runtime counter programming is transient. MSR-backed entries such as `INT_MISC.BPCLEAR_CYCLES`, `INT_MISC.UNKNOWN_BRANCH_CYCLES`, and `UOPS_RETIRED.MS` carry filter state through generated `MSRIndex` and `MSRValue` fields.

## Dependencies And Integration Points

Dependencies include Intel hybrid PMU units, fixed counter semantics, top-down slot architecture, and perf's JSON-to-C generator. Integration points are `tools/perf/pmu-events/jevents.py`, `pmu-events.h`, generated `pmu-events.c`, `util/metricgroup.c`, `builtin-stat.c`, `perf list`, `perf stat`, and PMU-event tests. It also coordinates with `metricgroups.json` because many pipeline events feed top-down metric groups.

## Risks

Hybrid duplication is the dominant maintenance risk: the same alias can have different event codes, masks, counters, or fixed-counter meanings on P-core and E-core PMUs. Deprecated atom events such as `ARITH.DIV_OCCUPANCY`, `ARITH.DIV_UOPS`, `LOAD_HIT_PREFETCH.HW_PF`, and `MACHINE_CLEARS.SLOW` should remain visible for compatibility but not be preferred in new metrics. Top-down fixed counters must line up with kernel support and CPU model capabilities. Counter masks and MSR filters are easy to mistype and can change a count from cycles to periods.

## Test Signals

Checks should include JSON validity, length 239, presence of both `cpu_core` and `cpu_atom` records, and generator success. Representative runtime checks are `perf list pipeline`, `perf stat -e cycles,instructions,topdown.slots`, and explicit hybrid aliases such as `cpu_core/uops_retired.slots/` and `cpu_atom/topdown_fe_bound.all/`. Tests should also verify deprecated entries remain marked, not removed silently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/uncore-interconnect.json

## Purpose

`uncore-interconnect.json` defines a single Lunar Lake uncore interconnect event: `UNC_CLOCK.SOCKET`. It represents a 48-bit fixed counter for UCLK cycles on the `SANTA` unit and is package-scoped via `PerPkg: "1"`. The event provides a clock reference for uncore/interconnect analysis and for normalizing package-level uncore activity.

## Important APIs, Types, And Data Shape

The file is a one-element JSON array. The event object uses `BriefDescription`, `Counter: "FIXED"`, `EventCode: "0xff"`, `EventName`, `PerPkg`, and `Unit: "SANTA"`. Unlike core PMU events, there is no `UMask`, no programmable counter list, and no sample-after value. The unit name must map through perf's uncore PMU matching rather than the hybrid `cpu_core` or `cpu_atom` paths.

## Control Flow

The generator treats the file as an ordinary event array, gives it the topic `uncore-interconnect`, and emits an event alias for the `SANTA` PMU. At runtime, perf can list and open the alias only if the kernel exposes a matching uncore PMU. Because the counter is fixed and per-package, aggregation semantics differ from per-thread core events.

## State And Persistence

The source is static. Generated perf tables persist the alias, fixed counter selector, package scope, and description. Runtime state is the uncore counter programmed by perf on a matching Lunar Lake system.

## Dependencies And Integration Points

This file depends on kernel support for the Lunar Lake `SANTA` uncore PMU name and fixed counter event `0xff`. It integrates with the same `jevents.py` event table generation as other JSON files, but runtime collection goes through uncore PMU discovery and package aggregation rather than per-CPU core scheduling.

## Risks

The main risk is PMU-name mismatch: if the kernel exposes a different uncore PMU name than `SANTA`, the generated alias will not bind. Fixed-counter semantics also mean generic event scheduling assumptions do not apply. Since there is only one event, missing or malformed data removes the whole interconnect topic for Lunar Lake.

## Test Signals

Validation should confirm JSON array length 1 and the exact `Unit`, `EventName`, `Counter`, and `PerPkg` fields. Runtime smoke tests on matching hardware should include `perf list uncore-interconnect` and `perf stat -e uncore_santa/unc_clock.socket/` or the kernel-specific PMU spelling exposed under `/sys/bus/event_source/devices`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/uncore-memory.json

## Purpose

`uncore-memory.json` defines five Lunar Lake integrated-memory-controller events for DRAM command and data movement analysis. `UNC_M_CAS_COUNT_RD` and `UNC_M_CAS_COUNT_WR` count read and write CAS commands, `UNC_M_DRAM_THERMAL_HOT` and `UNC_M_DRAM_THERMAL_WARM` count thermal state indications, and `UNC_M_TOTAL_DATA` counts read/write data transfers in 32-byte chunks per DDR channel. All entries use `Unit: "iMC"` and are package scoped.

## Important APIs, Types, And Data Shape

The file is a JSON array of five uncore event objects. Shared fields include `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, and `Unit`. The thermal events additionally carry `Experimental: "1"`, signaling that callers should treat them as less stable. Counters are programmable uncore counters `0,1,2,3,4`; event codes are `0x22`, `0x23`, `0x19`, `0x1A`, and `0x3C`.

## Control Flow

`jevents.py` parses the file as normal event metadata with topic `uncore-memory`. The generated alias table is available to perf list/stat, but runtime collection depends on matching uncore iMC devices exposed by the kernel. The data-transfer event can be scaled by tooling or humans using its 32-byte chunk description.

## State And Persistence

This is static declarative metadata. Generated perf tables persist event codes, package scope, and experimental markers. Runtime state is in uncore iMC counters; collection is package or memory-controller scoped rather than per task.

## Dependencies And Integration Points

Dependencies include Lunar Lake iMC PMU support, perf uncore PMU matching, and generated PMU event tables. Integration points include `perf list uncore-memory`, `perf stat` package aggregation, memory bandwidth metrics, and any dashboards that translate `UNC_M_TOTAL_DATA` counts into bytes.

## Risks

Thermal events are explicitly experimental and may change or be unavailable on some systems. `UNC_M_TOTAL_DATA` counts 32-byte chunks rather than bytes, so consumers can be off by a factor of 32 if they assume raw bytes. Per-package aggregation can surprise users expecting per-core or per-thread attribution. A unit spelling mismatch (`iMC`) would prevent alias matching.

## Test Signals

Useful checks are JSON validity, length 5, all entries `PerPkg: "1"`, and generator success. Runtime testing on Lunar Lake should confirm iMC PMUs under sysfs, `perf list uncore-memory`, read/write CAS counts under memory traffic, and expected scaling behavior for `UNC_M_TOTAL_DATA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/virtual-memory.json

## Purpose

`virtual-memory.json` defines 48 Lunar Lake events for TLB and page-walk behavior. It covers demand-load, store, and instruction-side TLB misses; STLB hits; page walks completed by page size; active and pending page walks; atom-specific load-head stalls; page-walker cache hits; and STLB flush attempts. The catalog is used to diagnose address-translation overhead and memory-side frontend/backend stalls.

## Important APIs, Types, And Data Shape

The file is a JSON array using `EventName`, `Unit`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. It contains both `cpu_atom` and `cpu_core` encodings for shared names such as `DTLB_LOAD_MISSES.STLB_HIT`, `DTLB_*_WALK_COMPLETED`, `DTLB_*_WALK_PENDING`, and `ITLB_MISSES.*`. Core walk-active events use `CounterMask: "1"` to count cycles with at least one page miss handler active.

## Control Flow

The perf generator assigns topic `virtual-memory`, converts each object into a generated event alias, and preserves unit-specific encodings. At runtime, users can collect aliases per PMU, while higher-level top-down metrics can combine these events with pipeline and cache stalls to explain memory-bound behavior.

## State And Persistence

The JSON is static. Generated aliases persist event codes and unit-specific masks. Runtime state is limited to configured PMU counters. There is no cross-run persistence in the source or generated table.

## Dependencies And Integration Points

Dependencies include Lunar Lake hybrid PMU encodings, page miss handler semantics, and perf JSON generation. Integration points include `perf list virtual-memory`, top-down memory/TLB metrics, `metricgroups.json` groups such as `MemoryTLB`, `tma_dtlb_load_group`, `tma_dtlb_store_group`, and `tma_itlb_misses_group`, plus tests that verify generated event aliases.

## Risks

The same event name can use different event codes and masks on atom and core PMUs, so unit-aware lookup is required. Some atom-only events such as `LD_HEAD.DTLB_MISS`, `PAGE_WALKER_LOADS.*`, and `TLB_FLUSHES.STLB_ANY` should not be assumed available on core PMUs. `WALK_PENDING` style events count outstanding walks per cycle, while `WALK_COMPLETED` counts completions; mixing them in ratios without unit care can produce misleading metrics.

## Test Signals

Validation should check array length 48, both units present, and expected groups of DTLB load, DTLB store, and ITLB events. Runtime tests include `perf list virtual-memory`, targeted collection of `dtlb_load_misses.walk_completed`, and hybrid-specific checks for atom-only aliases. Metric validation should compare TLB miss rates under workloads with known page-size or working-set changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/cache.json

## Purpose

`cache.json` is the Meteor Lake cache and memory-access event catalog for perf. It contains 162 events covering L1D replacements and pending misses, L2 line fills/evictions/requests, longest-latency-cache references and misses, instruction-fetch and demand-load memory-bound stalls, retired memory instructions, load data-source breakdowns, memory scheduler blocks, offcore requests and outstanding cycles, OCR snoop/data-source filters, software prefetches, bus locks, and an atom frontend icache top-down event.

## Important APIs, Types, And Data Shape

The array uses standard perf PMU event fields: `EventName`, `Unit`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, `MSRIndex`, `MSRValue`, `Data_LA`, and `EdgeDetect`. It has both `cpu_core` and `cpu_atom` events, often with the same alias name but different encodings. Core PEBS/load-address related retired memory events use `Data_LA: "1"`. OCR and some load-latency events program MSR filters such as `0x1a6,0x1a7` or `0x3F6`.

## Control Flow

`jevents.py` reads the file as topic `cache`, builds generated aliases, and emits unit-specific event records. At runtime, perf resolves names such as `l2_rqsts.references`, `mem_load_retired.l3_miss`, `ocr.demand_data_rd.l3_hit.snoop_hitm`, or `offcore_requests_outstanding.demand_data_rd` against the PMU unit. Higher-level memory metrics use these aliases to attribute stalls and bandwidth pressure.

## State And Persistence

The source is static metadata. Generated event tables persist encodings, descriptions, data-address capability annotations, and MSR filter values. Runtime state consists of PMU counter programming, PEBS configuration where required, and any offcore response MSR settings applied by perf during collection.

## Dependencies And Integration Points

Dependencies include Meteor Lake hybrid PMU event encodings, Intel offcore response filters, PEBS load-address support, and perf's generated PMU alias system. Integration points include `perf list cache`, `perf mem`, `perf stat` memory metrics, `util/pmu.c` alias matching, generated `pmu-events.c`, and tests that compare expected generated event fields. It also feeds metric groups such as cache hits/misses, memory bandwidth, memory latency, data sharing, snoop, and load/store bound groups.

## Risks

The file is dense and has several risk classes. Duplicate aliases must remain separated by `Unit`. OCR filters rely on exact `MSRValue` bitmasks; mistakes produce plausible but wrong data-source counts. PEBS/Data_LA events require hardware and kernel support, and should not be treated as generic counting events on unsupported systems. Some aliases are compatibility aliases, for example `L2_REQUEST.*` and `L2_RQSTS.*`, so removing one spelling can break users. Events that count cycles, requests, retired instructions, and latency-threshold samples should not be mixed without normalization.

## Test Signals

Validation should confirm array length 162, expected `cpu_atom` and `cpu_core` coverage, JSON generation success, and no accidental loss of MSR-backed OCR entries. Runtime checks include `perf list cache`, collecting L1/L2 aliases under cache-stressing workloads, PEBS availability checks for `mem_inst_retired.*`, and offcore-request smoke tests. Regression tests should compare generated event strings for representative aliases with `MSRIndex`, `MSRValue`, `CounterMask`, and `Data_LA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/floating-point.json

## Purpose

`floating-point.json` defines 32 Meteor Lake floating-point and vector arithmetic PMU events. It covers floating-point divider activity, FP assists, SSE/AVX transition assists, core FP arithmetic dispatch ports, retired FP arithmetic by scalar/vector width and precision, atom floating-point operation counts, atom FP instruction retired classes, vector-integer/FP store-data port execution, FP-assist machine clears, and retired FP divide uops.

## Important APIs, Types, And Data Shape

The file is an event array with `EventName`, `Unit`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Deprecated`. It includes both `cpu_core` and `cpu_atom` encodings for `ARITH.FPDIV_ACTIVE`. Core events focus on `FP_ARITH_DISPATCHED.*` and `FP_ARITH_INST_RETIRED.*`; atom events include `FP_FLOPS_RETIRED.*`, `FP_INST_RETIRED.*`, `MACHINE_CLEARS.FP_ASSIST`, and `UOPS_RETIRED.FPDIV`. Deprecated aliases preserve older names `FP_FLOPS_RETIRED.DP` and `FP_FLOPS_RETIRED.SP`, pointing users toward `FP64` and `FP32`.

## Control Flow

The generator assigns topic `floating-point`, lowercases aliases, and emits the event records into generated perf tables. At runtime, perf users collect these aliases per PMU unit. Derived FLOP or vectorization metrics use the retired arithmetic counts and must account for Intel's documented weighting, especially packed and fused operations that count multiple operations per instruction.

## State And Persistence

The JSON is static. Generated tables preserve alias spellings, deprecation flags, event encodings, and long descriptions. Runtime PMU state is transient and per collection. There is no source-level persistence.

## Dependencies And Integration Points

Dependencies include Meteor Lake hybrid PMU encodings, SIMD width/precision semantics, and perf's PMU alias generator. Integration points include `perf list floating-point`, HPC metric groups such as `Flops`, `FpScalar`, `FpVector`, `Compute`, and generated metrics from Intel metric scripts. FP assist events also integrate conceptually with pipeline machine-clear and assist analysis.

## Risks

FLOP interpretation is the main risk. Several descriptions state that each count represents multiple computational operations and that FMA or DPP instructions can count twice, so downstream metrics must not equate event counts directly to instructions. Deprecated aliases should remain marked to guide users without breaking compatibility. Hybrid differences matter: core dispatch-port aliases do not apply to atom PMUs, and atom FP FLOP aliases do not imply the same encoding on core PMUs.

## Test Signals

Validation should check array length 32, both units present, deprecated flags on `FP_FLOPS_RETIRED.DP` and `FP_FLOPS_RETIRED.SP`, and successful generated C output. Runtime tests include `perf list floating-point`, simple scalar and vector FP kernels to exercise width-specific retired events, and divide-heavy workloads to validate `ARITH.FPDIV_ACTIVE` and `UOPS_RETIRED.FPDIV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/floating-point.json -->
