<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/other.json

## Purpose
A64FX core PMU topic table for miscellaneous implementation-defined events that do not fit cleanly into the dedicated cache, pipeline, or SVE files. It supplies perf aliases for commit-width accounting, load completion waits, ROB empty cycles, WFE/WFI cycles, core energy, and L1/L2 hardware prefetch request classes.

## APIs, Types, and Functions
This is declarative data consumed by perf `jevents.py`, not executable code. Each record uses `EventName`, `EventCode`, `BriefDescription`, and `PublicDescription`; important aliases include `UOP_SPLIT`, `LD_COMP_WAIT*`, `EU_COMP_WAIT`, `FL_COMP_WAIT`, `BR_COMP_WAIT`, `_0INST_COMMIT` through `_4INST_COMMIT`, `EA_CORE`, `L1HWPF_*`, and `L2HWPF_*`.

## Control Flow, State, and Persistence
At build time, `jevents.py` walks the A64FX directory selected by `arch/arm64/mapfile.csv`, validates these JSON objects, and emits static PMU event tables into generated perf C sources. At runtime, perf matches CPUID `0x00000000460f0010` to `fujitsu/a64fx` and exposes these aliases through the core PMU. The file has no mutable state; persistence is the checked-in JSON plus generated build artifacts.

## Dependencies and Integration
Depends on the perf PMU event schema and the A64FX mapfile row. It integrates with `perf list`, `perf stat -e <event>`, and higher-level A64FX analysis that combines commit, wait, prefetch, and energy counters with cache and SVE topic files.

## Risks and Test Signals
Risks are stale event encodings, counter descriptions that distinguish L1 miss from L2/memory wait imprecisely, and derived analysis double-counting overlapping wait categories. Test signals are successful `jq`/JSON parsing, `jevents.py` generation, `perf list` visibility on A64FX, and hardware validation that selected aliases count under memory stalls, WFE/WFI idle loops, prefetch-heavy kernels, and commit-width microbenchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/pipeline.json

## Purpose
A64FX pipeline PMU topic table. It exposes frontend/backend stall aliases, execution pipeline valid-cycle counters, predicate population counters, L1/L1I/L2 pipeline valid and completion counters, tagged-address request counters, and gather/scatter flow counters for vector memory operations.

## APIs, Types, and Functions
The file is a JSON array of perf event records. Two entries use `ArchStdEvent` (`STALL_FRONTEND`, `STALL_BACKEND`) resolved from ARM64 architecture-standard tables; the rest define A64FX-specific `EventName`/`EventCode` values such as `EAGA_VAL`, `EXA_VAL`, `FLA_VAL`, `L1_PIPE0_COMP`, `L1_PIPE_COMP_GATHER_2FLOW`, and `L2_PIPE_COMP_ALL`.

## Control Flow, State, and Persistence
The table is parsed at perf build time into generated event descriptors. Runtime selection is by the A64FX CPUID mapfile entry, after which the aliases become static PMU event names. There is no runtime state in the JSON; all behavior comes from perf alias lookup and the hardware counters.

## Dependencies and Integration
Depends on standard ARM64 event resolution for the stall entries and A64FX hardware support for event codes in the 0x1A0, 0x240, 0x260, 0x2B0, and 0x330 ranges. It integrates with SVE and cache files when analyzing vector memory pipeline utilization and gather/scatter expansion.

## Risks and Test Signals
Risks include invalid `ArchStdEvent` references, architecture-standard events changing names, and misinterpreting predicate count semantics where full predicates are corrected to 16. Test signals are `jevents.py` resolution success, no duplicate alias conflicts, `perf stat` runs that show pipeline valid counts rising under scalar, SVE, gather, scatter, and L2 traffic workloads, and ratios that remain plausible against total cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/sve.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/sve.json

## Purpose
A64FX SVE topic table made entirely from ARM64 architecture-standard event aliases. It provides perf names for SVE instruction retirement/speculation, MOVPRFX, predicate activity, SVE loads/stores/prefetches, gather/scatter, first-fault loads, and scalable versus fixed floating-point operation counts.

## APIs, Types, and Functions
Each entry contains `ArchStdEvent` only, so `jevents.py` dereferences names from `arch/arm64/common-and-microarch.json`. Key aliases include `SIMD_INST_RETIRED`, `SVE_INST_RETIRED`, `UOP_SPEC`, `SVE_MATH_SPEC`, `SVE_PRED_SPEC`, `SVE_MOVPRFX_SPEC`, `SVE_LD_GATHER_SPEC`, `SVE_ST_SCATTER_SPEC`, and `FP_*_SCALE_OPS_SPEC`/`FP_*_FIXED_OPS_SPEC`.

## Control Flow, State, and Persistence
Build-time flow is alias resolution from the architecture-standard table into the A64FX generated event table. Runtime state is limited to the selected PMU and active event counters; the JSON itself persists only event membership for the A64FX model.

## Dependencies and Integration
Depends strongly on the ARM64 standard event catalog and on the A64FX mapfile row. It integrates with pipeline predicate counters and A64FX floating-point counters to support vectorization and SVE utilization analysis.

## Risks and Test Signals
Risks are unresolved standard aliases, semantic mismatch between standard event text and A64FX implementation behavior, and analysis mistakes when scalable-operation counters increment by vector-length-normalized units. Test signals are successful alias generation, `perf list` exposing all SVE names, and hardware runs with SVE vector loops, MOVPRFX-heavy sequences, gather/scatter kernels, and scalar baselines showing expected counter separation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/sve.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/core-imp-def.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/core-imp-def.json

## Purpose
Small Monaka implementation-defined override topic for a single instruction-cache prefetch event. It adds a local description for `L1I_CACHE_PRF`, counting L1I cache activity caused by hardware or software prefetch.

## APIs, Types, and Functions
The only record uses `ArchStdEvent: L1I_CACHE_PRF` plus `BriefDescription`. There are no functions or local event codes; the schema relies on standard ARM64 event metadata and local descriptive text.

## Control Flow, State, and Persistence
`jevents.py` resolves `L1I_CACHE_PRF` from the ARM64 standard table while preserving the Monaka-specific description. Runtime perf alias exposure follows the Monaka CPUID mapfile entry. The file contains no mutable state.

## Dependencies and Integration
Depends on `common-and-microarch.json` containing `L1I_CACHE_PRF` and on `arch/arm64/mapfile.csv` mapping CPUID `0x00000000460f0030` to `fujitsu/monaka`. It complements `l1i_cache.json`, which covers demand, refill, hit, and prefetch instruction-cache counters.

## Risks and Test Signals
The main risk is a dangling `ArchStdEvent` if the standard event catalog changes. Test signals are successful JSON parsing, generated alias presence, and instruction-prefetch workloads increasing `L1I_CACHE_PRF` consistently with broader L1I cache counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/core-imp-def.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/cycle_accounting.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/cycle_accounting.json

## Purpose
Monaka cycle-accounting event table for commit bandwidth, no-commit reasons, load completion waits, ROB empty cycles, WFE/WFI, retention, and MOVPRFX-only commit cycles. It is intended to explain where cycles are spent when instructions do not retire or retire at limited width.

## APIs, Types, and Functions
The records are direct Monaka event definitions with `EventName`, `EventCode`, and `BriefDescription`. Important aliases include `LD_COMP_WAIT`, `LD_COMP_WAIT_L1_MISS`, `LD_COMP_WAIT_L2_MISS`, `EU_COMP_WAIT`, `FL_COMP_WAIT`, `BR_COMP_WAIT`, `ROB_EMPTY`, `_0INST_COMMIT` through `_5INST_COMMIT`, `UOP_ONLY_COMMIT`, and `RETENTION_CYCLE`.

## Control Flow, State, and Persistence
The JSON is read during perf event-table generation and persisted as static aliases in the generated binary. At runtime, perf binds these events to the Monaka core PMU through the mapfile CPUID. No state is stored by the file itself; active counter state is owned by the kernel PMU and perf sessions.

## Dependencies and Integration
Depends on Monaka hardware event-code definitions and the perf PMU JSON schema. It integrates with `gcycle.json` for frequency/retention interpretation, `stall.json` for topdown stall classes, and cache/TLB files for diagnosing the root cause of load completion waits.

