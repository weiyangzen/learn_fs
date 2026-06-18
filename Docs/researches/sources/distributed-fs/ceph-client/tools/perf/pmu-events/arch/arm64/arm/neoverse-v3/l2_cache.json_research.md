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
