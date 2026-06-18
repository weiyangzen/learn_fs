# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/pmc.json

## Purpose
This JSON file is a PMU event table for `power9` under the `powerpc` perf PMU event tree. It provides topic-scoped raw event aliases for powerpc power9 `pmc` counters. It contains 23 entries and belongs to the `pmc` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x10026..0x4f148.
- Representative names: PM_BR_2PATH, PM_MEM_LOC_THRESH_LSU_HIGH, PM_MRK_DCACHE_RELOAD_INTV, PM_MRK_DPTEG_FROM_DL2L3_MOD, PM_THRESH_EXC_64, PM_DPTEG_FROM_L3MISS, PM_SYS_PUMP_MPRED_RTY, PM_MRK_DPTEG_FROM_L2MISS, PM_CMPLU_STALL_BRU, PM_4FLOP_CMPL.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- Power9 `pmc` contributes IBM PMU event mnemonics such as PM_BR_2PATH, PM_MEM_LOC_THRESH_LSU_HIGH, PM_MRK_DCACHE_RELOAD_INTV, PM_MRK_DPTEG_FROM_DL2L3_MOD, PM_THRESH_EXC_64, PM_DPTEG_FROM_L3MISS, PM_SYS_PUMP_MPRED_RTY, PM_MRK_DPTEG_FROM_L2MISS.
- The file focuses on PMC-threshold and marked-event samples, including pump retry and memory locality threshold signals.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/powerpc/mapfile.csv maps PVR 0x004e... to the power9 directory as core PMU events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Power event names are uppercase IBM PMU mnemonics; tests should preserve case and hex strings because user-facing perf aliases are generated from them.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