## Risks and Test Signals
Risks include overlapping no-commit categories, event-code drift from vendor documentation, and ratios exceeding intuitive totals if users sum non-exclusive counters. Test signals are build-time generation success, `perf stat` availability, idle/retention tests increasing `RETENTION_CYCLE`, memory-latency tests increasing `LD_COMP_WAIT*`, and instruction streams showing plausible commit-width distributions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/cycle_accounting.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/energy.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/energy.json

## Purpose
Monaka energy-event topic table. It exposes core, L3 cache, and LDO-loss energy counters for perf power and efficiency analysis.

## APIs, Types, and Functions
The file defines three direct records: `EA_CORE` at `0x01F0`, `EA_L3` at `0x03F0`, and `EA_LDO_LOSS` at `0x03F1`. Each uses the standard perf event JSON fields `EventName`, `EventCode`, and `BriefDescription`.

## Control Flow, State, and Persistence
The event table is generated statically by `jevents.py` and selected at runtime for Monaka cores. Counter values are transient PMU readings; the only persistent behavior here is the checked-in alias-to-code mapping.

## Dependencies and Integration
Depends on Monaka hardware exposing energy events through the core PMU encoding space. It integrates with cycle, frequency-level, cache, and stall events to compute energy per work, per cycle, or per memory behavior in user tooling.

## Risks and Test Signals
Risks include unclear scaling units, model-specific counter width/overflow behavior, and unsupported counters on early silicon or virtualized environments. Test signals are `perf list` visibility, nonzero counts under active workloads, stable deltas over repeated intervals, and correlation between `EA_CORE`, `EA_L3`, workload intensity, and frequency-state counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/energy.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/exception.json

## Purpose
Monaka exception topic file that selects standard ARM64 exception events for the model. It covers exception entry, return, undefined instruction, SVC, instruction/data aborts, IRQ/FIQ, SMC, and HVC.

## APIs, Types, and Functions
The file contains `ArchStdEvent` entries with Monaka descriptions. Aliases include `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, `EXC_SMC`, and `EXC_HVC`.

## Control Flow, State, and Persistence
During build, standard ARM64 event metadata is resolved and emitted into the Monaka PMU table. Runtime perf sessions program counters by alias after CPU matching. No configuration or persistence exists beyond the JSON table.

## Dependencies and Integration
Depends on ARM64 standard event definitions and the Monaka mapfile entry. It integrates with kernel, virtualization, interrupt, and fault-analysis workflows that need exception counts alongside instruction retirement and branch speculation data.

## Risks and Test Signals
Risks are architecture-version differences in exception attribution, virtualization traps being counted differently than expected, and alias resolution failures if standard names change. Test signals include generated table success, controlled syscall and interrupt workloads increasing `EXC_SVC` and `EXC_IRQ`, fault injection increasing abort counters, and consistency between `EXC_TAKEN` and subtype totals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/fp_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/fp_operation.json

## Purpose
Monaka floating-point operation topic table. It covers scalar, Advanced SIMD, SVE, mixed ASIMD/SVE, precision-specific, divide, square-root, FMA, multiply, add/subtract, reciprocal estimate, conversion, reduction, dot-product, matrix-multiply, BF16, and FP8 operation families.

## APIs, Types, and Functions
Most records are `ArchStdEvent` aliases resolved from ARM64 standard metadata, with three direct Monaka records: `FP_MV_SPEC`, `FP_LD_SPEC`, and `FP_ST_SPEC`. Important families include `ASE_FP_*`, `SVE_FP_*`, `ASE_SVE_FP_*`, `FP_SCALE_OPS_SPEC`, `FP_FIXED_OPS_SPEC`, `ASE_SVE_FP_DOT_SPEC`, `ASE_SVE_FP_MMLA_SPEC`, and BF16/FP8 minimum operation counters.

## Control Flow, State, and Persistence
Build-time alias resolution merges standard event codes with local descriptions and direct Monaka event codes into the generated PMU table. Runtime perf sessions use the aliases as static event descriptors; no state persists in the JSON.

## Dependencies and Integration
Depends on the ARM64 standard event catalog for architecture-defined floating-point and vector events and Monaka-specific event codes for move/load/store FP register operations. It integrates with `sve.json`, `pipeline.json`, and `metrics.json`-style external calculations for FLOP and vector utilization analysis.

## Risks and Test Signals
Risks include double counting between aggregate and precision-specific aliases, scaled operation counters using element or vector-length units rather than instruction counts, and unsupported BF16/FP8 events on some hardware revisions. Test signals are `jevents.py` resolution success, microbenchmarks for scalar FP, ASIMD, SVE, FMA, reduction, BF16, and FP8 paths, and sanity checks that aggregate counters dominate their subfamilies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/fp_operation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/gcycle.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/gcycle.json

## Purpose
Monaka global-cycle and frequency-level accounting table. It provides a fixed 100 MHz cycle counter plus per-frequency-level residency counters and retention transition counters.

## APIs, Types, and Functions
The file defines direct event records for `GCYCLES`, `FL0_GCYCLES` through `FL15_GCYCLES`, `RETENTION_GCYCLES`, and `RETENTION_COUNT`. Each record has `EventName`, `EventCode`, and `BriefDescription`.

## Control Flow, State, and Persistence
`jevents.py` converts the JSON records to static perf aliases. Runtime state lives in PMU counters that record frequency-level residency during the measured interval; the JSON holds no mutable state.

## Dependencies and Integration
Depends on Monaka event encodings in the 0x0880-0x08A1 range and the core PMU mapfile. It integrates with cycle, stall, energy, and retention events to normalize performance to frequency behavior and low-power residency.

## Risks and Test Signals
Risks include users treating `GCYCLES` as core clock cycles instead of fixed-rate cycles, unclear frequency-level definitions outside vendor docs, and counter availability differences across firmware. Test signals are `perf stat` visibility, frequency-scaling tests moving counts among `FL*_GCYCLES`, idle tests increasing `RETENTION_GCYCLES` and `RETENTION_COUNT`, and stable 100 MHz-derived deltas for `GCYCLES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/gcycle.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/general.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/general.json

## Purpose
Minimal Monaka general event topic selecting standard cycle counters. It exposes regular CPU cycles and constant-frequency counter cycles.

## APIs, Types, and Functions
The file has two `ArchStdEvent` entries: `CPU_CYCLES` and `CNT_CYCLES`, each with a Monaka description. There are no local event codes or executable functions.

## Control Flow, State, and Persistence
The standard aliases are resolved during generated PMU table construction. At runtime, perf uses them as ordinary event aliases once the Monaka CPU table is selected. The JSON itself is static configuration.

## Dependencies and Integration
Depends on the ARM64 common event catalog and the Monaka CPUID mapfile row. It integrates broadly with every other Monaka topic because cycle counts are denominators for stalls, IPC, cache MPKI, and utilization ratios.

## Risks and Test Signals
Risks are confusing variable CPU cycles with constant counter cycles and losing aliases if standard event names drift. Test signals are successful `jevents.py` generation, `perf stat -e CPU_CYCLES,CNT_CYCLES`, and ratio checks under frequency changes showing expected differences between clock-domain and constant-rate counting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/general.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/hwpf.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/hwpf.json

## Purpose
Monaka hardware-prefetch topic table. It distinguishes L1D, L2, L3, and L1I prefetch requests by stream, stride, target, other, and next-line classes.

## APIs, Types, and Functions
All records are direct Monaka event definitions with `EventName`, `EventCode`, and `BriefDescription`. Aliases include `L1HWPF_STREAM_PF`, `L1HWPF_STRIDE_PF`, `L1HWPF_PFTGT_PF`, `L2HWPF_STREAM_PF`, `L2HWPF_STRIDE_PF`, `L2HWPF_OTHER`, `L3HWPF_STREAM_PF`, `L3HWPF_STRIDE_PF`, `L3HWPF_OTHER`, and `L1IHWPF_NEXTLINE_PF`.

## Control Flow, State, and Persistence
The JSON is compiled into perf alias tables at build time. Runtime counter state is owned by the PMU during each perf session; the file is only persistent alias metadata.

