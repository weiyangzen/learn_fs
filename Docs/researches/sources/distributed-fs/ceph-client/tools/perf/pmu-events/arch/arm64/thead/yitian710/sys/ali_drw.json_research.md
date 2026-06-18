# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/thead/yitian710/sys/ali_drw.json

## Purpose
This 53-entry Yitian 710 system PMU table describes Alibaba DDR read/write controller events for the `ali_drw` unit. It covers HIF read/write/rmw traffic, DFI data cycles, critical read/write transactions, DRAM commands, precharge/refresh/power-state transitions, hazards, visible-window limits, CHI traffic, and DDR cycles.

## Important Data Fields
Rows use `BriefDescription`, `ConfigCode`, `EventName`, `Unit`, and `Compat`. `Unit` is consistently `ali_drw`, while `Compat` is `ali_drw_pmu`; `jevents.py` maps this unit into an uncore PMU name. Event encodings range from `0x0` for `hif_rd_or_wr` to `0x80` for `ddr_cycles`.

## Control Flow And Integration
The Arm64 mapfile selects the broader Yitian 710 directory for the CPU, and this system PMU file contributes uncore event aliases. At runtime, perf PMU matching uses the `Unit`/`Compat` data with uncore name matching, including wildcard or suffix-insensitive paths in `perf_pmu__name_wildcard_match` and `perf_pmu__name_no_suffix_match`.

## State, Dependencies, Risks, And Tests
The file is declarative state. It depends on the kernel exposing an `ali_drw_pmu`-compatible PMU and on the hardware interpreting `ConfigCode` values as documented. Risks include PMU-name mismatch, unit scaling errors for 64B transactions, and metric breakage if `hif_rd`, `hif_wr`, `hif_rmw`, or `duration_time` aliases are absent. Test signals include JSON validation, generated alias inspection, `perf list ali_drw`, and bandwidth sanity checks under memory-copy workloads.
