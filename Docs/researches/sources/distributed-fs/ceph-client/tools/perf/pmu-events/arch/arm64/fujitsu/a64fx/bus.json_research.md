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