## Dependencies and Integration
Depends on Monaka prefetch event encodings and integrates with L1/L2/L3 cache access/refill files to evaluate prefetch accuracy, coverage, and possible pollution. It is also useful with pipeline stall counters when prefetcher activity correlates with memory latency.

## Risks and Test Signals
Risks include confusing request counts with useful prefetches, overlapping hardware and software prefetch activity in downstream counters, and vendor-specific semantics for target/other classes. Test signals are successful alias generation, streaming and stride microbenchmarks increasing the expected classes, and cache refill reductions or hit changes that correlate with prefetch request volume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/hwpf.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l1d_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l1d_cache.json

## Purpose
Monaka L1 data-cache topic table. It exposes standard and implementation-defined aliases for L1D access, refill, write-back, read/write split, demand access, coherence requests, miss/hit classification, line-fill-buffer hits, prefetch activity, and refill pressure per cycle.

## APIs, Types, and Functions
The file mixes `ArchStdEvent` entries with direct event codes such as `L1D_CACHE_DM`, `L1D_CACHE_DM_RD`, `L1D_CACHE_DM_WR`, `L1D_CACHE_REFILL_DM*`, and `L1D_CACHE_BTC`. Standard aliases include `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_LMISS_RD`, `L1D_CACHE_HIT`, `L1D_LFB_HIT_*`, and `L1D_CACHE_REFILL_PERCYC`.

## Control Flow, State, and Persistence
`jevents.py` resolves standard aliases and emits direct encodings into the Monaka PMU event table. Runtime perf sessions program selected counters; the JSON retains only the static event catalog.

## Dependencies and Integration
Depends on ARM64 common event aliases plus Monaka event codes in the 0x0200 range. It integrates with `hwpf.json`, `memory.json`, `tlb.json`, and `stall.json` to diagnose demand misses, prefetch behavior, write traffic, and backend memory stalls.

## Risks and Test Signals
Risks include overlap between aggregate access/refill counters and demand/prefetch subcounters, nonexclusive LFB hit classifications, and coherence events being platform-sensitive. Test signals are generation success, load/store/cache-thrashing microbenchmarks, prefetch-on/off comparisons, and derived miss ratios that stay bounded when using matching numerator and denominator aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l1d_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l1i_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l1i_cache.json

## Purpose
Monaka L1 instruction-cache topic table. It covers instruction cache access, refill, demand reads, local misses, hardware and software prefetch refills, hits, line-fill-buffer hits, and refill pressure per cycle.

## APIs, Types, and Functions
The JSON uses standard aliases plus direct Monaka definitions `L1I_CACHE_DM_RD` and `L1I_CACHE_REFILL_DM_RD`. Other key aliases are `L1I_CACHE_REFILL`, `L1I_CACHE`, `L1I_CACHE_LMISS`, `L1I_CACHE_HWPRF`, `L1I_CACHE_REFILL_HWPRF`, `L1I_CACHE_HIT_RD`, `L1I_CACHE_HIT`, `L1I_LFB_HIT_RD`, `L1I_CACHE_REFILL_PRF`, and `L1I_CACHE_REFILL_PERCYC`.

## Control Flow, State, and Persistence
The perf build resolves `ArchStdEvent` records and stores direct encodings in generated tables. Runtime selection is static per Monaka CPU; measurement state is PMU counter state only.

## Dependencies and Integration
Depends on common ARM64 instruction-cache events and Monaka event-code definitions. It integrates with frontend stalls, ITLB events, branch/pipeline events, and the `core-imp-def.json` prefetch alias.

## Risks and Test Signals
Risks include demand and prefetch access overlap, instruction-side hardware prefetch behavior varying with firmware settings, and ratio mistakes when pairing all-access denominators with demand-only numerators. Test signals are `perf list` exposure, code-footprint microbenchmarks increasing refills, hot-loop tests showing hits, and frontend memory-bound stalls correlating with L1I/L2I miss activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l1i_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l2_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l2_cache.json

## Purpose
Monaka L2 cache and L2 TLB topic table. It describes L2D access, refill, write-back, demand read/write splits, exclusive/atomic write refills, coherence events, victim/clean/non-temporal/DC ZVA write-backs, flush-back, hit/miss, prefetch, and refill pressure counters.

## APIs, Types, and Functions
The file combines `ArchStdEvent` aliases with direct Monaka events including `L2D_CACHE_DM*`, `L2D_CACHE_HWPRF_ADJACENT`, `L2D_CACHE_REFILL_DM_WR_EXCL`, `L2D_CACHE_REFILL_DM_WR_ATOM`, `L2D_CACHE_BTC`, `L2D_CACHE_WB_VICTIM_CLEAN`, `L2D_CACHE_WB_NT`, `L2D_CACHE_WB_DCZVA`, and `L2D_CACHE_FB`.

## Control Flow, State, and Persistence
Build-time generation resolves standard aliases and writes direct event descriptors into perf. Runtime state is only the active PMU counter set selected by a perf command; the JSON remains static source metadata.

## Dependencies and Integration
Depends on common ARM64 L2 cache/TLB aliases plus Monaka-specific encodings. It integrates with L1D, L3, LL-cache, hardware-prefetch, TLB, memory, and backend stall topics to trace demand traffic beyond the L1.

## Risks and Test Signals
Risks include write-back subcategories not summing to aggregate write-backs, adjacent prefetch semantics being implementation-specific, and coherence events depending on multi-core sharing patterns. Test signals include successful `jevents.py` output, cache-size sweep microbenchmarks, non-temporal store and DC ZVA tests, atomic/write-exclusive workloads, and derived L2 miss ratios using consistent event scopes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l2_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l3_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l3_cache.json

## Purpose
Monaka L3 cache topic table. It represents L3 activity mostly as L2D refill traffic reaching L3, with demand/prefetch, read/write, hit/miss, PFTGT buffer, local memory, remote memory, local/remote L2, and local/remote L3 classifications.

## APIs, Types, and Functions
The file combines `ArchStdEvent` aliases (`L3D_CACHE`, `L3D_CACHE_RD`, `L3D_CACHE_LMISS_RD`) with direct event names such as `L2D_CACHE_REFILL_L3D_CACHE*`, `L2D_CACHE_REFILL_L3D_MISS*`, `L2D_CACHE_REFILL_L3D_HIT*`, and topology-specific `*_L_MEM`, `*_FR_MEM`, `*_L_L2`, `*_NR_L2`, `*_NR_L3`, `*_FR_L2`, and `*_FR_L3`.

## Control Flow, State, and Persistence
The JSON is compiled into perf's generated event table for Monaka. At runtime, aliases program PMU counters for the selected core; persistence is limited to the checked-in JSON and generated perf build artifacts.

## Dependencies and Integration
Depends on Monaka L3 fabric encodings and common ARM64 last-level cache aliases. It integrates with NUMA/locality analysis, L2 refill events, memory traffic analysis, and `ll_cache.json` aliases that summarize last-level read and miss behavior.

## Risks and Test Signals
Risks include notes in the descriptions that several L3 hit/miss events may count inaccurately, topology labels being misunderstood, and aggregate L3 access definitions relying on L2 refill plus clean victim write-back behavior. Test signals are generation success, local versus remote NUMA memory tests, L3-resident and DRAM-resident working-set sweeps, and sanity checks that inaccurate-note events are treated as advisory rather than exact accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/l3_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/ll_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/ll_cache.json

## Purpose
Monaka last-level cache summary topic. It selects standard aliases for last-level read accesses and read misses, described locally in terms of L3D cache activity and L2D refill miss behavior.

## APIs, Types, and Functions
The two records are `ArchStdEvent` aliases `LL_CACHE_RD` and `LL_CACHE_MISS_RD`, each with a Monaka-specific `BriefDescription`. There are no local event codes or functions.

## Control Flow, State, and Persistence
The build resolves the two aliases from the ARM64 standard catalog and includes them in the generated Monaka PMU table. Runtime measurement state is held by PMU counters only.

## Dependencies and Integration
Depends on ARM64 standard last-level cache events and the Monaka mapfile mapping. It integrates with `l3_cache.json` as a concise denominator/numerator pair for high-level LLC miss analysis.

