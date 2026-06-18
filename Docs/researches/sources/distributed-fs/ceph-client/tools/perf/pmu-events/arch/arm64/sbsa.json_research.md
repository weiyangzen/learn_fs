# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/sbsa.json

## Purpose
This 4-entry Arm64 metric file defines SBSA topdown level-1 metrics: `frontend_bound`, `bad_speculation`, `retiring`, and `backend_bound`. These formulas express percentages of total slots using common Arm counters such as stall slots, branch mispredictions, operation retirement, CPU cycles, and `#slots`.

## Important Data Fields
Each row uses `MetricExpr`, `BriefDescription`, `DefaultMetricgroupName`, `MetricGroup`, `MetricName`, and `ScaleUnit`. The formulas use lower-case event aliases and perf metric constants, for example `100 * (stall_slot_backend / (#slots * cpu_cycles))`.

## Control Flow And Integration
`jevents.py` parses `MetricExpr` through the perf metric parser and emits generated metric tables. Runtime consumers include `perf stat -M` and Python metric export paths that expose `MetricName`, `MetricExpr`, `ScaleUnit`, and descriptions.

## State, Dependencies, Risks, And Tests
The file is static; runtime persistence is limited to generated perf objects. Dependencies are the availability and naming of the referenced Arm64 events, plus parser support for `#slots`. Risks include division by zero, formula drift when event aliases change, and CPU models that map SBSA metrics without the full counter set. Test signals include metric parser tests, `perf list --metrics`, and `perf stat -M TopdownL1` on SBSA-capable hardware.
