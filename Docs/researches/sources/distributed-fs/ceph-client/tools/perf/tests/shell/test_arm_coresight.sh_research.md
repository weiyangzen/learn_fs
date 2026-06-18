## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_coresight.sh

Purpose: exclusive Arm CoreSight ETM trace recording and synthesized sample validation.
Important functions: `skip_if_no_cs_etm_event`, `record_touch_file`, `perf_script_branch_samples`, `perf_report_branch_samples`, `perf_report_instruction_samples`, `is_device_sink`, `arm_cs_iterate_devices`, `arm_cs_etm_traverse_path_test`, `arm_cs_etm_system_wide_test`, `arm_cs_etm_snapshot_test`, `arm_cs_etm_basic_test`, and sparse CPU tests.
Control flow: skips without `cs_etm//`, traverses CoreSight sysfs connections to test each sink, records system-wide, snapshot, per-thread/system-wide/normal timestamp variants, and sparse CPU lists.
State and persistence: temp perf.data and touched file are cleaned; global `glb_err` accumulates failures.
Dependencies and integration: CoreSight PMU sysfs, taskset, trace decode, perf script/report itrace.
Risks: hardware topology traversal is sysfs-name sensitive; snapshot timing and sink support can vary.
Test signals: branch samples in script/report and instruction samples in report for expected command names.
