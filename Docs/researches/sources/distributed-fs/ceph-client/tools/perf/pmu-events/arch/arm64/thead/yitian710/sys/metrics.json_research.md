# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/thead/yitian710/sys/metrics.json

## Purpose
This 2-entry Yitian 710 system PMU metrics file derives DDR read and write bandwidth metrics for the `ali_drw` PMU. `ddr_read_bandwidth.all` uses `hif_rd * 64 / 1e6 / duration_time`; `ddr_write_bandwidth.all` uses `(hif_wr + hif_rmw) * 64 / 1e6 / duration_time`.

## Important Data Fields
Each metric has `MetricName`, `BriefDescription`, `MetricGroup`, `MetricExpr`, `ScaleUnit`, `Unit`, and `Compat`. The formulas rely on `ali_drw.json` event aliases and the common tool event `duration_time`.

## Control Flow And Integration
`jevents.py` parses these expressions, keeps `Compat` and `Unit`, and emits metric rows associated with the ali_drw PMU. Runtime perf metric listing and `perf stat -M ali_drw` style use depend on PMU matching and event availability.

## State, Dependencies, Risks, And Tests
The file is static metric metadata. Dependencies are the `hif_*` events, correct 64-byte transaction semantics, `duration_time`, and the kernel PMU compatibility string. Risks include unit mistakes because `duration_time` is nanoseconds while the formula divides by `1e6`, zero-duration edge cases, and inaccurate bandwidth if events count transactions differently than assumed. Test signals are metric parser checks and comparison against external memory-bandwidth tools.