## Risks and Test Signals
Risks include the `LL_CACHE_MISS_RD` description inheriting the L3 miss inaccuracy warning and users assuming LL-cache aliases are independent from L3-topic events. Test signals are alias generation, `perf stat -e LL_CACHE_RD,LL_CACHE_MISS_RD`, and workload sweeps that show read misses increasing once data exceeds local L3 capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/ll_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/memory.json

## Purpose
Monaka memory-operation topic selecting generic load/store access aliases. It provides high-level counters for all memory access instructions and memory reads.

## APIs, Types, and Functions
The file contains two `ArchStdEvent` entries: `MEM_ACCESS` and `MEM_ACCESS_RD`, both with local descriptions tying them to `LDST_SPEC` and `LD_SPEC` semantics. There are no direct event codes or executable APIs.

## Control Flow, State, and Persistence
`jevents.py` resolves the aliases during perf build. Runtime perf sessions select these aliases after Monaka CPU matching; the JSON has no state.

## Dependencies and Integration
Depends on the ARM64 standard event catalog. It integrates with cache, TLB, and stall files as denominator events for load/store intensity, miss ratios, and backend-memory-bound interpretations.

## Risks and Test Signals
Risks include ambiguity between architecturally executed memory instructions and actual cache/fabric transactions, and lack of a write-only alias in this topic. Test signals are successful standard event resolution, load-only and store-only microbenchmarks showing expected behavior, and consistency with `LD_SPEC`, `ST_SPEC`, and `LDST_SPEC` from `spec_operation.json`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/pipeline.json

## Purpose
Monaka pipeline topic table. It exposes valid-cycle counters for address, prefetch, execution, floating-point, store, and L1/L1I/L2 pipelines; predicate population counters; gather/scatter flow counters; and selected TLB/store/interlock stall aliases.

## APIs, Types, and Functions
Direct event names include `EAGA_VAL`, `EAGB_VAL`, `PRX_VAL`, `EXA_VAL` through `EXD_VAL`, `FLA_VAL`, `FLB_VAL`, `STEA_VAL`, `STEB_VAL`, `STFL_VAL`, `STPX_VAL`, `L1_PIPE*`, `L1I_PIPE_*`, `L2_PIPE_*`, and predicate/gather/scatter counters. The final entries use `ArchStdEvent` for `STALL_FRONTEND_TLB`, `STALL_BACKEND_TLB`, `STALL_BACKEND_ST`, and `STALL_BACKEND_ILOCK`.

## Control Flow, State, and Persistence
The perf build merges direct event-code records and standard stall aliases into the generated Monaka table. Runtime state consists only of active PMU counters during perf sessions.

## Dependencies and Integration
Depends on Monaka pipeline event encodings and ARM64 standard stall aliases. It integrates with SVE, FP operation, L1/L2 cache, and stall topic files to localize throughput limitations inside execution, memory, and frontend pipelines.

## Risks and Test Signals
Risks include predicate-count full-width corrections changing between A64FX and Monaka (for example descriptions mention 32 or 64), nonexclusive valid-cycle counters, and gather/scatter flow counters requiring careful interpretation. Test signals are build-time alias generation, scalar/vector/store-heavy microbenchmarks exercising separate pipelines, and correlation between stall aliases here and the broader `stall.json` categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/retired.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/retired.json

## Purpose
Monaka retired-operation topic selecting standard retirement aliases. It covers software PMU increments, retired instructions, context-ID writes, retired branches, branch mispredictions, architecturally executed operations, and retired micro-operations.

## APIs, Types, and Functions
The file uses `ArchStdEvent` entries for `SW_INCR`, `INST_RETIRED`, `CID_WRITE_RETIRED`, `BR_RETIRED`, `BR_MIS_PRED_RETIRED`, `OP_RETIRED`, and `UOP_RETIRED`, each with local descriptions.

## Control Flow, State, and Persistence
Build-time standard alias resolution creates the Monaka event table. Runtime perf measurement is stateless beyond PMU counter values and perf sample records.

## Dependencies and Integration
Depends on `common-and-microarch.json` for standard retirement events. It integrates with cycle accounting, branch/speculation, and IPC calculations where retired instructions or operations serve as denominators.

## Risks and Test Signals
Risks include mixing instruction, operation, and micro-operation counts as if they were interchangeable, and context-ID/write events being privileged or workload-specific. Test signals are successful alias resolution, `perf stat` on simple loops, branch-prediction microbenchmarks increasing branch retired counters, and expected IPC/op-per-cycle relationships against `CPU_CYCLES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/retired.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/spec_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/spec_operation.json

## Purpose
Monaka speculative and architecturally executed operation topic. It covers branch prediction, instruction and operation speculation, exclusive loads/stores, loads/stores, data processing, ASIMD/VFP/crypto, PC writes, branch forms, barriers, predicate/inter-element/inter-register operations, DC ZVA, addressing modes, micro-op split, integer arithmetic, and non-floating-point operation classes.

## APIs, Types, and Functions
Most records are `ArchStdEvent` aliases. Direct Monaka events include `PRD_SPEC`, `IEL_SPEC`, `IREG_SPEC`, `BC_LD_SPEC`, `DCZVA_SPEC`, `EFFECTIVE_INST_SPEC`, `PRE_INDEX_SPEC`, `POST_INDEX_SPEC`, and `UOP_SPLIT`. Standard aliases include `BR_MIS_PRED`, `BR_PRED`, `INST_SPEC`, `OP_SPEC`, `LD_SPEC`, `ST_SPEC`, `LDST_SPEC`, `DP_SPEC`, `CRYPTO_SPEC`, and barrier events.

## Control Flow, State, and Persistence
`jevents.py` resolves standard aliases and emits direct event encodings for the Monaka PMU table. Runtime perf counter programming is driven by the selected aliases; no file-level state exists.

## Dependencies and Integration
Depends on ARM64 common event definitions and Monaka-specific operation counters. It integrates with retired, cycle, pipeline, memory, SVE, and FP operation topics to distinguish executed, speculated, and retired work.

## Risks and Test Signals
Risks include confusing speculative operation counts with retired instruction counts, aggregate events overlapping subfamilies, and architecture references in descriptions requiring ARMv9 interpretation. Test signals are generated table success, branch-mispredict and barrier microbenchmarks, load/store addressing-mode tests, integer multiply/divide loops, and sanity checks that `EFFECTIVE_INST_SPEC` excludes MOVPRFX as described.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/spec_operation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/stall.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/stall.json

## Purpose
Monaka stall taxonomy table. It selects ARM64 standard topdown-style stall aliases for frontend, backend, slot-level, memory-bound, cache/TLB-bound, core-bound, rename, flow, flush, busy, store, atomic, and memory-copy/set stall causes.

## APIs, Types, and Functions
All records are `ArchStdEvent` aliases with Monaka descriptions. Key aliases are `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`, `STALL_FRONTEND_MEMBOUND`, `STALL_FRONTEND_L1I`, `STALL_FRONTEND_L2I`, `STALL_BACKEND_L1D`, `STALL_BACKEND_L2D`, `STALL_BACKEND_BUSY`, and `STALL_BACKEND_RENAME`.

## Control Flow, State, and Persistence
The build resolves standard aliases into generated Monaka PMU tables. Runtime state is the active set of counters in perf and the kernel PMU driver; the JSON is immutable metadata.

## Dependencies and Integration
Depends on ARM64 standard stall event definitions. It integrates with cache, TLB, branch, cycle accounting, and pipeline files to implement topdown-style diagnosis on Monaka.

## Risks and Test Signals
Risks include nonexclusive stall subcategories, denominator confusion between cycles and slots, and standard event availability depending on PMU architecture level. Test signals are `jevents.py` success, `perf stat` topdown-style groups, frontend miss workloads increasing frontend memory/cache stalls, data cache miss workloads increasing backend memory stalls, and rename/resource pressure tests increasing core-bound subevents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/stall.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/sve.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/sve.json

## Purpose
Monaka SVE and SIMD operation topic. It covers SIMD/SVE retirement and speculation, SVE math, integer and non-FP operation classes, predicate generation and permutes, MOVPRFX modes, vector/scalar cross-pipeline transfers, SVE load/store/prefetch patterns, non-temporal accesses, gather/scatter, first-fault loads, precision-scaled FP operations, and integer dot/matrix operations.

## APIs, Types, and Functions
The file uses only `ArchStdEvent` records with Monaka descriptions. Important aliases include `SIMD_INST_RETIRED`, `SVE_INST_RETIRED`, `SVE_INST_SPEC`, `ASE_SVE_INST_SPEC`, `SVE_INT_SPEC`, `SVE_PRED_SPEC`, `SVE_MOVPRFX_Z_SPEC`, `SVE_MOVPRFX_M_SPEC`, `SVE_LDNT_CONTIG_SPEC`, `SVE_STNT_CONTIG_SPEC`, `SVE_LD_GATHER_SPEC`, `SVE_ST_SCATTER_SPEC`, `FP_*_SCALE_OPS_SPEC`, and `ASE_SVE_INT_MMLA_SPEC`.

## Control Flow, State, and Persistence
At build time, perf resolves all standard aliases into the generated Monaka PMU table. Runtime counters are selected by alias through perf; the JSON has no live state or persistence outside source control.

## Dependencies and Integration
Depends on ARM64 common/microarchitecture SVE event definitions. It integrates with `fp_operation.json`, `pipeline.json`, and cache topics for vectorization, predicate density, and memory behavior analysis.

## Risks and Test Signals
Risks include interpreting scalable operation counts without accounting for vector-length semantics, overlapping ASIMD/SVE aggregate aliases, and MOVPRFX fused versus unfused counts being subtle. Test signals are alias-resolution success, SVE integer/FP/gather/scatter/non-temporal microbenchmarks, predicate-density tests for empty/full/partial behavior, and comparison with scalar or ASIMD baselines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/sve.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/tlb.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/tlb.json

## Purpose
Monaka TLB topic table. It includes standard L1/L2 instruction and data TLB access/refill/walk events plus implementation-defined page-size split counters for 4K, 64K, 2M, 32M, 512M, 1G, and 16G pages, walk pressure per cycle, walk steps, and block/page/large/small result classes.

## APIs, Types, and Functions
The file mixes `ArchStdEvent` aliases (`L1I_TLB_REFILL`, `L1D_TLB_REFILL`, `L1D_TLB`, `L1I_TLB`, `L2D_TLB_REFILL`, `L2D_TLB`, `DTLB_WALK`, `ITLB_WALK`, and walk-derived aliases) with direct Monaka `EventName`/`EventCode` records such as `L1I_TLB_4K`, `L1D_TLB_REFILL_2M`, `L2I_TLB_1G`, and `L2D_TLB_REFILL_16G`.

## Control Flow, State, and Persistence
Build-time generation resolves standard events and preserves the direct page-size event encodings. Runtime perf programs counters by alias for Monaka cores. The JSON is static and stores no measured state.

## Dependencies and Integration
Depends on ARM64 standard TLB events and Monaka-specific page-size encodings. It integrates with frontend/backend stall aliases, cache events, and memory access events to diagnose translation overhead and page-size effects.

## Risks and Test Signals
Risks include page-size counters not matching OS page mappings due to huge-page split/merge behavior, walk-derived aliases overlapping, and unsupported page-size encodings on firmware revisions. Test signals are successful generation, workloads pinned to 4K versus huge pages, ITLB pressure from large code footprints, DTLB pressure from random access, and stall correlation with `STALL_FRONTEND_TLB` and `STALL_BACKEND_TLB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/tlb.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/trace.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/trace.json

