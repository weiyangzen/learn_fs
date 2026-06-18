<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/tlb.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/tlb.json

## Purpose
Lists 16 Arm architecture-standard event references for TLB translation behavior on the Arm Neoverse V1 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 16 JSON records using `ArchStdEvent` references. It exports standard aliases `L1I_TLB_REFILL`, `L1D_TLB_REFILL`, `L1D_TLB`, `L1I_TLB`, `L2D_TLB_REFILL`, `L2D_TLB`, `DTLB_WALK`, `ITLB_WALK`, `L1D_TLB_REFILL_RD`, `L1D_TLB_REFILL_WR`, `L1D_TLB_RD`, `L1D_TLB_WR`, and 4 more. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/tlb.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/brbe.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/brbe.json

## Purpose
Lists 1 Arm architecture-standard event references for branch record buffer extension filtering on the Arm Neoverse V3 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 1 JSON records using `ArchStdEvent` references. It exports standard aliases `BRB_FILTRATE`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/brbe.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/bus.json

## Purpose
Lists 4 Arm architecture-standard event references for bus and interconnect traffic on the Arm Neoverse V3 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 4 JSON records using `ArchStdEvent` references. It exports standard aliases `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/exception.json

## Purpose
Lists 15 Arm architecture-standard event references for exception and trap accounting on the Arm Neoverse V3 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 15 JSON records using `ArchStdEvent` references. It exports standard aliases `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, `EXC_SMC`, `EXC_HVC`, `EXC_TRAP_PABORT`, `EXC_TRAP_DABORT`, and 3 more. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/fp_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/fp_operation.json

## Purpose
Lists 5 Arm architecture-standard event references for floating point operation mix on the Arm Neoverse V3 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 5 JSON records using `ArchStdEvent` references. It exports standard aliases `FP_HP_SPEC`, `FP_SP_SPEC`, `FP_DP_SPEC`, `FP_SCALE_OPS_SPEC`, `FP_FIXED_OPS_SPEC`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/fp_operation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/general.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/general.json

## Purpose
Combines 2 Arm architecture-standard event references with 5 implementation-defined events for cycle and CHI response-pressure accounting on the Arm Neoverse V3 core model. The file lets perf expose both standardized aliases and model-specific counters from one topic table.

## APIs, Types, and Functions
The file has 7 JSON records using `ArchStdEvent` references, `EventName`/`EventCode` entries. It exports standard aliases `CPU_CYCLES`, `CNT_CYCLES`; custom encodings `L2_CHI_CBUSY0` (`0x198`), `L2_CHI_CBUSY1` (`0x199`), `L2_CHI_CBUSY2` (`0x19A`), `L2_CHI_CBUSY3` (`0x19B`), `L2_CHI_CBUSY_MT` (`0x19C`). `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias; wrong raw `EventCode` values produce misleading perf counts. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/general.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/l1d_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/l1d_cache.json

## Purpose
Lists 18 Arm architecture-standard event references for L1 data cache behavior on the Arm Neoverse V3 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 18 JSON records using `ArchStdEvent` references. It exports standard aliases `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_LMISS_RD`, `L1D_CACHE_RD`, `L1D_CACHE_WR`, `L1D_CACHE_REFILL_RD`, `L1D_CACHE_REFILL_WR`, `L1D_CACHE_REFILL_INNER`, `L1D_CACHE_REFILL_OUTER`, `L1D_CACHE_WB_VICTIM`, `L1D_CACHE_WB_CLEAN`, and 6 more. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/l1d_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/l1i_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/l1i_cache.json

## Purpose
Lists 15 Arm architecture-standard event references for L1 instruction cache behavior on the Arm Neoverse V3 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 15 JSON records using `ArchStdEvent` references. It exports standard aliases `L1I_CACHE_REFILL`, `L1I_CACHE`, `L1I_CACHE_LMISS`, `L1I_CACHE_RD`, `L1I_CACHE_PRFM`, `L1I_CACHE_HWPRF`, `L1I_CACHE_REFILL_PRFM`, `L1I_CACHE_HIT_RD`, `L1I_CACHE_HIT_RD_FPRFM`, `L1I_CACHE_HIT_RD_FHWPRF`, `L1I_CACHE_HIT`, `L1I_CACHE_HIT_PRFM`, and 3 more. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/l1i_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/l2_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/l2_cache.json

## Purpose
Combines 16 Arm architecture-standard event references with 2 implementation-defined events for L2 data cache behavior on the Arm Neoverse V3 core model. The file lets perf expose both standardized aliases and model-specific counters from one topic table.

## APIs, Types, and Functions
The file has 18 JSON records using `ArchStdEvent` references, `EventName`/`EventCode` entries. It exports standard aliases `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_RD`, `L2D_CACHE_WR`, `L2D_CACHE_REFILL_RD`, `L2D_CACHE_REFILL_WR`, `L2D_CACHE_WB_VICTIM`, `L2D_CACHE_WB_CLEAN`, `L2D_CACHE_INVAL`, `L2D_CACHE_LMISS_RD`, `L2D_CACHE_RW`, and 4 more; custom encodings `L2D_CACHE_L1HWPRF` (`0x1B8`), `L2D_CACHE_REFILL_L1HWPRF` (`0x1B9`). `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias; wrong raw `EventCode` values produce misleading perf counts. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/l2_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/ll_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/ll_cache.json

## Purpose
Lists 2 Arm architecture-standard event references for last-level cache read behavior on the Arm Neoverse V3 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 2 JSON records using `ArchStdEvent` references. It exports standard aliases `LL_CACHE_RD`, `LL_CACHE_MISS_RD`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/ll_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/memory.json

