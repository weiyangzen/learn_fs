# subset-b-006702

Grouped research report for Intel x86 perf PMU event catalogs under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake` and `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/pipeline.json

Purpose: defines the Meteor Lake core and atom pipeline performance events consumed by Linux perf's PMU event generation path. The file is a JSON array of 201 static event descriptors covering arithmetic/divide activity, assists, retired branch and misprediction events, unhalted clocks, cycle activity, execution port utilization, retired instructions, topdown slots and subcategories, LSD, uop decode/dispatch/issue/execute/retire, machine clears, resource stalls, and miscellaneous retire/serialization events.

Important APIs/types/functions: this file does not implement functions, but its schema is an API for `tools/perf/pmu-events/jevents.py`. Each object uses fields such as `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `BriefDescription`, optional `PublicDescription`, `CounterMask`, and `SampleAfterValue`. `Unit` is important on Meteor Lake because the same logical event name can have separate `cpu_core` and `cpu_atom` encodings, for example `ARITH.DIV_ACTIVE`, `BR_INST_RETIRED.*`, `BR_MISP_RETIRED.*`, and `CPU_CLK_UNHALTED.*`.

Control flow: at build time `jevents.py` reads this JSON, lowercases event names for generated lookup tables, maps `SampleAfterValue` to default periods, maps event code fields to perf event strings, and emits C tables included by perf. At runtime perf resolves a user event name for the detected Meteor Lake model, checks the target PMU unit, and programs the encoded event select, umask, counter mask, and counter constraints into the kernel PMU interface. There is no runtime control flow in this source file itself.

State and persistence: the source is immutable catalog data. Runtime state lives outside the file in hardware counters, perf evlist state, generated C tables, and perf data output. Entries with fixed-counter aliases such as `CPU_CLK_UNHALTED.THREAD` and `CPU_CLK_UNHALTED.REF_TSC` persist only as generated metadata; counter values are sampled or counted by perf sessions.

Dependencies and integration points: depends on the perf PMU JSON schema and the x86 Meteor Lake model mapping in the surrounding `pmu-events` tree. It integrates with `jevents.py`, `metric.py`, Intel metric-generation helpers, generated `pmu-events.c`, perf list output, and user commands such as `perf stat -e cpu_core/event/` or named aliases. `Counter` limits legal programmable counters or fixed counters, and `Unit` routes events to hybrid PMUs.

Risks: duplicate names across `cpu_core` and `cpu_atom` must stay deliberately distinguished by `Unit`; a bad encoding would silently misprogram hardware on one half of the hybrid CPU. Many branch cost events rely on PEBS retire latency semantics described in text but not explicitly modeled by a `PEBS` field here, so documentation drift matters. `CounterMask` values on cycle activity and stall events change event meaning and must not be normalized away. Deprecated aliases such as `BR_INST_RETIRED.IND_CALL` remain compatibility surface and should not be removed without checking perf alias behavior.

Test signals: run `jq` over the file to validate JSON array shape; run perf PMU event tests that invoke `jevents.py`; inspect `perf list` on Meteor Lake or generated tables for both `cpu_core` and `cpu_atom`; use targeted `perf stat` smoke tests for representative fixed, programmable, topdown, branch, and uop events. Diffing generated tables before and after edits is the strongest regression signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-cache.json

Purpose: defines two Meteor Lake uncore cache events for HAC CBO table-of-requests allocation accounting: `UNC_HAC_CBO_TOR_ALLOCATION.ALL` and `UNC_HAC_CBO_TOR_ALLOCATION.DRD`. These expose all TOR allocations and coherent data-read allocations into the HAC CBO queue.

Important APIs/types/functions: static perf PMU JSON descriptors with `EventName`, `EventCode` `0x35`, `UMask` values `0x8` and `0x1`, `Counter` `0,1`, `Unit` `HAC_CBO`, `PerPkg` `1`, and `BriefDescription`. The schema is interpreted by `jevents.py`; there are no local functions.

Control flow: build tooling converts the two JSON rows into generated perf aliases. At runtime perf resolves the uncore event name, targets the `HAC_CBO` PMU, applies the counter constraint, and counts package-level uncore queue allocation activity while the perf session is active.

State and persistence: no source-level mutable state. Hardware counter state exists in uncore PMU registers and is package scoped because `PerPkg` is set. Counts are transient unless perf records them into its output.

Dependencies and integration points: depends on Meteor Lake uncore PMU naming, the HAC CBO hardware unit, and perf's generated PMU event tables. These cache events integrate with adjacent uncore interconnect and memory files to explain off-core traffic pressure.

Risks: the file is tiny, so any field typo has a large blast radius for this category. `PerPkg` must remain present so tooling and users do not interpret counts as per-core. Event names encode CBO/HAC terminology that must match kernel PMU names. The `DRD` event excludes prefetches according to its description, so using it as total read demand requires care.

Test signals: JSON validation, generated-table diff, `perf list` visibility for `UNC_HAC_CBO_TOR_ALLOCATION.*`, and hardware smoke tests on Meteor Lake uncore PMUs. Compare `ALL` versus `DRD` under memory-read workloads to catch swapped umasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-interconnect.json

Purpose: defines seven Meteor Lake uncore interconnect and arbitration events. The catalog covers read data occupancy, coherent tracker allocation, outgoing coherent data-read requests, CMI transaction totals, CMI reads, CMI writes, and all outgoing HAC ARB tracker allocations.

Important APIs/types/functions: static event rows with `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and descriptions. Units are `ARB` for `UNC_ARB_DAT_OCCUPANCY.RD` and `HAC_ARB` for the remaining coherent tracker and transaction events. Event codes include `0x85`, `0x84`, `0x81`, and `0x8A`; counters are constrained to `0` or `0,1` depending on the PMU.