## Purpose
Monaka trace-related PMU topic selecting standard trace-buffer, trace trigger, external output, and CTI trigger events.

## APIs, Types, and Functions
The file contains `ArchStdEvent` entries for `TRB_WRAP`, `TRB_TRIG`, `TRCEXTOUT0`, and `CTI_TRIGOUT4`, each with a local description. There are no direct event codes or functions.

## Control Flow, State, and Persistence
`jevents.py` resolves the standard trace aliases during generated table construction. Runtime use depends on perf and hardware trace/CTI configuration; the JSON holds only static alias membership.

## Dependencies and Integration
Depends on ARM64 standard trace event definitions and Monaka PMU support. It integrates with tracing workflows that correlate PMU counts with CoreSight trace buffer wrap, trigger, and CTI signaling.

## Risks and Test Signals
Risks include trace infrastructure being disabled or unavailable, aliases resolving but counters staying zero without CoreSight setup, and CTI wiring being platform-specific. Test signals are alias generation, trace sessions that cause buffer wraps or trigger events, and platform validation of external trigger routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/trace.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/core-imp-def.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/core-imp-def.json

## Purpose
HiSilicon Hip08 core implementation-defined event table. It extends the ARM64 core PMU catalog with read/write cache and TLB splits, L1I prefetch counters, frontend fetch/issue bubbles, prefetch request/hit events, and execution or memory stall cycles.

## APIs, Types, and Functions
The JSON mixes standard-style and direct records with `EventName`, `EventCode`, `BriefDescription`, and `PublicDescription`. Important aliases include `L1D_CACHE_RD/WR`, `L1D_CACHE_REFILL_RD/WR`, `L1D_TLB_RD/WR`, `L2D_CACHE_RD/WR`, `L2D_CACHE_REFILL_RD/WR`, `L1I_CACHE_PRF`, `IQ_IS_EMPTY`, `IF_IS_STALL`, `FETCH_BUBBLE`, `PRF_REQ`, `HIT_ON_PRF`, `EXE_STALL_CYCLE`, and `MEM_STALL_*`.

## Control Flow, State, and Persistence
Perf build tooling reads this file when generating the Hip08 PMU event table selected by CPUID `0x00000000480fd010`. Runtime perf aliases are static descriptors for hardware counters; the JSON itself has no state.

## Dependencies and Integration
Depends on Hip08 event-code definitions and the ARM64 mapfile entry. It integrates with `metrics.json`, whose topdown formulas reference many of these implementation-defined events, and with uncore Hip08 DDRC/HHA/L3C files for socket-level diagnosis.

## Risks and Test Signals
Risks include metric expressions breaking if event names change, direct event encodings drifting from firmware, and frontend/memory stall aliases being nonexclusive. Test signals are JSON and `jevents.py` success, `perf list` showing Hip08 names, topdown metric evaluation, and workload tests for cache/TLB pressure, prefetch behavior, fetch stalls, and execution stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/core-imp-def.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/metrics.json

## Purpose
Hip08 derived metrics table for topdown-style performance diagnosis. It defines frontend, bad speculation, retiring, backend, fetch latency/bandwidth, branch misprediction and flush submetrics, core and memory bound classes, execution port utilization, cache-level bounds, and store bound metrics.

## APIs, Types, and Functions
Records use perf metric schema fields such as `MetricName`, `MetricExpr`, `MetricGroup`, `DefaultMetricgroupName`, `BriefDescription`, and `PublicDescription`. Metric names include `frontend_bound`, `bad_speculation`, `retiring`, `backend_bound`, `fetch_latency_bound`, `branch_mispredicts`, `machine_clears`, `core_bound`, `memory_bound`, `idle_by_itlb_miss`, `bp_misp_flush`, `rob_stall`, `l1_bound`, `l2_bound`, `mem_bound`, and `store_bound`.

## Control Flow, State, and Persistence
`jevents.py` preserves metric expressions into generated perf metadata. At runtime, perf metric evaluation reads underlying PMU events from `core-imp-def.json` and standard ARM64 events, computes formulas over measured counts, and reports percentages or ratios. No metric state is persisted by the JSON.

## Dependencies and Integration
Depends heavily on Hip08 event aliases such as `FETCH_BUBBLE`, `BR_MIS_PRED`, `EXE_STALL_CYCLE`, `MEM_STALL_L1MISS`, and cache/TLB events. It integrates with `perf stat -M` and provides the main human-facing analysis layer above raw Hip08 counters.

## Risks and Test Signals
Risks include divide-by-zero expressions, formulas that assume Intel-like topdown slot semantics on Hip08, missing source events, and percentage metrics that are not mutually exclusive. Test signals are `perf list --metrics`, `perf stat -M` on Hip08, expression parser success, no missing-event warnings, and sanity under branch-heavy, memory-bound, core-bound, and frontend-bound microbenchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-ddrc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-ddrc.json