## Purpose
Lists 14 Arm architecture-standard event references for memory access and alignment behavior on the Arm Neoverse V3 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 14 JSON records using `ArchStdEvent` references. It exports standard aliases `MEM_ACCESS`, `MEMORY_ERROR`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `LDST_ALIGN_LAT`, `LD_ALIGN_LAT`, `ST_ALIGN_LAT`, `MEM_ACCESS_CHECKED`, `MEM_ACCESS_CHECKED_RD`, `MEM_ACCESS_CHECKED_WR`, `INST_FETCH_PERCYC`, and 2 more. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/metrics.json

## Purpose
Provides 63 derived perf metrics for the Arm Neoverse V3 core model, covering derived perf metrics. The entries expose user-facing `MetricName` aliases such as backend_busy_bound, backend_cache_l1d_bound, backend_cache_l2d_bound, backend_core_bound, backend_core_rename_bound, backend_mem_bound, backend_mem_cache_bound, backend_mem_store_bound, backend_mem_tlb_bound, backend_stalled_cycles, and 53 more and translate raw events into ratios, byte counts, percentages, or bandwidth utilization values.

## APIs, Types, and Functions
The exported API is declarative metric metadata: `ArchStdEvent` references, `MetricName`/`MetricExpr` formulas. Metric expressions are perf JSON formulas parsed by `metric.ParsePerfJson()` and may reference raw events, architecture-standard aliases, PMU filter syntax, and `duration_time`. Example metric names include `backend_busy_bound`, `backend_cache_l1d_bound`, `backend_cache_l2d_bound`, `backend_core_bound`, `backend_core_rename_bound`. Metric groups are Branch_Effectiveness, Cycle_Accounting, FP_Arithmetic_Intensity, FP_Precision_Mix, General, LL_Cache_Effectiveness, MPKI;Branch_Effectiveness, MPKI;DTLB_Effectiveness, MPKI;ITLB_Effectiveness, MPKI;ITLB_Effectiveness;DTLB_Effectiveness, and 16 more.

## Control Flow, State, and Persistence
There is no executable control flow in the JSON itself. Build-time flow is: perf scans the architecture directory, loads this file, parses each `MetricExpr`, validates event/PMU references, then emits generated metric tables into `pmu-events.c`. Runtime state is limited to hardware counters sampled by perf; this repository file persists only the metric definitions. The Neoverse V3 formulas combine stall, branch, cache, TLB, FP, SVE, and topdown events into percentages, MPKI values, and ratios; several topdown category rows are also referenced through `ArchStdEvent`.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias; malformed `MetricExpr`, stale event references, divide-by-zero denominators, or wrong scale units can make derived metrics invalid. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, metric parser coverage via `tools/perf/pmu-events/metric_test.py`, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/retired.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/retired.json

## Purpose
Lists 24 Arm architecture-standard event references for retired instruction and branch behavior on the Arm Neoverse V3 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 24 JSON records using `ArchStdEvent` references. It exports standard aliases `SW_INCR`, `INST_RETIRED`, `CID_WRITE_RETIRED`, `BR_IMMED_RETIRED`, `BR_RETURN_RETIRED`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, `BR_MIS_PRED_RETIRED`, `OP_RETIRED`, `BR_INDNR_TAKEN_RETIRED`, `BR_IMMED_PRED_RETIRED`, `BR_IMMED_MIS_PRED_RETIRED`, and 12 more. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/retired.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/spe.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/spe.json

## Purpose
Lists 10 Arm architecture-standard event references for statistical profiling extension sampling on the Arm Neoverse V3 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 10 JSON records using `ArchStdEvent` references. It exports standard aliases `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`, `SAMPLE_FEED_BR`, `SAMPLE_FEED_LD`, `SAMPLE_FEED_ST`, `SAMPLE_FEED_OP`, `SAMPLE_FEED_EVENT`, `SAMPLE_FEED_LAT`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/spe.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/spec_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/spec_operation.json

## Purpose
Lists 31 Arm architecture-standard event references for speculatively executed operation mix on the Arm Neoverse V3 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 31 JSON records using `ArchStdEvent` references. It exports standard aliases `BR_MIS_PRED`, `BR_PRED`, `INST_SPEC`, `OP_SPEC`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`, `LDREX_SPEC`, `STREX_PASS_SPEC`, `STREX_FAIL_SPEC`, `STREX_SPEC`, `LD_SPEC`, and 19 more. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/spec_operation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/stall.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/stall.json

## Purpose
Combines 23 Arm architecture-standard event references with 5 implementation-defined events for frontend/backend stall attribution on the Arm Neoverse V3 core model. The file lets perf expose both standardized aliases and model-specific counters from one topic table.

## APIs, Types, and Functions
The file has 28 JSON records using `ArchStdEvent` references, `EventName`/`EventCode` entries. It exports standard aliases `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`, `STALL_FRONTEND_MEMBOUND`, `STALL_FRONTEND_L1I`, `STALL_FRONTEND_MEM`, `STALL_FRONTEND_TLB`, `STALL_FRONTEND_CPUBOUND`, and 11 more; custom encodings `DISPATCH_STALL_IQ_SX` (`0x15C`), `DISPATCH_STALL_IQ_MX` (`0x15D`), `DISPATCH_STALL_IQ_LS` (`0x15E`), `DISPATCH_STALL_IQ_VX` (`0x15F`), `DISPATCH_STALL_MCQ` (`0x160`). `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias; wrong raw `EventCode` values produce misleading perf counts. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/stall.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/sve.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/sve.json

