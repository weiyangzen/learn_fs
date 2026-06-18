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
