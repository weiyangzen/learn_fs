# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/legacy-hardware.json

## Purpose
This 14-entry common table maps traditional perf hardware event aliases such as `cpu-cycles`, `instructions`, `cache-misses`, `branches`, `branch-misses`, frontend/backend stalled cycles, and `ref-cycles` to legacy hardware config codes. It preserves the familiar cross-architecture perf event names.

## Important Data Fields
Rows use `EventName`, `BriefDescription`, and `LegacyConfigCode`. `jevents.py` converts `LegacyConfigCode` into generated `legacy-hardware-config=<value>` event strings rather than ordinary raw PMU event encodings.

## Control Flow And Integration
This common file is included in the generated common PMU event tables and backs perf aliases used by user commands and metric formulas. It integrates with generic metrics in `arch/common/common/metrics.json`, which reference names like `instructions`, `cycles`, and cache miss events.

## State, Dependencies, Risks, And Tests
The file is stable declarative state with very broad consumers. Risks are severe for compatibility: renaming aliases, changing config codes, or altering descriptions can break existing commands, scripts, and metrics across architectures. Test signals include generated event validation, `perf list` for legacy aliases, `perf stat -e cycles,instructions`, and parser tests for formulas that depend on these aliases.
