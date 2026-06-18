# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/andes/ax45/microarch.json

## Purpose
This JSON file is a PMU event table for `andes/ax45` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv andes/ax45 `microarch` counters. It contains 15 entries and belongs to the `microarch` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x2..0x161.
- Representative names: cycle_wait_icache_fill, cycle_wait_dcache_fill, uncached_ifetch_from_bus, uncached_load_from_bus, cycle_wait_uncached_ifetch, cycle_wait_uncached_load, main_itlb_access, main_itlb_miss, main_dtlb_access, main_dtlb_miss.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The andes/ax45 `microarch` table defines model-specific aliases such as cycle_wait_icache_fill, cycle_wait_dcache_fill, uncached_ifetch_from_bus, uncached_load_from_bus, cycle_wait_uncached_ifetch, cycle_wait_uncached_load, main_itlb_access, main_itlb_miss.
- Andes AX45 events use lower-case event aliases and encode cache, TLB, bus, unaligned-access, branch, and retire class counters.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
