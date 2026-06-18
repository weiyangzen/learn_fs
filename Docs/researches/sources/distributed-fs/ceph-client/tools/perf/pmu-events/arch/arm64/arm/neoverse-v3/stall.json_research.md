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