Control flow: perf's build generator reads the JSON and emits C aliases. A user selecting one of these names causes perf to address the relevant uncore arbitration PMU and program the encoded event. Occupancy events are cycle-weighted, while request and transaction events count allocations or CMI transfers.

State and persistence: static source data only. Runtime state is in uncore counters, package-level because `PerPkg` is set on all entries. The data is not persisted by this file; perf may persist samples or aggregate counts.

Dependencies and integration points: depends on Meteor Lake uncore PMU support and generated `pmu-events` tables. It integrates with uncore cache events for queue pressure and uncore memory events for downstream DRAM traffic, allowing read occupancy and transaction counts to be correlated.

Risks: event descriptions distinguish coherent versus non-coherent traffic and reads versus writes; alias misuse can produce misleading bandwidth or occupancy interpretations. The single-counter `ARB` occupancy event may fail scheduling if combined with other events requiring the same counter. Counter constraints and `Unit` values must match kernel-exposed PMU names.

Test signals: `jq` schema validation, generated table checks, `perf list` visibility, and `perf stat` runs under read-heavy and write-heavy workloads. A useful behavioral signal is that `UNC_HAC_ARB_TRANSACTIONS.READS` and `.WRITES` should move differently under synthetic traffic while `.ALL` remains a superset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-memory.json

Purpose: defines 18 Meteor Lake uncore memory-controller events. The file covers free-running memory-controller read CAS, write CAS, and total request counters for MC0 and MC1, plus programmable iMC events for ACT, CAS, PRE, thermal warm/hot, read data, write data, and total data transfers.

Important APIs/types/functions: each object is a perf PMU event descriptor. Free-running entries use `Unit` `imc_free_running_0` or `imc_free_running_1`, fixed event code `0xff`, package scope, and specific counter indices for read/write/total request counts. Programmable entries use `Unit` `iMC`, counters `0,1,2,3,4`, event codes such as `0x22` for read CAS, `0x23` for write CAS, `0x3A` for read data, and `0x3C` for total data. Several entries include `PublicDescription` clarifying 32B/64B CAS and request merge semantics.

Control flow: build-time `jevents.py` turns the descriptors into perf aliases. Runtime perf chooses the correct uncore PMU unit, programs the event or reads the free-running counter, and reports package-level memory-controller activity. Users typically combine these events in `perf stat` to estimate bandwidth, command mix, page behavior, and thermal throttling signals.

