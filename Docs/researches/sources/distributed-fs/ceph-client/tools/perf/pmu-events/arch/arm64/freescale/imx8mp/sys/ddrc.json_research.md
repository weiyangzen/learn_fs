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