## Purpose
Hip08 uncore DDR controller PMU event table. It exposes memory read/write flux, command counts, precharge/activate commands, rank changes, and read/write direction changes.

## APIs, Types, and Functions
Records use uncore schema fields `EventName`, `ConfigCode`, `BriefDescription`, and `Unit`. Aliases are `flux_wr`, `flux_rd`, `flux_wcmd`, `flux_rcmd`, `pre_cmd`, `act_cmd`, `rnk_chg`, and `rw_chg`, all associated with the DDRC unit.

## Control Flow, State, and Persistence
At perf build time, the uncore JSON is encoded into PMU metadata. Runtime perf uses the uncore PMU unit name and config code rather than core event codes; counter state belongs to the DDRC PMU instance during a measurement.

## Dependencies and Integration
Depends on Hip08 uncore PMU driver naming and config-code interpretation. It integrates with core memory-bound metrics, HHA home-agent events, and L3C events to explain bandwidth and DRAM command behavior.

## Risks and Test Signals
Risks include uncore unit naming mismatches, multi-controller aggregation mistakes, permissions or kernel support limiting uncore access, and flux units needing conversion before bandwidth comparisons. Test signals are `perf list` uncore visibility, memory bandwidth workloads increasing `flux_rd`/`flux_wr`, row-locality tests affecting precharge/activate counts, and multi-controller runs showing expected distribution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-ddrc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-hha.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-hha.json

## Purpose
Hip08 uncore HHA home-agent PMU event table. It tracks received operations from outer/SCCL/CCIX paths, write-back and stash traffic, DDR read/write transactions, spill behavior, broadcast/invalidation and snoop traffic, snoop responses, directory lookup/hit counts, and home migration.

## APIs, Types, and Functions
Records use `EventName`, `ConfigCode`, `BriefDescription`, and `Unit`. Important aliases include `rx_ops_num`, `rx_outer`, `rx_sccl`, `rx_ccix`, `rx_wbi`, `rd_ddr_64b`, `wr_ddr_128b`, `spill_num`, `spill_success`, `bi_num`, `tx_snp_num`, `rx_snprspdata`, `sdir-lookup`, `edir-lookup`, `sdir-hit`, `edir-hit`, and home-migrate events.

## Control Flow, State, and Persistence
The file is compiled into perf uncore event metadata. Runtime perf programs HHA unit counters by config code; the JSON stores no mutable state and no aggregation policy.

## Dependencies and Integration
Depends on the Hip08 HHA uncore PMU driver exposing matching unit names and config codes. It integrates with DDRC and L3C uncore events plus core cache-miss and memory-bound metrics to analyze coherence and memory-routing behavior.

## Risks and Test Signals
Risks include event names containing hyphens needing correct perf alias handling, topology-specific SCCL/CCIX semantics, multi-agent aggregation errors, and directory counters not matching simple cache-hit expectations. Test signals are alias generation, socket-local versus remote/coherent workloads, CCIX traffic tests where available, and consistency among HHA DDR transaction counts and DDRC flux counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-hha.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-l3c.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-l3c.json

## Purpose
Hip08 uncore L3 cache PMU event table. It records read/write traffic and hits in CPIPE and SPIPE paths, victim counts, invalidations, CPU and ring retries, and dropped prefetches.

## APIs, Types, and Functions
Each event uses `EventName`, `ConfigCode`, `BriefDescription`, and `Unit`. Aliases include `rd_cpipe`, `wr_cpipe`, `rd_hit_cpipe`, `wr_hit_cpipe`, `victim_num`, `rd_spipe`, `wr_spipe`, `rd_hit_spipe`, `wr_hit_spipe`, `back_invalid`, `retry_cpu`, `retry_ring`, and `prefetch_drop`.

## Control Flow, State, and Persistence
Perf encodes the uncore table at build time and uses config codes at runtime for L3C PMU instances. The JSON has no state and does not define cross-instance aggregation.

## Dependencies and Integration
Depends on the Hip08 L3C uncore PMU driver and unit naming. It integrates with HHA directory/coherence counters, DDRC traffic counters, and core L2/L3 miss metrics to diagnose LLC behavior and fabric backpressure.

## Risks and Test Signals
Risks include CPIPE/SPIPE meaning being vendor-specific, retries indicating congestion but not the full source, and prefetch-drop interpretation depending on hardware prefetch policy. Test signals are `perf list` visibility, cache-resident and cache-thrashing workloads, retry increases under contention, and hit/access ratios that move predictably with working-set size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-l3c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip09/sys/uncore-cpa.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip09/sys/uncore-cpa.json

## Purpose
Hip09 system uncore CPA PMU table. It exposes CPA cycles, port 0 and port 1 read/write data counts, width-specific 64-bit and 32-bit read data counts, and derived average bandwidth metrics per port.

## APIs, Types, and Functions
Raw event records use `EventName`, `ConfigCode`, `Unit`, and `Compat`; metric records additionally use `MetricName`, `MetricExpr`, and `MetricGroup`. Aliases include `cpa_cycles`, `cpa_p1_wr_dat`, `cpa_p1_rd_dat`, `cpa_p1_rd_dat_64b`, `cpa_p1_rd_dat_32b`, `cpa_p0_wr_dat`, `cpa_p0_rd_dat`, and metric names `cpa_p1_avg_bw` and `cpa_p0_avg_bw`.

## Control Flow, State, and Persistence
The raw events and metric expressions are compiled into perf metadata. At runtime, perf can program the system uncore PMU by config code and evaluate average bandwidth formulas from data counts and cycles. The JSON contains no runtime persistence.

## Dependencies and Integration
Depends on the Hip09 CPA PMU compatible string, uncore unit naming, and perf metric-expression support. It integrates with system-level bandwidth analysis rather than core CPUID mapping alone.

## Risks and Test Signals
Risks include `Compat` strings not matching kernel PMU device names, bandwidth formulas assuming a fixed cycle/data unit scale, and per-port aggregation being misread as system total bandwidth. Test signals are `perf list` on Hip09, raw event increments under CPA traffic, metric evaluation without missing events, and bandwidth estimates matching external memory or interconnect benchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip09/sys/uncore-cpa.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/branch.json

## Purpose
NVIDIA T410 branch PMU topic table. It combines standard branch prediction aliases with T410-specific branch target buffer context updates, directional misprediction resolution classes, multi-branch prediction resolution, and region reclaim events.

## APIs, Types, and Functions
The file mixes `ArchStdEvent` entries (`BR_MIS_PRED`, `BR_PRED`) with direct records such as `BR_PRED_BTB_CTX_UPDATE`, `BR_MIS_PRED_DIR_RESOLVED`, `BR_MIS_PRED_DIR_UNCOND_RESOLVED`, `BR_MIS_PRED_DIR_UNCOND_DIRECT_RESOLVED`, `BR_PRED_MULTI_RESOLVED`, `BR_MIS_PRED_MULTI_RESOLVED`, and `BR_RGN_RECLAIM`. Direct records use `EventCode`, `EventName`, and `PublicDescription`.

## Control Flow, State, and Persistence
Perf build generation resolves standard aliases and emits T410 direct event descriptors. Runtime selection follows the ARM64 mapfile row for CPUID `0x000000004e0f0100`; counters are transient per perf session.

## Dependencies and Integration
Depends on ARM64 standard branch events and NVIDIA T410 event-code definitions. It integrates with T410 metrics for branch misprediction ratios and frontend-bound analysis.

## Risks and Test Signals
Risks include misprediction subevents not being additive, vendor-specific BTB context and region reclaim semantics, and alias conflicts with standard branch events. Test signals are successful generation, branch-heavy and indirect-branch benchmarks, correlation with `branch_misprediction_ratio` metrics, and predictable increases in direction-specific counters for controlled branch patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/brbe.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/brbe.json

## Purpose
NVIDIA T410 BRBE topic file selecting the standard branch-record filtering event. It exposes `BRB_FILTRATE` for branch record buffer filtering activity.

## APIs, Types, and Functions
The only entry is `ArchStdEvent: BRB_FILTRATE` with a public description. There are no local event codes or functions.

## Control Flow, State, and Persistence
Build-time alias resolution imports the standard BRBE event into the generated T410 PMU table. Runtime behavior depends on PMU and BRBE support exposed by the kernel; the JSON stores no state.