State and persistence: no mutable source state. Free-running counters may already be advancing outside a perf session, while programmable iMC counters count only while configured. The file itself persists only event metadata. Counts are package-level because all rows set `PerPkg`.

Dependencies and integration points: depends on Meteor Lake kernel PMU support for `iMC` and `imc_free_running_*` units and the perf PMU event generation pipeline. It integrates with uncore interconnect events for traffic source analysis and with core pipeline/memory-stall events for correlating bandwidth pressure with frontend/backend stalls.

Risks: request counts and DRAM command counts are not equivalent to bytes; descriptions warn that partial/full-line writes and merged writes can make request count higher than DRAM bandwidth. Data transfer events increment in 32B chunks, so downstream metrics must multiply correctly. Free-running MC0 and MC1 counter indices are explicit and easy to transpose. Thermal warm/hot events are rank-level state indicators, not byte traffic.

Test signals: JSON validation, generated alias inspection, `perf list` checks for both free-running and programmable iMC events, and memory bandwidth smoke tests using read, write, and mixed workloads. Compare `UNC_M_RD_DATA`, `UNC_M_WR_DATA`, and `UNC_M_TOTAL_DATA` for arithmetic consistency, and compare MC0/MC1 free-running counters on systems where both controllers are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-other.json

Purpose: defines the Meteor Lake package uncore clock event `UNC_CLOCK.SOCKET`, a 48-bit fixed counter for UCLK cycles.

Important APIs/types/functions: one static descriptor with `EventName` `UNC_CLOCK.SOCKET`, `EventCode` `0xff`, `Counter` `FIXED`, `Unit` `CNCU`, `PerPkg` `1`, and a brief description. The row is consumed by perf's PMU event generator; there are no functions.

Control flow: `jevents.py` emits the alias into generated tables. At runtime perf resolves the named event to the `CNCU` uncore PMU fixed counter and reads UCLK cycles for the socket/package during measurement.

State and persistence: no source-level state. The fixed counter is hardware state and package scoped. Perf may use it as an elapsed uncore-cycle denominator for ratios, but the JSON file only provides metadata.

Dependencies and integration points: depends on kernel support for the Meteor Lake `CNCU` PMU and fixed uncore counter access. Integrates with uncore cache, interconnect, and memory events as a normalization denominator for package-level activity.

Risks: because this is a fixed counter, treating it like a programmable event could cause scheduling or availability surprises. `PerPkg` and `Unit` are essential for correct scope. Counter width is described as 48-bit; long-running sessions must account for wraparound in lower layers.

Test signals: JSON validation, generated alias presence, `perf list` visibility, and a simple `perf stat -e UNC_CLOCK.SOCKET` run showing monotonically increasing uncore cycles. Long-duration tests can catch fixed-counter wrap or scaling issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/virtual-memory.json

Purpose: defines 37 Meteor Lake virtual-memory and TLB events for load DTLB misses, store DTLB misses, instruction TLB misses, and one atom-specific load-buffer retirement stall caused by a DTLB miss. The file covers STLB hits, page-walk active cycles, completed walks for all page sizes and specific 4K, 2M/4M, and 1G pages, and pending page-walk cycles.