## Purpose
Lists 12 Arm architecture-standard event references for SVE operation and predicate behavior on the Arm Neoverse V3 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 12 JSON records using `ArchStdEvent` references. It exports standard aliases `SVE_INST_SPEC`, `SVE_PRED_SPEC`, `SVE_PRED_EMPTY_SPEC`, `SVE_PRED_FULL_SPEC`, `SVE_PRED_PARTIAL_SPEC`, `SVE_PRED_NOT_FULL_SPEC`, `SVE_LDFF_SPEC`, `SVE_LDFF_FAULT_SPEC`, `ASE_SVE_INT8_SPEC`, `ASE_SVE_INT16_SPEC`, `ASE_SVE_INT32_SPEC`, `ASE_SVE_INT64_SPEC`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/sve.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/tlb.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/tlb.json

## Purpose
Lists 34 Arm architecture-standard event references for TLB translation behavior on the Arm Neoverse V3 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 34 JSON records using `ArchStdEvent` references. It exports standard aliases `L1I_TLB_REFILL`, `L1D_TLB_REFILL`, `L1D_TLB`, `L1I_TLB`, `L2D_TLB_REFILL`, `L2D_TLB`, `DTLB_WALK`, `ITLB_WALK`, `L1D_TLB_REFILL_RD`, `L1D_TLB_REFILL_WR`, `L1D_TLB_RD`, `L1D_TLB_WR`, and 22 more. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, Arm Neoverse PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v3/tlb.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/cavium/thunderx2/core-imp-def.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/cavium/thunderx2/core-imp-def.json

## Purpose
Lists 37 Arm architecture-standard event references for core implementation-defined event selection on the Cavium ThunderX2 core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 37 JSON records using `ArchStdEvent` references. It exports standard aliases `L1D_CACHE_RD`, `L1D_CACHE_WR`, `L1D_CACHE_REFILL_RD`, `L1D_CACHE_REFILL_WR`, `L1D_CACHE_REFILL_INNER`, `L1D_CACHE_REFILL_OUTER`, `L1D_CACHE_WB_VICTIM`, `L1D_CACHE_WB_CLEAN`, `L1D_CACHE_INVAL`, `L1D_TLB_REFILL_RD`, `L1D_TLB_REFILL_WR`, `L1D_TLB_RD`, and 25 more. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/cavium/thunderx2/core-imp-def.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/common-and-microarch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/common-and-microarch.json

## Purpose
Defines the Arm64 architecture-wide event dictionary used when model files dereference standard events with `ArchStdEvent`. It contains 369 named `EventName`/`EventCode` records spanning base architectural counters, cache/TLB, stall, branch, SPE, SVE, FP, and Armv9-style microarchitectural extensions; the densest name families are SVE (54), ASE (51), L1D (29), FP (29), STALL (27), L1I (24), BR (22), L2D (21).

## APIs, Types, and Functions
This data file exports JSON objects with `EventName`, `EventCode`, `BriefDescription`, and sometimes `PublicDescription`. Early canonical entries include `SW_INCR`=`0x00`, `L1I_CACHE_REFILL`=`0x01`, `L1I_TLB_REFILL`=`0x02`, `L1D_CACHE_REFILL`=`0x03`, `L1D_CACHE`=`0x04`, `L1D_TLB_REFILL`=`0x05`, `LD_RETIRED`=`0x06`, `ST_RETIRED`=`0x07`; later entries include newer FP/SVE/ASE forms such as `FP_BF16_FIXED_MIN_OPS_SPEC`, `FP_FP8_FIXED_MIN_OPS_SPEC`, `FP_SP_SCALE_MIN_OPS_SPEC`, `FP_HP_SCALE_MIN_OPS_SPEC`, `FP_BF16_SCALE_MIN_OPS_SPEC`, `FP_FP8_SCALE_MIN_OPS_SPEC`. It is consumed as a lookup table by `tools/perf/pmu-events/jevents.py` when a model JSON names an `ArchStdEvent`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are wrong raw `EventCode` values produce misleading perf counts. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/common-and-microarch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mm/sys/ddrc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mm/sys/ddrc.json

## Purpose
Defines 5 model-specific PMU events for DDR controller PMU raw events on the NXP/Freescale SoC DDR uncore PMU model. These entries give perf symbolic names and raw event encodings for hardware behavior that is not represented solely by Arm architecture-standard events.

## APIs, Types, and Functions
The file has 5 JSON records using `EventName`/`EventCode` entries, `Unit` PMU selectors, `Compat` filters. It exports custom encodings `imx8mm_ddr.cycles` (`0x00`), `imx8mm_ddr.read_cycles` (`0x2a`), `imx8mm_ddr.write_cycles` (`0x2b`), `imx8mm_ddr.read` (`0x35`), `imx8mm_ddr.write` (`0x38`); unit(s) `imx8_ddr`; compat selector(s) `i.MX8MM`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx8_ddr`, compatible string `i.MX8MM`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are wrong raw `EventCode` values produce misleading perf counts; incorrect `Compat` values prevent uncore events from matching the target device. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mm/sys/ddrc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mm/sys/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mm/sys/metrics.json

## Purpose
Provides 2 derived perf metrics for the NXP/Freescale SoC DDR uncore PMU model, covering derived perf metrics. The entries expose user-facing `MetricName` aliases such as imx8mm_ddr_read.all, imx8mm_ddr_write.all and translate raw events into ratios, byte counts, percentages, or bandwidth utilization values.

## APIs, Types, and Functions
The exported API is declarative metric metadata: `MetricName`/`MetricExpr` formulas, `Unit` PMU selectors, `Compat` filters. Metric expressions are perf JSON formulas parsed by `metric.ParsePerfJson()` and may reference raw events, architecture-standard aliases, PMU filter syntax, and `duration_time`. Example metric names include `imx8mm_ddr_read.all`, `imx8mm_ddr_write.all`. Metric groups are not explicitly grouped.

## Control Flow, State, and Persistence
There is no executable control flow in the JSON itself. Build-time flow is: perf scans the architecture directory, loads this file, parses each `MetricExpr`, validates event/PMU references, then emits generated metric tables into `pmu-events.c`. Runtime state is limited to hardware counters sampled by perf; this repository file persists only the metric definitions. The i.MX8 metric formulas multiply DDR read/write cycle events by bus width factors, while i.MX9 formulas compose raw `imx9_ddr0@...@` filtered events, beat counts, and `duration_time` for bandwidth utilization.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx8_ddr`, compatible string `i.MX8MM`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are malformed `MetricExpr`, stale event references, divide-by-zero denominators, or wrong scale units can make derived metrics invalid; incorrect `Compat` values prevent uncore events from matching the target device; AXI mask/id filters are easy to transpose between SoC revisions. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, metric parser coverage via `tools/perf/pmu-events/metric_test.py`, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mm/sys/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mn/sys/ddrc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mn/sys/ddrc.json