## Dependencies and Integration
Depends on `common-and-microarch.json` containing `BRB_FILTRATE` and on T410 mapfile selection. It integrates with branch sampling/recording workflows rather than ordinary branch count metrics alone.

## Risks and Test Signals
Risks include BRBE support being disabled or absent in the kernel despite alias availability, and users expecting counts without configuring branch records. Test signals are successful alias generation, `perf list` visibility, and branch-recording workloads that exercise BRB filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/brbe.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/bus.json

## Purpose
NVIDIA T410 bus and CHI activity topic. It exposes generic bus access/cycle/read/write/request/retry aliases plus T410-specific L2 CHI channel busy counters.

## APIs, Types, and Functions
The file uses standard `ArchStdEvent` names for `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`, `BUS_REQUEST_REQ`, and `BUS_REQUEST_RETRY`, and direct `EventCode` records `L2_CHI_CBUSY0` through `L2_CHI_CBUSY3`.

## Control Flow, State, and Persistence
Build-time generation resolves standard bus aliases and stores direct CHI event codes. Runtime perf sessions program the selected aliases on T410 core PMUs. The JSON itself is immutable metadata.

## Dependencies and Integration
Depends on ARM64 standard bus events, T410 CHI event encodings, and CPUID mapfile selection. It integrates with cache and memory metrics, especially `bus_bandwidth` and backend memory-bound calculations.

## Risks and Test Signals
Risks include CHI channel busy counters being difficult to aggregate, standard bus events not mapping cleanly to fabric bandwidth, and retry events indicating contention without identifying source. Test signals include alias generation, memory bandwidth tests increasing read/write access counts, contention tests increasing retries or CHI busy counts, and metric formulas producing plausible bandwidth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/exception.json

## Purpose
NVIDIA T410 exception topic table. It selects standard exception entry/return/subtype events plus trapped exception classes for aborts, other traps, IRQ, and FIQ.