Important APIs/types/functions: static event descriptors with `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `SampleAfterValue`, and `BriefDescription`. Like the pipeline file, it has hybrid `cpu_core` and `cpu_atom` rows with different event codes for similar semantic names, such as `DTLB_LOAD_MISSES.WALK_COMPLETED` on `0x12` for core and `0x08` for atom. Counter constraints differ between core (`0,1,2,3`) and atom (`0,1,2,3,4,5,6,7`).

Control flow: perf generation consumes the JSON and emits aliases for Meteor Lake. At runtime perf routes the selected event to the core or atom PMU, programs the DTLB/ITLB event code and umask, and counts page-walk activity or STLB hits while workloads run.

State and persistence: no local mutable state. Hardware PMU counters hold transient counts; perf records aggregate or sampled results. `SampleAfterValue` supplies default sampling periods for generated event metadata.

Dependencies and integration points: depends on x86 PMU support for Meteor Lake hybrid units and perf's JSON schema. Integrates with core pipeline stall events such as cycle activity and topdown backend-bound categories, and with kernel memory-management investigations where page size, TLB reach, and page-walk pressure matter.

Risks: semantically similar core and atom events have different encodings and sometimes different availability, so merging rows by name would be wrong. `WALK_ACTIVE`/`WALK_PENDING` are cycle-like occupancy measures, not completed walk counts. The atom `DTLB_STORE_MISSES.WALK_COMPLETED` description says 1G while the event name says all completions, which is a documentation-risk signal worth checking against Intel source material before metric use.

Test signals: validate JSON, inspect generated aliases for both PMU units, run `perf list` on Meteor Lake, and use workloads with large random memory footprints or instruction-cache pressure to move DTLB and ITLB walk counters. Huge-page versus 4K-page tests should change the page-size-specific completed-walk events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/cache.json

Purpose: defines 324 Nehalem EP core cache, memory-retirement, and offcore cache-response events for perf. It covers L1D and L1I activity, lock cycles, L1 writebacks, L2 requests/transactions/lines, longest-latency cache references, memory instruction retirement latency thresholds, retired load data sources, uncore-retired load sources, offcore request pressure, and a large matrix of `OFFCORE_RESPONSE` request/response combinations.

Important APIs/types/functions: static JSON event descriptors consumed by `jevents.py`. Common fields are `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`; many offcore rows also rely on the event generator's support for model-specific offcore encodings through `MSRIndex`/`MSRValue` when present in related memory files. Counter constraints vary from `0,1` for some L1 events to `0,1,2,3` for broader core PMU events, and several precise memory-retirement events constrain to counter `3`.

Control flow: at build time perf converts the JSON into generated C event tables. At runtime perf resolves names such as `L2_RQSTS.LD_MISS`, `MEM_LOAD_RETIRED.LLC_MISS`, or `OFFCORE_RESPONSE.DEMAND_DATA_RD.LOCAL_DRAM`, programs event select/umask and any model-specific offcore response filter, and reads counts or samples. The file itself is declarative and has no executable flow.

State and persistence: no mutable state in the file. Runtime state is in core PMU counters, PEBS sampling state for precise events, and offcore response MSR filters. Sample periods such as `2000000`, `200000`, `100000`, and smaller latency-threshold values become generated metadata but are not persisted by the source file.

Dependencies and integration points: depends on Nehalem EP PMU definitions, perf JSON schema, and `jevents.py`. Integrates with memory analysis metrics, perf list/stat/record, and sibling Nehalem EP files for floating point, frontend, memory, and miscellaneous stalls. Cache rows are often paired with `nehalemep/memory.json` offcore DRAM filters to distinguish cache misses from local/remote memory service.

Risks: the large `OFFCORE_RESPONSE` matrix is easy to edit inconsistently because many rows share event code `0xB7` and differ only by request/response filter semantics. Counter `3` constraints on latency and offcore events can create scheduling conflicts. Sample-after values vary by event frequency; using an overly large default on rare latency events can hide samples. MESI-state and demand/prefetch naming is precise, so broad aliases such as `.ANY` must be treated as masks rather than independent event families.

Test signals: full JSON validation, generated-table diffs, perf PMU unit tests, and `perf list` alias inspection. Hardware smoke tests should include L1/L2 cache-hit workloads, LLC-miss memory streams, locked operations for lock events, and PEBS sampling for `MEM_INST_RETIRED.*` / `MEM_LOAD_RETIRED.*` precise events. Scheduling tests should verify constrained counter combinations fail or multiplex predictably.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/counter.json

Purpose: declares Nehalem EP PMU counter inventory for the `core` unit: four fixed counters and four generic programmable counters.

Important APIs/types/functions: this is a one-row JSON metadata file with `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. It is consumed by perf PMU event tooling as platform capability metadata rather than as a countable event. There are no functions or event encodings.