## Purpose
Defines 5 model-specific PMU events for DDR controller PMU raw events on the NXP/Freescale SoC DDR uncore PMU model. These entries give perf symbolic names and raw event encodings for hardware behavior that is not represented solely by Arm architecture-standard events.

## APIs, Types, and Functions
The file has 5 JSON records using `EventName`/`EventCode` entries, `Unit` PMU selectors, `Compat` filters. It exports custom encodings `imx8mn_ddr.cycles` (`0x00`), `imx8mn_ddr.read_cycles` (`0x2a`), `imx8mn_ddr.write_cycles` (`0x2b`), `imx8mn_ddr.read` (`0x35`), `imx8mn_ddr.write` (`0x38`); unit(s) `imx8_ddr`; compat selector(s) `i.MX8MN`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx8_ddr`, compatible string `i.MX8MN`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are wrong raw `EventCode` values produce misleading perf counts; incorrect `Compat` values prevent uncore events from matching the target device. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mn/sys/ddrc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mn/sys/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mn/sys/metrics.json

## Purpose
Provides 2 derived perf metrics for the NXP/Freescale SoC DDR uncore PMU model, covering derived perf metrics. The entries expose user-facing `MetricName` aliases such as imx8mn_ddr_read.all, imx8mn_ddr_write.all and translate raw events into ratios, byte counts, percentages, or bandwidth utilization values.

## APIs, Types, and Functions
The exported API is declarative metric metadata: `MetricName`/`MetricExpr` formulas, `Unit` PMU selectors, `Compat` filters. Metric expressions are perf JSON formulas parsed by `metric.ParsePerfJson()` and may reference raw events, architecture-standard aliases, PMU filter syntax, and `duration_time`. Example metric names include `imx8mn_ddr_read.all`, `imx8mn_ddr_write.all`. Metric groups are not explicitly grouped.

## Control Flow, State, and Persistence
There is no executable control flow in the JSON itself. Build-time flow is: perf scans the architecture directory, loads this file, parses each `MetricExpr`, validates event/PMU references, then emits generated metric tables into `pmu-events.c`. Runtime state is limited to hardware counters sampled by perf; this repository file persists only the metric definitions. The i.MX8 metric formulas multiply DDR read/write cycle events by bus width factors, while i.MX9 formulas compose raw `imx9_ddr0@...@` filtered events, beat counts, and `duration_time` for bandwidth utilization.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx8_ddr`, compatible string `i.MX8MN`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are malformed `MetricExpr`, stale event references, divide-by-zero denominators, or wrong scale units can make derived metrics invalid; incorrect `Compat` values prevent uncore events from matching the target device; AXI mask/id filters are easy to transpose between SoC revisions. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, metric parser coverage via `tools/perf/pmu-events/metric_test.py`, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mn/sys/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mp/sys/ddrc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mp/sys/ddrc.json

## Purpose
Defines 5 model-specific PMU events for DDR controller PMU raw events on the NXP/Freescale SoC DDR uncore PMU model. These entries give perf symbolic names and raw event encodings for hardware behavior that is not represented solely by Arm architecture-standard events.

