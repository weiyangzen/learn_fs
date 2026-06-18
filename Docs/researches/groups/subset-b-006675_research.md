# Research: subset-b-006675

Grouped source research for five Intel Ice Lake perf PMU event data files. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/virtual-memory.json

Purpose: Defines 22 core PMU event aliases for Ice Lake client virtual-memory behavior. The table covers DTLB load misses, DTLB store misses, ITLB misses, and TLB flush attempts so `perf list`, `perf stat`, and `perf record` can expose named translation events instead of raw event-select/umask encodings.

Important schema fields and events: Every entry uses `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`; the active-cycle variants also use `CounterMask`. `DTLB_LOAD_MISSES.*` uses event `0x08`, `DTLB_STORE_MISSES.*` uses `0x49`, `ITLB_MISSES.*` uses `0x85`, and `TLB_FLUSH.*` uses `0xBD`. The walk-completed events split all page sizes (`UMask 0xe`) into 4K (`0x2`), 2M/4M (`0x4`), and for data loads/stores 1G (`0x8`) variants. `WALK_ACTIVE` and `WALK_PENDING` deliberately share `UMask 0x10`, with `WALK_ACTIVE` adding `CounterMask: 1` to count cycles with at least one page miss handler busy.

Control flow: The file itself has no executable flow. During perf build, `tools/perf/pmu-events/jevents.py` parses the JSON array, lowercases event names for generated tables, converts each event code and umask into perf event strings, and emits them into generated `pmu-events.c`. At runtime, perf maps the CPU model through the x86 PMU mapfile, selects the Ice Lake table, and resolves user-facing names such as `dtlb_load_misses.walk_completed_4k` into raw core event encodings.

State and persistence behavior: This is static source data checked into the tree. It persists only as generated C tables in the perf binary after build and owns no runtime state. The `Counter` field restricts the events to programmable core counters `0,1,2,3`; `SampleAfterValue` controls default sampling periods and can affect profiling interrupt rates.

Dependencies and integration points: Depends on the perf PMU event JSON schema and on `jevents.py` support for `CounterMask`. It integrates with `tools/perf/pmu-events/arch/x86/mapfile.csv`, generated `pmu-events.c`, `util/pmu.c`, `perf list`, and raw event parsing in perf. Semantically it complements Ice Lake frontend events that report instruction-side TLB misses and cache events that mark retired STLB-miss loads/stores.

Risks: `WALK_ACTIVE` versus `WALK_PENDING` is easy to misread because both use the same event and umask while only one has `CounterMask`. Any wrong umask silently reports the wrong page-size class. The file is under `icelake` rather than `icelakex`, so applying it to server models would depend on mapfile/model selection rather than filename similarity. The ITLB group lacks a 1G-specific completed-walk alias present for data-side events.

Test signals: Validate with `jq` that the file is a JSON array of 22 objects and that all entries have `EventName`, `EventCode`, and `UMask`. Build perf with jevents enabled and confirm `perf list` shows the named DTLB/ITLB/TLB flush events on an Ice Lake client target or generated table. Functional smoke tests should compare `WALK_ACTIVE` with `WALK_PENDING` on a TLB-stressing workload and verify flush events move during `mprotect`, `munmap`, or context-switch-heavy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/cache.json

Purpose: Defines 128 Ice Lake Xeon core PMU event aliases for cache, memory hierarchy, snoop, offcore response, memory-retired, outstanding request, store queue, and software prefetch analysis. It is the main human-readable event catalog for diagnosing cache locality, NUMA/PMM placement, L2 behavior, L3 hit/miss source, and offcore response classes on `icelakex`.

