# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/common/common/tool.json

## Purpose
This 14-entry common file defines perf tool-provided pseudo-events and constants, including `duration_time`, `user_time`, `system_time`, persistent-memory presence, CPU/core/package topology values, `slots`, SMT state, TSC frequency, `core_wide`, and `target_cpu`.

## Important Data Fields
Rows use `Unit` set to `tool`, `EventName`, `BriefDescription`, and `ConfigCode`. Unlike raw hardware PMU events, these names are supplied by perf/tooling context and are often used as metric formula inputs.

## Control Flow And Integration
`jevents.py` maps the `tool` unit into generated metadata. Runtime metric evaluation resolves these pseudo-events/constants when evaluating expressions in common, Arm64, and vendor metric files, for example `duration_time` in bandwidth metrics and `#slots`/`slots` in topdown calculations.

## State, Dependencies, Risks, And Tests
The file is static schema input, but values are populated at runtime by perf. Risks include breaking metric formulas by renaming tool values, config-code drift, topology values being unavailable in some collection modes, and confusion between event-like counters and constants. Test signals include metric parser tests, `perf list tool`, and metrics that exercise `duration_time`, topology, and target-mode predicates.