## APIs, Types, and Functions
The file has 5 JSON records using `EventName`/`EventCode` entries, `Unit` PMU selectors, `Compat` filters. It exports custom encodings `imx8mp_ddr.cycles` (`0x00`), `imx8mp_ddr.read_cycles` (`0x2a`), `imx8mp_ddr.write_cycles` (`0x2b`), `imx8mp_ddr.read` (`0x35`), `imx8mp_ddr.write` (`0x38`); unit(s) `imx8_ddr`; compat selector(s) `i.MX8MP`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx8_ddr`, compatible string `i.MX8MP`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are wrong raw `EventCode` values produce misleading perf counts; incorrect `Compat` values prevent uncore events from matching the target device. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mp/sys/ddrc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mp/sys/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mp/sys/metrics.json

## Purpose
Provides 58 derived perf metrics for the NXP/Freescale SoC DDR uncore PMU model, covering derived perf metrics. The entries expose user-facing `MetricName` aliases such as imx8mp_ddr_read.all, imx8mp_ddr_write.all, imx8mp_ddr_read.a53, imx8mp_ddr_write.a53, imx8mp_ddr_read.supermix, imx8mp_ddr_write.supermix, imx8mp_ddr_read.3d, imx8mp_ddr_write.3d, imx8mp_ddr_read.2d, imx8mp_ddr_write.2d, and 48 more and translate raw events into ratios, byte counts, percentages, or bandwidth utilization values.

## APIs, Types, and Functions
The exported API is declarative metric metadata: `MetricName`/`MetricExpr` formulas, `Unit` PMU selectors, `Compat` filters. Metric expressions are perf JSON formulas parsed by `metric.ParsePerfJson()` and may reference raw events, architecture-standard aliases, PMU filter syntax, and `duration_time`. Example metric names include `imx8mp_ddr_read.all`, `imx8mp_ddr_write.all`, `imx8mp_ddr_read.a53`, `imx8mp_ddr_write.a53`, `imx8mp_ddr_read.supermix`. Metric groups are not explicitly grouped.

## Control Flow, State, and Persistence
There is no executable control flow in the JSON itself. Build-time flow is: perf scans the architecture directory, loads this file, parses each `MetricExpr`, validates event/PMU references, then emits generated metric tables into `pmu-events.c`. Runtime state is limited to hardware counters sampled by perf; this repository file persists only the metric definitions. The i.MX8 metric formulas multiply DDR read/write cycle events by bus width factors, while i.MX9 formulas compose raw `imx9_ddr0@...@` filtered events, beat counts, and `duration_time` for bandwidth utilization.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx8_ddr`, compatible string `i.MX8MP`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are malformed `MetricExpr`, stale event references, divide-by-zero denominators, or wrong scale units can make derived metrics invalid; incorrect `Compat` values prevent uncore events from matching the target device; AXI mask/id filters are easy to transpose between SoC revisions. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, metric parser coverage via `tools/perf/pmu-events/metric_test.py`, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mp/sys/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mq/sys/ddrc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mq/sys/ddrc.json

## Purpose
Defines 5 model-specific PMU events for DDR controller PMU raw events on the NXP/Freescale SoC DDR uncore PMU model. These entries give perf symbolic names and raw event encodings for hardware behavior that is not represented solely by Arm architecture-standard events.

## APIs, Types, and Functions
The file has 5 JSON records using `EventName`/`EventCode` entries, `Unit` PMU selectors, `Compat` filters. It exports custom encodings `imx8mq_ddr.cycles` (`0x00`), `imx8mq_ddr.read_cycles` (`0x2a`), `imx8mq_ddr.write_cycles` (`0x2b`), `imx8mq_ddr.read` (`0x35`), `imx8mq_ddr.write` (`0x38`); unit(s) `imx8_ddr`; compat selector(s) `i.MX8MQ`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx8_ddr`, compatible string `i.MX8MQ`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are wrong raw `EventCode` values produce misleading perf counts; incorrect `Compat` values prevent uncore events from matching the target device. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mq/sys/ddrc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mq/sys/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mq/sys/metrics.json

## Purpose
Provides 2 derived perf metrics for the NXP/Freescale SoC DDR uncore PMU model, covering derived perf metrics. The entries expose user-facing `MetricName` aliases such as imx8mq_ddr_read.all, imx8mq_ddr_write.all and translate raw events into ratios, byte counts, percentages, or bandwidth utilization values.

## APIs, Types, and Functions
The exported API is declarative metric metadata: `MetricName`/`MetricExpr` formulas, `Unit` PMU selectors, `Compat` filters. Metric expressions are perf JSON formulas parsed by `metric.ParsePerfJson()` and may reference raw events, architecture-standard aliases, PMU filter syntax, and `duration_time`. Example metric names include `imx8mq_ddr_read.all`, `imx8mq_ddr_write.all`. Metric groups are not explicitly grouped.

## Control Flow, State, and Persistence
There is no executable control flow in the JSON itself. Build-time flow is: perf scans the architecture directory, loads this file, parses each `MetricExpr`, validates event/PMU references, then emits generated metric tables into `pmu-events.c`. Runtime state is limited to hardware counters sampled by perf; this repository file persists only the metric definitions. The i.MX8 metric formulas multiply DDR read/write cycle events by bus width factors, while i.MX9 formulas compose raw `imx9_ddr0@...@` filtered events, beat counts, and `duration_time` for bandwidth utilization.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx8_ddr`, compatible string `i.MX8MQ`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are malformed `MetricExpr`, stale event references, divide-by-zero denominators, or wrong scale units can make derived metrics invalid; incorrect `Compat` values prevent uncore events from matching the target device; AXI mask/id filters are easy to transpose between SoC revisions. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, metric parser coverage via `tools/perf/pmu-events/metric_test.py`, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx8mq/sys/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx91/sys/ddrc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx91/sys/ddrc.json

## Purpose
Defines 1 model-specific PMU events for DDR controller PMU raw events on the NXP/Freescale SoC DDR uncore PMU model. These entries give perf symbolic names and raw event encodings for hardware behavior that is not represented solely by Arm architecture-standard events.

