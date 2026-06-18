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