Important schema fields and event families: The table uses standard fields (`EventName`, `EventCode`, `UMask`, `Counter`, descriptions, `SampleAfterValue`) plus specialized fields: `CounterMask` and `EdgeDetect` for phase/cycle variants, `MSRIndex`/`MSRValue` for offcore response filters, `Data_LA` for precise address-capable retired memory events, and `Deprecated` on two `MEM_LOAD_L3_HIT_RETIRED.XSNP_*` aliases. Major families include `CORE_SNOOP_RESPONSE` (7 snoop response state aliases), `L1D` and `L1D_PEND_MISS` (replacement and outstanding/fill-buffer pressure), `L2_RQSTS`, `L2_LINES_*`, `L2_TRANS`, `LONGEST_LAT_CACHE`, retired memory instruction/load families, 50 `OCR.*` offcore response filters, `OFFCORE_REQUESTS*`, `SQ_MISC`, and `SW_PREFETCH_ACCESS`.

Control flow: The file is parsed by `tools/perf/pmu-events/jevents.py` during perf build. Normal core events are converted into event strings from the first `EventCode` and `UMask`; `MSRIndex` values `0x1a6,0x1a7` are converted by `lookup_msr()` into `offcore_rsp=` filters, so `OCR.*` entries become selectable named aliases for the offcore response MSRs. At runtime, perf selects this `icelakex` table for matching CPU models, exposes names through `perf list`, and programs core counters plus offcore filter MSRs when users request OCR events.

State and persistence behavior: The JSON has no mutable state. Its persistent effect is the generated PMU event table compiled into perf. `Counter` limits most events to generic core counters `0,1,2,3`; retired memory and frontend-adjacent PEBS-style events still encode their counter constraints in JSON. `Data_LA: 1` annotates retired memory events as supporting sampled data linear addresses when precise sampling is used. Offcore entries rely on writing the right filter value into MSR `0x1a6` or `0x1a7`.

Dependencies and integration points: Depends on perf's PMU JSON schema and `jevents.py` mappings for `MSRIndex`, `Data_LA`, `CounterMask`, `EdgeDetect`, and `Deprecated`. It integrates with x86 model mapping, generated `pmu-events.c`, event parser support for `offcore_rsp`, `perf mem`/PEBS address workflows, and metric or topdown analysis that composes cache events. It is adjacent to `counter.json`, which declares core and uncore counter capacities, and to `frontend.json`, which covers instruction-side delivery stalls.

Risks: Offcore filter values are high-risk because a single wrong bit in `MSRValue` changes request type, snoop class, locality, PMM/DRAM, or SNC classification while the event still appears valid. `EventCode` values such as `0xB7, 0xBB` depend on `jevents.py` taking the first code while still allowing either offcore response register path through the MSR list. Deprecated XSNP aliases share encodings with replacement names and can confuse users or tests that expect unique semantic names. `Data_LA` promises address support only when the event is used in a precise-capable mode; non-precise sampling should not be interpreted as address-qualified. Counter pressure is significant because most aliases share only four counters and OCR filters consume scarce offcore MSR resources.

Test signals: Validate JSON schema and count 128 entries. Build perf and inspect generated event strings for representative normal, `Data_LA`, deprecated, and OCR entries. Run `perf list cache` on an Ice Lake Xeon model and confirm visibility. Use synthetic pointer-chasing, streaming load/store, prefetch, and NUMA/PMM placement workloads to check movement in `L1D_PEND_MISS`, `L2_RQSTS`, `MEM_LOAD_RETIRED`, and `OCR.READS_TO_CORE.*`. Include event-group tests with multiple OCR aliases to verify MSR/counter scheduling failures are understandable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/counter.json

Purpose: Declares counter inventory for Ice Lake Xeon PMU units. Unlike the event-definition files, this table describes how many fixed and generic counters exist for the core PMU and each uncore PMU unit so perf can expose capacity metadata for scheduling and discovery.

Important schema fields and entries: Each object uses `Unit`, `CountersNumFixed`, and `CountersNumGeneric`; it intentionally has no `EventName`. The file lists 11 units: `core` with 4 fixed and 8 generic counters, `CHA`, `IIO`, `M2M`, `UPI`, `M2PCIe`, `M3UPI`, and `PCU` with 4 generic counters, `IRP` and `UBOX` with 2 generic counters, and `iMC` with 1 fixed plus 4 generic counters. `UBOX` stores `CountersNumFixed` as numeric `1` while most other counts are strings, so consumers must tolerate both JSON number and string forms.