## APIs, Types, and Functions
The file has 1 JSON records using `EventName`/`EventCode` entries, `Unit` PMU selectors, `Compat` filters. It exports custom encodings `imx91_ddr.cycles` (`0x00`); unit(s) `imx9_ddr`; compat selector(s) `imx91`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx9_ddr`, compatible string `imx91`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are wrong raw `EventCode` values produce misleading perf counts; incorrect `Compat` values prevent uncore events from matching the target device. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx91/sys/ddrc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx91/sys/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx91/sys/metrics.json

## Purpose
Provides 3 derived perf metrics for the NXP/Freescale SoC DDR uncore PMU model, covering derived perf metrics. The entries expose user-facing `MetricName` aliases such as imx91_bandwidth_usage.lpddr4, imx91_ddr_read.all, imx91_ddr_write.all and translate raw events into ratios, byte counts, percentages, or bandwidth utilization values.

## APIs, Types, and Functions
The exported API is declarative metric metadata: `MetricName`/`MetricExpr` formulas, `Unit` PMU selectors, `Compat` filters. Metric expressions are perf JSON formulas parsed by `metric.ParsePerfJson()` and may reference raw events, architecture-standard aliases, PMU filter syntax, and `duration_time`. Example metric names include `imx91_bandwidth_usage.lpddr4`, `imx91_ddr_read.all`, `imx91_ddr_write.all`. Metric groups are not explicitly grouped.

## Control Flow, State, and Persistence
There is no executable control flow in the JSON itself. Build-time flow is: perf scans the architecture directory, loads this file, parses each `MetricExpr`, validates event/PMU references, then emits generated metric tables into `pmu-events.c`. Runtime state is limited to hardware counters sampled by perf; this repository file persists only the metric definitions. The i.MX8 metric formulas multiply DDR read/write cycle events by bus width factors, while i.MX9 formulas compose raw `imx9_ddr0@...@` filtered events, beat counts, and `duration_time` for bandwidth utilization.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx9_ddr`, compatible string `imx91`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are malformed `MetricExpr`, stale event references, divide-by-zero denominators, or wrong scale units can make derived metrics invalid; incorrect `Compat` values prevent uncore events from matching the target device; AXI mask/id filters are easy to transpose between SoC revisions. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, metric parser coverage via `tools/perf/pmu-events/metric_test.py`, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx91/sys/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx93/sys/ddrc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx93/sys/ddrc.json

## Purpose
Defines 1 model-specific PMU events for DDR controller PMU raw events on the NXP/Freescale SoC DDR uncore PMU model. These entries give perf symbolic names and raw event encodings for hardware behavior that is not represented solely by Arm architecture-standard events.

## APIs, Types, and Functions
The file has 1 JSON records using `EventName`/`EventCode` entries, `Unit` PMU selectors, `Compat` filters. It exports custom encodings `imx93_ddr.cycles` (`0x00`); unit(s) `imx9_ddr`; compat selector(s) `imx93`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx9_ddr`, compatible string `imx93`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are wrong raw `EventCode` values produce misleading perf counts; incorrect `Compat` values prevent uncore events from matching the target device. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx93/sys/ddrc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx93/sys/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx93/sys/metrics.json

## Purpose
Provides 3 derived perf metrics for the NXP/Freescale SoC DDR uncore PMU model, covering derived perf metrics. The entries expose user-facing `MetricName` aliases such as imx93_bandwidth_usage.lpddr4x, imx93_ddr_read.all, imx93_ddr_write.all and translate raw events into ratios, byte counts, percentages, or bandwidth utilization values.

## APIs, Types, and Functions
The exported API is declarative metric metadata: `MetricName`/`MetricExpr` formulas, `Unit` PMU selectors, `Compat` filters. Metric expressions are perf JSON formulas parsed by `metric.ParsePerfJson()` and may reference raw events, architecture-standard aliases, PMU filter syntax, and `duration_time`. Example metric names include `imx93_bandwidth_usage.lpddr4x`, `imx93_ddr_read.all`, `imx93_ddr_write.all`. Metric groups are not explicitly grouped.

## Control Flow, State, and Persistence
There is no executable control flow in the JSON itself. Build-time flow is: perf scans the architecture directory, loads this file, parses each `MetricExpr`, validates event/PMU references, then emits generated metric tables into `pmu-events.c`. Runtime state is limited to hardware counters sampled by perf; this repository file persists only the metric definitions. The i.MX8 metric formulas multiply DDR read/write cycle events by bus width factors, while i.MX9 formulas compose raw `imx9_ddr0@...@` filtered events, beat counts, and `duration_time` for bandwidth utilization.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx9_ddr`, compatible string `imx93`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are malformed `MetricExpr`, stale event references, divide-by-zero denominators, or wrong scale units can make derived metrics invalid; incorrect `Compat` values prevent uncore events from matching the target device; AXI mask/id filters are easy to transpose between SoC revisions. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, metric parser coverage via `tools/perf/pmu-events/metric_test.py`, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx93/sys/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx94/sys/ddrc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx94/sys/ddrc.json

## Purpose
Defines 1 model-specific PMU events for DDR controller PMU raw events on the NXP/Freescale SoC DDR uncore PMU model. These entries give perf symbolic names and raw event encodings for hardware behavior that is not represented solely by Arm architecture-standard events.

