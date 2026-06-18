# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z15/basic.json

## Purpose
This JSON file is a PMU event table for `cf_z15` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z15 `basic` counters. It contains 8 entries and belongs to the `basic` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x0..0x21; Units: CPU-M-CF.
- Representative names: CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z15 `basic` table exposes s390 counter facility aliases such as CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
