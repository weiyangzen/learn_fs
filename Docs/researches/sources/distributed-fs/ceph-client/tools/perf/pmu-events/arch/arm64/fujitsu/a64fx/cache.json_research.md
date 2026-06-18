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