## APIs, Types, and Functions
The file has 1 JSON records using `EventName`/`EventCode` entries, `Unit` PMU selectors, `Compat` filters. It exports custom encodings `imx94_ddr.cycles` (`0x00`); unit(s) `imx9_ddr`; compat selector(s) `imx94`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx9_ddr`, compatible string `imx94`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are wrong raw `EventCode` values produce misleading perf counts; incorrect `Compat` values prevent uncore events from matching the target device. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx94/sys/ddrc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx94/sys/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx94/sys/metrics.json

## Purpose
Provides 56 derived perf metrics for the NXP/Freescale SoC DDR uncore PMU model, covering derived perf metrics. The entries expose user-facing `MetricName` aliases such as imx94_bandwidth_usage.lpddr5, imx94_bandwidth_usage.lpddr4, imx94_ddr_read.all, imx94_ddr_write.all, imx94_ddr_read.a55_all, imx94_ddr_write.a55_all, imx94_ddr_read.a55_0, imx94_ddr_write.a55_0, imx94_ddr_read.a55_1, imx94_ddr_write.a55_1, and 46 more and translate raw events into ratios, byte counts, percentages, or bandwidth utilization values.

## APIs, Types, and Functions
The exported API is declarative metric metadata: `MetricName`/`MetricExpr` formulas, `Unit` PMU selectors, `Compat` filters. Metric expressions are perf JSON formulas parsed by `metric.ParsePerfJson()` and may reference raw events, architecture-standard aliases, PMU filter syntax, and `duration_time`. Example metric names include `imx94_bandwidth_usage.lpddr5`, `imx94_bandwidth_usage.lpddr4`, `imx94_ddr_read.all`, `imx94_ddr_write.all`, `imx94_ddr_read.a55_all`. Metric groups are not explicitly grouped.

## Control Flow, State, and Persistence
There is no executable control flow in the JSON itself. Build-time flow is: perf scans the architecture directory, loads this file, parses each `MetricExpr`, validates event/PMU references, then emits generated metric tables into `pmu-events.c`. Runtime state is limited to hardware counters sampled by perf; this repository file persists only the metric definitions. The i.MX8 metric formulas multiply DDR read/write cycle events by bus width factors, while i.MX9 formulas compose raw `imx9_ddr0@...@` filtered events, beat counts, and `duration_time` for bandwidth utilization.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx9_ddr`, compatible string `imx94`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are malformed `MetricExpr`, stale event references, divide-by-zero denominators, or wrong scale units can make derived metrics invalid; incorrect `Compat` values prevent uncore events from matching the target device; AXI mask/id filters are easy to transpose between SoC revisions. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, metric parser coverage via `tools/perf/pmu-events/metric_test.py`, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx94/sys/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx95/sys/ddrc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx95/sys/ddrc.json

## Purpose
Defines 1 model-specific PMU events for DDR controller PMU raw events on the NXP/Freescale SoC DDR uncore PMU model. These entries give perf symbolic names and raw event encodings for hardware behavior that is not represented solely by Arm architecture-standard events.

## APIs, Types, and Functions
The file has 1 JSON records using `EventName`/`EventCode` entries, `Unit` PMU selectors, `Compat` filters. It exports custom encodings `imx95_ddr.cycles` (`0x00`); unit(s) `imx9_ddr`; compat selector(s) `imx95`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx9_ddr`, compatible string `imx95`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are wrong raw `EventCode` values produce misleading perf counts; incorrect `Compat` values prevent uncore events from matching the target device. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx95/sys/ddrc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx95/sys/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx95/sys/metrics.json

## Purpose
Provides 110 derived perf metrics for the NXP/Freescale SoC DDR uncore PMU model, covering derived perf metrics. The entries expose user-facing `MetricName` aliases such as imx95_bandwidth_usage.lpddr5, imx95_bandwidth_usage.lpddr4x, imx95_ddr_read.all, imx95_ddr_write.all, imx95_ddr_read.a55_all, imx95_ddr_write.a55_all_1, imx95_ddr_write.a55_all_2, imx95_ddr_read.a55_0, imx95_ddr_write.a55_0, imx95_ddr_read.a55_1, and 100 more and translate raw events into ratios, byte counts, percentages, or bandwidth utilization values.

## APIs, Types, and Functions
The exported API is declarative metric metadata: `MetricName`/`MetricExpr` formulas, `Unit` PMU selectors, `Compat` filters. Metric expressions are perf JSON formulas parsed by `metric.ParsePerfJson()` and may reference raw events, architecture-standard aliases, PMU filter syntax, and `duration_time`. Example metric names include `imx95_bandwidth_usage.lpddr5`, `imx95_bandwidth_usage.lpddr4x`, `imx95_ddr_read.all`, `imx95_ddr_write.all`, `imx95_ddr_read.a55_all`. Metric groups are not explicitly grouped.

## Control Flow, State, and Persistence
There is no executable control flow in the JSON itself. Build-time flow is: perf scans the architecture directory, loads this file, parses each `MetricExpr`, validates event/PMU references, then emits generated metric tables into `pmu-events.c`. Runtime state is limited to hardware counters sampled by perf; this repository file persists only the metric definitions. The i.MX8 metric formulas multiply DDR read/write cycle events by bus width factors, while i.MX9 formulas compose raw `imx9_ddr0@...@` filtered events, beat counts, and `duration_time` for bandwidth utilization.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, kernel PMU driver exposing `imx9_ddr`, compatible string `imx95`, i.MX DDR controller uncore PMU filter syntax. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are malformed `MetricExpr`, stale event references, divide-by-zero denominators, or wrong scale units can make derived metrics invalid; incorrect `Compat` values prevent uncore events from matching the target device; AXI mask/id filters are easy to transpose between SoC revisions. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, metric parser coverage via `tools/perf/pmu-events/metric_test.py`, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/freescale/imx95/sys/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/branch.json

## Purpose
Lists 2 Arm architecture-standard event references for branch prediction events on the Fujitsu A64FX core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 2 JSON records using `ArchStdEvent` references. It exports standard aliases `BR_MIS_PRED`, `BR_PRED`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, A64FX PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias; A64FX CMG-local semantics and energy-per-cycle events need hardware-side validation. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/bus.json

## Purpose
Defines 10 model-specific PMU events for bus and interconnect traffic on the Fujitsu A64FX core model. These entries give perf symbolic names and raw event encodings for hardware behavior that is not represented solely by Arm architecture-standard events.

## APIs, Types, and Functions
The file has 10 JSON records using `EventName`/`EventCode` entries. It exports custom encodings `BUS_READ_TOTAL_TOFU` (`0x314`), `BUS_READ_TOTAL_PCI` (`0x315`), `BUS_READ_TOTAL_MEM` (`0x316`), `BUS_WRITE_TOTAL_CMG0` (`0x318`), `BUS_WRITE_TOTAL_CMG1` (`0x319`), `BUS_WRITE_TOTAL_CMG2` (`0x31A`), `BUS_WRITE_TOTAL_CMG3` (`0x31B`), `BUS_WRITE_TOTAL_TOFU` (`0x31C`), 2 more. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, A64FX PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are wrong raw `EventCode` values produce misleading perf counts; A64FX CMG-local semantics and energy-per-cycle events need hardware-side validation. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/cache.json

## Purpose
Combines 14 Arm architecture-standard event references with 14 implementation-defined events for cache and TLB events on the Fujitsu A64FX core model. The file lets perf expose both standardized aliases and model-specific counters from one topic table.

## APIs, Types, and Functions
The file has 28 JSON records using `ArchStdEvent` references, `EventName`/`EventCode` entries. It exports standard aliases `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_TLB_REFILL`, `L2I_TLB_REFILL`, and 2 more; custom encodings `L1D_CACHE_REFILL_PRF` (`0x49`), `L2D_CACHE_REFILL_PRF` (`0x59`), `L1D_CACHE_REFILL_DM` (`0x200`), `L1D_CACHE_REFILL_HWPRF` (`0x202`), `L1_MISS_WAIT` (`0x208`), `L1I_MISS_WAIT` (`0x209`), `L2D_CACHE_REFILL_DM` (`0x300`), `L2D_CACHE_REFILL_HWPRF` (`0x302`), 6 more. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, A64FX PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias; wrong raw `EventCode` values produce misleading perf counts; A64FX CMG-local semantics and energy-per-cycle events need hardware-side validation. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/cycle.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/cycle.json

## Purpose
Lists 1 Arm architecture-standard event references for cycle accounting on the Fujitsu A64FX core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 1 JSON records using `ArchStdEvent` references. It exports standard aliases `CPU_CYCLES`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, A64FX PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias; A64FX CMG-local semantics and energy-per-cycle events need hardware-side validation. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/cycle.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/exception.json

## Purpose
Lists 9 Arm architecture-standard event references for exception and trap accounting on the Fujitsu A64FX core model. The file is a topic-specific allowlist: each `ArchStdEvent` is resolved against the Arm64 shared event dictionary during perf PMU event generation.

## APIs, Types, and Functions
The file has 9 JSON records using `ArchStdEvent` references. It exports standard aliases `EXC_TAKEN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, `EXC_SMC`, `EXC_HVC`. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, A64FX PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias; A64FX CMG-local semantics and energy-per-cycle events need hardware-side validation. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/instruction.json