Control flow: During PMU event generation, this file is read as metadata rather than as an event alias list. `jevents.py` and the generated PMU tables use `Unit` naming rules to associate metadata with PMU names: `core` maps to the default core PMU, while unknown units map by convention to uncore PMU names such as `uncore_cha`, `uncore_iio`, or `uncore_pcu`. Runtime perf can then present and reason about unit counter capacities alongside model-specific event tables.

State and persistence behavior: The file is static metadata. It has no runtime state, but its values persist into generated perf tables and affect user expectations about groupability and available counters. Incorrect capacities can make valid groups look impossible or make impossible groups appear schedulable until kernel PMU constraints reject them.

Dependencies and integration points: Depends on the PMU event metadata schema and on `jevents.py` unit-to-PMU naming. It integrates with all `icelakex` event categories because event tables reference the same PMU units, and with perf list/introspection paths that expose counter counts.

Risks: Mixed numeric/string count representation is a schema consistency risk for strict validators. Unit spelling is ABI-like: changing `iMC`, `M2PCIe`, or `M3UPI` casing can alter generated uncore PMU names. The file does not specify per-event constraints, so it is capacity metadata only and must not be used as a complete scheduler model.

Test signals: Validate the JSON array has 11 objects and no accidental `EventName` keys. Build perf with jevents enabled and confirm counter metadata is accepted despite mixed number/string values. Cross-check against Ice Lake Xeon PMU documentation or kernel uncore PMU registration names, especially for `iMC`, `UBOX`, `M2PCIe`, and `M3UPI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/floating-point.json

Purpose: Defines 13 Ice Lake Xeon core PMU aliases for floating-point assists and retired scalar/vector floating-point arithmetic. The file supports workload analysis for SSE, AVX, and AVX-512 instruction mix and for detecting microcode FP assist overhead.

Important schema fields and events: All entries use `EventName`, `EventCode`, `UMask`, `Counter`, descriptions, and `SampleAfterValue`. `ASSISTS.FP` uses event `0xc1` and umask `0x2`. The remaining 12 aliases use `FP_ARITH_INST_RETIRED` event `0xc7` with umasks that separate scalar single/double (`0x2`/`0x1`), scalar aggregate (`0x3`), 128-bit packed single/double (`0x8`/`0x4`), 256-bit packed single/double (`0x20`/`0x10`), 512-bit packed single/double (`0x80`/`0x40`), aggregate 4-FLOP and 8-FLOP classes (`0x18`, `0x60`), and all vector forms (`0xfc`). Entries are available on generic counters `0,1,2,3,4,5,6,7`.

Control flow: `jevents.py` parses the JSON at build time and emits named aliases into generated `pmu-events.c`. Runtime perf selects the `icelakex` table, then programs raw event `0xc7` or `0xc1` with the requested umask when users request aliases such as `fp_arith_inst_retired.512b_packed_single` or `assists.fp`.

State and persistence behavior: The file is immutable event metadata. Its generated form persists in the perf binary. There is no mutable state, but the descriptions encode important interpretation state: many counts represent instructions retired rather than true FLOP totals, fused multiply-add and dot-product instructions can count twice, and the public descriptions state that DAZ and FTZ MXCSR flags need to be set when using the arithmetic events.

Dependencies and integration points: Depends on perf PMU JSON schema and generated event tables. It integrates with perf stat/record, HPC analysis workflows, and any metrics that derive floating-point intensity from retired instruction classes. It also interacts with workload/compiler behavior because AVX width, FMA use, and denormal handling materially change counts.

Risks: Users may misinterpret instruction counts as operation counts without applying lane width and FMA semantics. Aggregate masks overlap narrower aliases, so summing aliases can double-count. The DAZ/FTZ note is operationally important; denormal behavior or FP exceptions can change assist counts and arithmetic-event reliability. AVX-512 availability and frequency behavior are outside this file, so event presence does not prove a workload actually executed at a given vector width.

Test signals: Validate 13 JSON entries. Build perf and confirm all `ASSISTS.FP` and `FP_ARITH_INST_RETIRED.*` aliases appear. Run scalar, SSE/AVX2, AVX-512, FMA, and denormal-heavy microbenchmarks to check that only the expected width/precision aliases move and that `ASSISTS.FP` increases on assist-prone inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/frontend.json

Purpose: Defines 38 Ice Lake Xeon frontend PMU aliases for branch resteers, length-changing-prefix decode stalls, DSB-to-MITE switches, retired frontend-stall attribution, instruction-cache lookup/stall events, IDQ delivery paths, microcode sequencer delivery, and uops-not-delivered topdown signals.

Important schema fields and events: The file uses standard event fields plus `CounterMask`, `EdgeDetect`, `Invert`, and `MSRIndex`/`MSRValue`. `BACLEARS.ANY`, `DECODE.LCP`, and `DSB2MITE_SWITCHES.*` cover branch/decode redirection and uop-cache-to-legacy decode transitions. `FRONTEND_RETIRED.*` contains 17 entries using event `0xc6`, umask `0x1`, MSR `0x3F7`, and distinct frontend filter values for DSB miss, ITLB/L1I/L2/STLB miss, and latency thresholds from 1 to 512 cycles. `ICACHE_*` entries cover L1I tag/data hit, miss, and stall aliases. `IDQ.*` distinguishes DSB, MITE, and microcode sequencer uop delivery; `IDQ_UOPS_NOT_DELIVERED.*` includes the inverted `CYCLES_FE_WAS_OK` variant.

Control flow: At build time, `jevents.py` maps `MSRIndex 0x3F7` to the `frontend=` event filter and emits each JSON object into `pmu-events.c`. At runtime, perf resolves the selected `icelakex` frontend aliases, programs the event select/umask and any frontend MSR filter, and applies counter masks, edge detection, or inversion for the cycle/transition variants.

State and persistence behavior: This is static event metadata. Runtime state exists only in programmed PMU counters and frontend filter MSR settings while perf sessions run. Counter masks turn raw event occurrences into cycle predicates, edge detection turns sustained conditions into transition counts, and inversion changes `IDQ_UOPS_NOT_DELIVERED.CYCLES_FE_WAS_OK` into an "enough uops delivered" condition rather than a missing-uops count.

Dependencies and integration points: Depends on the perf JSON schema and `jevents.py` support for frontend MSR lookup, counter masks, edge detection, and inversion. It integrates with topdown analysis, `perf stat` frontend-bound metrics, instruction-cache profiling, and virtual-memory research through ITLB/STLB frontend-retired aliases.

Risks: The `FRONTEND_RETIRED.*` events are filter-MSR based; wrong `MSRValue` values would silently attribute stalls to the wrong frontend cause or latency threshold. Several aliases intentionally share encodings (`ICACHE_16B.IFDATA_STALL` with `ICACHE_DATA.STALLS`, and `ICACHE_64B.IFTAG_STALL` with `ICACHE_TAG.STALLS`), so duplicate-looking events are expected. Counter-mask semantics must be preserved for "cycles any", "cycles ok", and "switch count" variants. The uppercase `EventCode` `0x9C` on one entry should be accepted by parsers but is worth keeping in schema tests.

Test signals: Validate 38 JSON entries and verify every `FRONTEND_RETIRED.*` entry has `MSRIndex 0x3F7`. Build perf and inspect generated `frontend=` filters. Use workloads with large code footprints, branch predictor churn, length-changing prefixes, DSB pressure, and microcoded instructions to check movement in the corresponding families. Include parser tests for aliases, `EdgeDetect`, `Invert`, and uppercase hex event codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/frontend.json -->
