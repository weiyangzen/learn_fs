## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+shadow_stat.sh

Purpose: verifies derived `insn_per_cycle` shadow-stat metric values against raw instruction/cycle counts.
Important functions: `test_global_aggr` and `test_no_aggr`.
Control flow: skips if system-wide stat is forbidden or hybrid CPU output is detected, then runs global and per-CPU `perf stat -M insn_per_cycle`, recalculates IPC with awk, and fails if difference exceeds `THRESHOLD=0.015`.
State and persistence: no files.
Dependencies and integration: needs cycles/instructions counts, system-wide permissions, and non-hybrid output assumptions.
Risks: parsing depends on text columns and metric rounding; not-counted events are skipped line-by-line.
Test signals: computed IPC matches printed IPC within tolerance for aggregate and no-aggregate modes.