## Purpose
Combines 21 Arm architecture-standard event references with 11 implementation-defined events for instruction and operation mix on the Fujitsu A64FX core model. The file lets perf expose both standardized aliases and model-specific counters from one topic table.

## APIs, Types, and Functions
The file has 32 JSON records using `ArchStdEvent` references, `EventName`/`EventCode` entries. It exports standard aliases `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, `LDREX_SPEC`, `STREX_SPEC`, `LD_SPEC`, `ST_SPEC`, `LDST_SPEC`, `DP_SPEC`, `ASE_SPEC`, and 9 more; custom encodings `DCZVA_SPEC` (`0x9F`), `FP_MV_SPEC` (`0x105`), `PRD_SPEC` (`0x108`), `IEL_SPEC` (`0x109`), `IREG_SPEC` (`0x10A`), `FP_LD_SPEC` (`0x112`), `FP_ST_SPEC` (`0x113`), `BC_LD_SPEC` (`0x11A`), 3 more. `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, `arch/arm64/common-and-microarch.json`, A64FX PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are an `ArchStdEvent` typo or missing common-dictionary entry breaks generation or silently removes an alias; wrong raw `EventCode` values produce misleading perf counts; A64FX CMG-local semantics and energy-per-cycle events need hardware-side validation. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/memory.json

## Purpose
Defines 1 model-specific PMU events for memory access and alignment behavior on the Fujitsu A64FX core model. These entries give perf symbolic names and raw event encodings for hardware behavior that is not represented solely by Arm architecture-standard events.

## APIs, Types, and Functions
The file has 1 JSON records using `EventName`/`EventCode` entries. It exports custom encodings `EA_MEMORY` (`0x3E8`). `jevents.py` lowers these objects into generated `struct pmu_event` records, with `EventCode` converted to perf event config strings and `ArchStdEvent` expanded from `common-and-microarch.json`.

## Control Flow, State, and Persistence
There is no mutable state or runtime control flow in the file. Build-time control flow is data-driven: `jevents.py` discovers the JSON, resolves any `ArchStdEvent` through the Arm64 common dictionary, canonicalizes event codes, and emits generated C tables. At runtime perf selects the table through `arch/arm64/mapfile.csv` and exposes aliases through `perf list`/`perf stat`; the source JSON itself is persistent configuration.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, `arch/arm64/mapfile.csv`, A64FX PMU event semantics. The generated tables are linked into perf before runtime, then selected for matching CPUs or uncore devices so users can request these symbols by name rather than raw event numbers.

## Risks and Test Signals
Primary risks are wrong raw `EventCode` values produce misleading perf counts; A64FX CMG-local semantics and energy-per-cycle events need hardware-side validation. Useful test signals are JSON parsing with `json.load`, perf `jevents.py` generation, `perf list` alias visibility, hardware `perf stat` smoke tests on the named CPU/SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/a64fx/memory.json -->
