## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_spe.sh

Purpose: exclusive Arm SPE trace recording validation for snapshot, system-wide, and discard mode.
Important functions: `skip_if_no_arm_spe_event`, `arm_spe_report`, `perf_script_samples`, `perf_report_samples`, `arm_spe_snapshot_test`, `arm_spe_system_wide_test`, and `arm_spe_discard_test`.
Control flow: skips without `arm_spe_*//`, records snapshot and system-wide traces of `dd`, validates synthesized memory/cache/TLB/branch events in script/report, and tests discard mode by ensuring no AUX/AUXTRACE data remains.
State and persistence: temp perf.data is cleaned; `glb_err` accumulates failures.
Dependencies and integration: Arm SPE PMUs, taskset for discard CPU targeting, perf report/script synthesis.
Risks: event names in `events` regex must track `arm-spe.c`; discard support is optional per PMU instance.
Test signals: synthesized SPE samples present or absent according to mode.
