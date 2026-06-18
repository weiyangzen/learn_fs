# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/thead/c900-legacy/firmware.json

## Purpose
This JSON file is a architecture-standard alias table for `thead/c900-legacy` under the `riscv` perf PMU event tree. It provides model-local references to RISC-V architecture standard firmware events declared in the architecture root. It contains 22 entries and belongs to the `firmware` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `ArchStdEvent`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: FW_MISALIGNED_LOAD, FW_MISALIGNED_STORE, FW_ACCESS_LOAD, FW_ACCESS_STORE, FW_ILLEGAL_INSN, FW_SET_TIMER, FW_IPI_SENT, FW_IPI_RECEIVED, FW_FENCE_I_SENT, FW_FENCE_I_RECEIVED.
- `ArchStdEvent` is a dereference key, not a standalone event definition; generation resolves it against architecture standard events by `EventName`.

## Content Notes
- The file contains 22 bare `ArchStdEvent` references; descriptions and config codes are inherited from the RISC-V root standard firmware table.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is architecture-standard resolution: the local entry names a firmware standard event, and the generator copies the canonical root definition into the model table.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.
- `jevents.py` resolves each `ArchStdEvent` through architecture-root standard events by matching `EventName`

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Every reference must match an architecture-root standard event; a typo fails at generation or silently drops expected firmware aliases depending on validation path.
- These model files intentionally duplicate the same SBI firmware reference list; consistency with `riscv-sbi-firmware.json` matters more than local descriptions.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Check every `ArchStdEvent` resolves to a root RISC-V standard event by `EventName`.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