## APIs, Types, and Functions
All records are `ArchStdEvent` aliases with public descriptions. Names include `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, `EXC_SMC`, `EXC_HVC`, `EXC_TRAP_PABORT`, `EXC_TRAP_DABORT`, `EXC_TRAP_OTHER`, `EXC_TRAP_IRQ`, and `EXC_TRAP_FIQ`.

## Control Flow, State, and Persistence
The perf build resolves these standard aliases into the generated T410 PMU table. Runtime counter state is owned by PMU hardware and perf sessions; the JSON has no persistence beyond source metadata.

## Dependencies and Integration
Depends on ARM64 standard exception events and the T410 mapfile row. It integrates with virtualization, kernel fault, and interrupt diagnostics on NVIDIA ARM64 systems.

## Risks and Test Signals
Risks include traps being counted differently across exception levels, virtualized environments masking hardware events, and subtype totals not matching aggregate `EXC_TAKEN` exactly. Test signals are successful generation, syscall and interrupt workloads, fault injection for aborts, hypervisor trap tests where available, and consistency with kernel tracepoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/fp_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/fp_operation.json

## Purpose
NVIDIA T410 floating-point operation topic selecting standard FP precision and operation-scaling aliases. It covers half, single, double precision, scalable and fixed operation counts, minimum precision operation counts, BF16, and FP8 classes.

## APIs, Types, and Functions
The file contains only `ArchStdEvent` entries such as `FP_HP_SPEC`, `FP_SP_SPEC`, `FP_DP_SPEC`, `FP_SCALE_OPS_SPEC`, `FP_FIXED_OPS_SPEC`, `FP_HP_SCALE_OPS_SPEC`, `FP_SP_FIXED_OPS_SPEC`, `FP_DP_FIXED_OPS_SPEC`, `FP_SP_FIXED_MIN_OPS_SPEC`, `FP_BF16_FIXED_MIN_OPS_SPEC`, `FP_FP8_FIXED_MIN_OPS_SPEC`, and scalable minimum operation aliases.

## Control Flow, State, and Persistence
Build-time standard alias resolution adds these events to the generated T410 table. Runtime perf measurement uses PMU counters selected by alias; the JSON is static.

## Dependencies and Integration
Depends on ARM64 common FP event definitions. It integrates with T410 `metrics.json` for FP16/FP32/FP64 percentages and FP operations per cycle, and with SVE-related metrics where supported through standard event names.

## Risks and Test Signals
Risks include hardware support gaps for BF16 or FP8 aliases, scaled counters not equal to instruction counts, and overlap between aggregate precision counters. Test signals are alias-generation success, FP microbenchmarks by precision, BF16/FP8 tests on capable hardware, and metric sanity for `fp_ops_per_cycle`, `fp16_percentage`, `fp32_percentage`, and `fp64_percentage`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/fp_operation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/general.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/general.json

## Purpose
NVIDIA T410 general event topic exposing core cycle, constant counter cycle, and CPU slot counters. These are central denominators for topdown metrics and IPC-style calculations.

## APIs, Types, and Functions
The records are `ArchStdEvent` aliases `CPU_CYCLES` and `CNT_CYCLES`, plus `CPU_SLOT` with direct T410 metadata. Fields include `ArchStdEvent`, `EventName`, `EventCode`, and `PublicDescription` depending on the record.

## Control Flow, State, and Persistence
Perf generation resolves standard aliases and emits the slot event into the T410 table. At runtime, metrics in `metrics.json` use these counters as denominators for slots, cycles, SMT/ST mode, and IPC calculations.

## Dependencies and Integration
Depends on ARM64 common cycle events, T410 slot event encoding, and mapfile selection. It integrates directly with nearly every T410 metric.

## Risks and Test Signals
Risks include slot semantics changing with SMT mode, users confusing `CNT_CYCLES` with core cycles, and divide-by-zero in metrics when counters are not scheduled together. Test signals are `perf stat` for the three aliases, metric evaluation for topdown groups, and frequency/SMT tests showing expected cycle and slot relationships.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/general.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l1d_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l1d_cache.json

## Purpose
NVIDIA T410 L1 data-cache topic table. It covers standard L1D accesses/refills/write-backs, read/write splits, inner/outer refill sources, invalidations, read-write and prefetch classes, demand miss/refill classes, hardware/software prefetch hit and refill classifications, line-fill-buffer hits, and outer LLC/DRAM/remote refill classes.

## APIs, Types, and Functions
The file mixes `ArchStdEvent` aliases with direct T410 event records. Names include `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_RD`, `L1D_CACHE_WR`, `L1D_CACHE_REFILL_INNER`, `L1D_CACHE_REFILL_OUTER`, `L1D_CACHE_RW`, `L1D_CACHE_PRFM`, `L1D_CACHE_HIT_RW_FPRF*`, `L1D_LFB_HIT_RW_FPRF*`, and `L1D_CACHE_REFILL_OUTER_*`.

## Control Flow, State, and Persistence
Build-time generation resolves standard events and includes T410-specific encodings. Runtime state is PMU counter state selected by perf aliases; the JSON does not persist measurements.

## Dependencies and Integration
Depends on ARM64 cache aliases and T410 implementation-specific refill/source events. It integrates with T410 metrics for L1D miss ratio, MPKI, prefetch accuracy/coverage, demand accesses/misses, and backend cache-bound analysis.

## Risks and Test Signals
Risks include overlapping demand, prefetch, hardware prefetch, and outer-source categories; remote refill classifications being topology-specific; and metrics requiring matching denominators. Test signals are `jevents.py` success, streaming/random load-store tests, prefetch control tests, cache-size sweeps, and metric sanity for L1D demand and prefetch groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l1d_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l1i_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l1i_cache.json

## Purpose
NVIDIA T410 L1 instruction-cache topic table. It describes instruction-cache accesses, refills, local misses, read and prefetch classes, hardware prefetches, hit and line-fill-buffer classifications, dropped hardware prefetch requests, CFC entries, invalidations, and prefetch request types.

## APIs, Types, and Functions
The records combine standard aliases with T410-specific `EventName`/`EventCode` entries. Important names include `L1I_CACHE_REFILL`, `L1I_CACHE`, `L1I_CACHE_LMISS`, `L1I_CACHE_RD`, `L1I_CACHE_PRFM`, `L1I_CACHE_HWPRF`, `L1I_CACHE_REFILL_RD`, `L1I_CFC_ENTRIES`, `L1I_HWPRF_REQ_DROP`, `L1I_PRFM_REQ`, `L1I_HWPRF_REQ`, and several `*_FPRF` filtered hit events.

## Control Flow, State, and Persistence
Perf build tooling emits the combined standard/direct table for T410. Runtime perf sessions select aliases for active counters; the JSON remains static metadata.

## Dependencies and Integration
Depends on ARM64 instruction-cache standard aliases and NVIDIA T410 event encodings. It integrates with frontend-bound metrics, branch behavior, ITLB metrics, and instruction-fetch latency calculations.

## Risks and Test Signals
Risks include prefetch hit filters being hard to interpret, dropped request counts not directly mapping to performance loss, and CFC entry semantics requiring vendor knowledge. Test signals are alias generation, hot-code versus large-code-footprint benchmarks, instruction-prefetch experiments, frontend cache-bound metric correlation, and expected changes in `l1i_cache_miss_ratio` and `instruction_fetch_average_latency`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l1i_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l2d_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l2d_cache.json

## Purpose
NVIDIA T410 L2 data-cache topic table. It covers L2D accesses/refills/write-backs, read/write splits, invalidations, local misses, read-write/prefetch classes, hardware prefetch and generic prefetch refills, instruction fetch/TBW/PF refill classes, L1-prefetch-induced traffic, virtual alias backsnoop, and filtered hit/LFB behavior.

## APIs, Types, and Functions
The JSON uses `ArchStdEvent` plus direct event records. Names include `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_RD`, `L2D_CACHE_WR`, `L2D_CACHE_LMISS_RD`, `L2D_CACHE_RW`, `L2D_CACHE_PRFM`, `L2D_CACHE_IF_REFILL`, `L2D_CACHE_TBW_REFILL`, `L2D_CACHE_PF_REFILL`, `L2D_CACHE_L1PRF`, `L2D_CACHE_REFILL_L1PRF`, and `L2D_CACHE_BACKSNOOP_L1D_VIRT_ALIASING`.

## Control Flow, State, and Persistence
Build-time generation resolves standard aliases and stores T410 direct encodings. Runtime perf aliases program counters on the selected T410 PMU; the JSON has no mutable state.

## Dependencies and Integration
Depends on ARM64 L2D aliases and T410-specific L2 events. It integrates with L1D, LLC, bus, memory, and T410 metrics for L2 miss ratios, MPKI, prefetch accuracy, and backend cache-bound analysis.

## Risks and Test Signals
Risks include overlap among L1 prefetch, hardware prefetch, and demand refills; virtual alias backsnoop events being rare and platform-sensitive; and TBW/PF refill meanings requiring vendor context. Test signals are cache-size sweep benchmarks, instruction/data refill separation tests, prefetch accuracy metrics, and consistency between L2 refills and LLC/bus traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/l2d_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/ll_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/ll_cache.json

## Purpose
NVIDIA T410 last-level/L3 cache topic table. It exposes L3 allocation, refill, access, read, local miss, read-write, prefetch, hardware prefetch, L1/L2 prefetch-induced traffic, instruction fetch and memory-management refills, and standard `LL_CACHE_RD`/`LL_CACHE_MISS_RD` aliases.

## APIs, Types, and Functions
The file combines `ArchStdEvent` entries with direct event names such as `L3D_CACHE_ALLOCATE`, `L3D_CACHE_REFILL`, `L3D_CACHE`, `L3D_CACHE_RD`, `L3D_CACHE_REFILL_RD`, `L3D_CACHE_LMISS_RD`, `L3D_CACHE_RW`, `L3D_CACHE_PRFM`, `L3D_CACHE_REFILL_RWL1PRFL2PRF`, `L3D_CACHE_REFILL_IF`, `L3D_CACHE_REFILL_MM`, `L3D_CACHE_L1PRF`, and `L3D_CACHE_L2PRF`.

## Control Flow, State, and Persistence
Perf generation resolves the standard LL aliases and emits T410 L3 direct encodings. Runtime state is limited to active PMU counters selected by perf.

## Dependencies and Integration
Depends on ARM64 LLC aliases and NVIDIA T410 L3 event definitions. It integrates with L2D cache, bus, memory, and metrics for LLC read hit/miss ratios, MPKI, demand access/miss counts, and prefetch accuracy/coverage.

## Risks and Test Signals
Risks include aggregate L3 events overlapping with L1/L2 prefetch-origin subevents, instruction and memory-management refills requiring careful attribution, and LLC metrics using read-only denominators. Test signals are generated alias success, LLC working-set sweeps, prefetch-heavy tests, instruction-fetch refill tests, and consistency between LLC misses and bus/memory traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/ll_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/memory.json

## Purpose
NVIDIA T410 memory topic selecting standard memory access, remote access, alignment latency, instruction fetch, and per-cycle access counters. It provides high-level load/store/fetch activity and latency anchors for metrics.

## APIs, Types, and Functions
All records are `ArchStdEvent` aliases with public descriptions. Names include `MEM_ACCESS`, `MEMORY_ERROR`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `LDST_ALIGN_LAT`, `LD_ALIGN_LAT`, `ST_ALIGN_LAT`, `INST_FETCH_PERCYC`, `MEM_ACCESS_RD_PERCYC`, and `INST_FETCH`.

## Control Flow, State, and Persistence
Build-time standard alias resolution includes these events in the T410 PMU table. Runtime perf sessions measure counters by alias; no file state exists.

## Dependencies and Integration
Depends on ARM64 common memory and latency event definitions. It integrates with T410 metrics for load/store percentages, load average latency, instruction fetch latency, remote access behavior, and memory-bound diagnosis.

## Risks and Test Signals
Risks include latency events counting accumulated latency rather than event occurrences, remote access visibility being topology-dependent, and memory errors being rare or privileged. Test signals are generation success, aligned versus unaligned access tests, load/store microbenchmarks, remote NUMA traffic where applicable, and metrics that pair per-cycle latency counters with matching access counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/metrics.json

## Purpose
NVIDIA T410 derived metrics table. It defines 103 perf metrics for topdown L1/backend/frontend breakdowns, branch ratios and MPKI, bus bandwidth, SMT/ST cycle fractions, crypto/integer/FP/SIMD/SVE percentages, TLB MPKI and walk latency, cache miss ratios and MPKI, prefetch accuracy/coverage/usefulness, LLC hit/miss ratios, load/store percentages, IPC, and SVE predicate density.

## APIs, Types, and Functions
Records use `MetricName`, `MetricExpr`, `BriefDescription`, `ScaleUnit`, and `MetricGroup`. Important groups include `TopdownL1`, `Topdown_Backend`, `Topdown_Frontend`, `Cycle_Accounting`, `Branch`, `Bus`, `General`, `Cache`, `Memory`, `Pipeline`, `SVE`, `TLB`, and `Retiring`. Expressions reference raw aliases from the T410 topic files, for example `STALL_SLOT_BACKEND / CPU_SLOT`, `L1D_CACHE_REFILL / INST_RETIRED`, and prefetch-derived numerator/denominator pairs.

## Control Flow, State, and Persistence
`jevents.py` embeds metric metadata into generated perf tables. Runtime perf metric evaluation schedules referenced events where possible, reads counts, evaluates `MetricExpr`, applies `ScaleUnit`, and groups output by `MetricGroup`. The JSON does not persist computed values.

## Dependencies and Integration
Depends on nearly every T410 raw-event topic in this work item plus additional T410 files not in this subset, such as retired, stall, spec operation, and TLB event tables. It is the main integration layer that turns raw PMU aliases into user-facing performance analysis.

## Risks and Test Signals
Risks include missing referenced events when related JSON files are absent or renamed, divide-by-zero expressions, multiplexing errors when metrics require too many counters, overlapping percentages, and formulas that assume specific cache/prefetch semantics. Test signals are `perf list --metrics`, `perf stat -M` for each metric group, expression parser success with no unresolved aliases, controlled frontend/backend/branch/cache/TLB/SVE workloads, and comparison of derived ratios against raw counter sanity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/metrics.json -->