Control flow: build tooling reads the metadata alongside event files and can use it to describe available counters in generated PMU tables or validation logic. Runtime perf scheduling ultimately depends on kernel PMU capabilities, but this file documents the expected Nehalem EP counter topology for the event catalog.

State and persistence: static platform metadata only. It does not create runtime state or persist measurements.

Dependencies and integration points: integrates with the rest of `arch/x86/nehalemep` event files and the perf PMU event generator. The declared generic/fixed counts provide context for counter constraints in cache, memory, frontend, floating-point, and other event files.

Risks: an incorrect counter count would mislead generated metadata and humans reasoning about event scheduling. The values are strings, matching surrounding schema conventions; tooling must parse or preserve them correctly. This file has no `EventName`, so consumers must tolerate metadata rows without event aliases.

Test signals: JSON validation and a generator run that confirms metadata-only rows do not require `EventName`. Cross-check with generated tables and Nehalem EP PMU scheduling behavior where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/floating-point.json

Purpose: defines 28 Nehalem EP floating-point, MMX, SSE, and SIMD integer events. It covers x87 FP assists, floating-point computational uops by ISA/type, MMX/FP transition events, and 64-bit and 128-bit SIMD integer pack, arithmetic, logical, multiply, shift, shuffle/move, and unpack operations.

Important APIs/types/functions: static descriptors use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PEBS` on the three `FP_ASSIST.*` precise events. `FP_COMP_OPS_EXE.*` rows share event code `0x10` with different umasks; `SIMD_INT_128.*` uses `0x12`, and `SIMD_INT_64.*` uses `0xFD`.

Control flow: `jevents.py` converts rows into generated perf aliases. Runtime perf programs the selected core event to count FP/SIMD execution, assists, or transition activity. PEBS-capable assist events can be used in sampling flows where supported by kernel and hardware.

State and persistence: static source data. Runtime state exists in programmable PMU counters and optional PEBS buffers. Default sample periods are encoded as metadata; the file itself persists no measurements.

Dependencies and integration points: depends on Nehalem EP core PMU encoding and perf JSON schema. Integrates with `perf stat` for instruction mix analysis and `perf record` for precise FP assist investigation. It complements pipeline and frontend events by exposing execution-unit class rather than generic uop flow.

Risks: old ISA terminology such as MMX, x87, and SSE must remain historically accurate for Nehalem EP; renaming for modern terminology would break aliases. PEBS is only marked on assists, so assuming precise attribution for all FP/SIMD events would be wrong. Shared event codes make umask edits high risk.

Test signals: JSON validation, generated alias inspection, and workload smoke tests using x87 assists, SSE floating point, MMX transitions, and SIMD integer kernels. PEBS tests should specifically target `FP_ASSIST.ALL`, `.INPUT`, and `.OUTPUT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/frontend.json

Purpose: defines three Nehalem EP frontend decode events: decoded macro-instructions, decoded macro-fused instructions, and decoded two-uop instructions.

