# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/translation.json

## Purpose
This JSON file is a PMU event table for `power9` under the `powerpc` perf PMU event tree. It provides topic-scoped raw event aliases for powerpc power9 `translation` counters. It contains 45 entries and belongs to the `translation` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x1e..0x4e05c.
- Representative names: PM_CYC, PM_PMC2_OVERFLOW, PM_DATA_FROM_L21_SHR, PM_DP_QP_FLOP_CMPL, PM_DPTEG_FROM_DMEM, PM_ST_FIN, PM_IPTEG_FROM_RL2L3_SHR, PM_MRK_LSU_FIN, PM_CMPLU_STALL_VFXU, PM_LSU_FIN.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- Power9 `translation` contributes IBM PMU event mnemonics such as PM_CYC, PM_PMC2_OVERFLOW, PM_DATA_FROM_L21_SHR, PM_DP_QP_FLOP_CMPL, PM_DPTEG_FROM_DMEM, PM_ST_FIN, PM_IPTEG_FROM_RL2L3_SHR, PM_MRK_LSU_FIN.
- The file emphasizes translation/data-source aliases, including PM_CYC and LSU/IPTEG/DPTEG source events used for memory hierarchy attribution.
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