Important APIs/types/functions: static descriptors with `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Events are `MACRO_INSTS.DECODED` (`0xD0/0x1`), `MACRO_INSTS.FUSIONS_DECODED` (`0xA6/0x1`), and `TWO_UOP_INSTS_DECODED` (`0x19/0x1`), all available on counters `0,1,2,3`.

Control flow: perf generation converts the JSON rows to aliases. Runtime perf programs the selected event to count decode-path behavior during a workload, allowing users to compare instruction decode volume with retired instruction and uop activity.

State and persistence: no source-level state. Counts live in core PMU counters during perf measurement and may be stored in perf output.

Dependencies and integration points: depends on Nehalem EP PMU event encoding and perf PMU event generation. Integrates with pipeline, cache, and floating-point events when diagnosing frontend pressure or macro-fusion effectiveness.

Risks: the event family is small but semantically specific; macro-fusion counts are not the same as total fused-domain uops. If descriptions are used in generated help text, stale wording can mislead users about decode pipeline behavior. Counter availability is broad, but concurrent use with other events still competes for four generic counters.

Test signals: JSON validation, generated alias presence, `perf list` checks, and microbenchmarks with branch/compare patterns that should alter macro-fusion counts. Compare decoded instruction counts with retired instruction counts for sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/memory.json

Purpose: defines 67 Nehalem EP offcore memory response events focused on DRAM and LLC-miss outcomes. The rows form a matrix across request classes such as any data, instruction fetch, RFO, writeback, demand data, demand instruction fetch, demand RFO, prefetch data, prefetch instruction fetch, prefetch RFO, other, and aggregate request groups, crossed with response locations such as any DRAM, any LLC miss, local DRAM, and remote DRAM.

Important APIs/types/functions: every row uses `EventName`, `EventCode` `0xB7`, `UMask` `0x1`, constrained `Counter` `2`, `MSRIndex` `0x1A6`, an `MSRValue` filter, `SampleAfterValue`, and `BriefDescription`. The `MSRIndex`/`MSRValue` pair is the key schema surface: perf must program the offcore response filter MSR as well as the architectural event selector.

Control flow: at build time `jevents.py` recognizes `MSRIndex`, looks it up through its MSR mapping, and emits event strings that include the offcore filter. At runtime perf schedules the event on counter 2, writes the offcore response MSR filter, and counts requests matching both request type and response location.

State and persistence: no mutable source state. Runtime state includes a programmable counter plus the model-specific offcore response MSR, which is shared hardware configuration and must be managed carefully by perf scheduling. Measurements persist only through perf output.

Dependencies and integration points: depends on Nehalem EP offcore response MSR semantics, kernel support for programming offcore filters, and perf event generation. Integrates tightly with `cache.json`, where broader cache/offcore aliases and retired memory events provide complementary views of cache misses and data sources.

Risks: all rows share the same event code, umask, MSR index, and counter, so the `MSRValue` is the only differentiator for many aliases; copy/paste errors are hard to spot. Counter 2 exclusivity can create scheduling conflicts. Local versus remote DRAM semantics matter on multi-socket systems; on unsuitable hardware, counts may be zero or misleading. Some aggregate filters such as `ANY_LLC_MISS` include broad response masks rather than just DRAM.

Test signals: validate JSON, inspect generated event strings for `offcore_rsp`/MSR filters, verify `perf list` aliases, and run local versus remote NUMA memory workloads on Nehalem EP-class systems. Scheduling tests should combine two offcore response events to ensure perf handles the shared MSR and counter constraint correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/other.json

Purpose: defines 13 miscellaneous Nehalem EP core events for segment rename behavior, I/O transactions, load dispatch paths, partial address aliasing, store-buffer drain stalls, snoop responses, super-queue full stalls, and related execution/memory ordering effects.

Important APIs/types/functions: static descriptors with `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Event families include `LOAD_DISPATCH.*` on event code `0x13`, `SNOOP_RESPONSE.*` on `0xB8`, and single-purpose rows such as `PARTIAL_ADDRESS_ALIAS`, `SB_DRAIN.ANY`, and `SQ_FULL_STALL_CYCLES`.

Control flow: build-time generation emits aliases from the JSON. Runtime perf programs selected core PMU events to count dispatch source, snoop response, aliasing, or stall-cycle behavior for active workloads.

State and persistence: no source-level state. Counts are transient PMU hardware state and may be written to perf output. Default sampling periods become generated metadata.

Dependencies and integration points: depends on Nehalem EP PMU encoding and perf JSON event support. Integrates with cache and memory files for diagnosing memory ordering, snoop, and queue pressure issues; `LOAD_DISPATCH.*` can be compared with retired load and cache miss events.

Risks: several events are low-level microarchitectural signals with names that are easy to overinterpret. `LOAD_DISPATCH.RS_DELAYED` uses a terse description, "stage 305", that may need vendor-document cross-checking. Snoop response events require coherent traffic to be meaningful. Store-buffer and super-queue stalls may be workload and topology sensitive.

Test signals: JSON validation, generated alias checks, and targeted microbenchmarks for partial address aliasing, store-buffer pressure, coherent sharing/snoop traffic, and I/O transaction paths. Compare `LOAD_DISPATCH.ANY` against its MOB/RS components to catch umask errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/other.json -->
