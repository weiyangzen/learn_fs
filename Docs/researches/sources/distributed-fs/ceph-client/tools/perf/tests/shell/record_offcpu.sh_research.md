## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_offcpu.sh

Purpose: validates `perf record --off-cpu` profiling, child accounting, and threshold behavior.
Important functions: `test_offcpu_priv`, `test_offcpu_basic`, `test_offcpu_child`, `test_offcpu_above_thresh`, and `test_offcpu_below_thresh`.
Control flow: requires root and BPF skeleton support, records off-CPU samples for `sleep` and `perf bench sched messaging`, verifies `offcpu-time` event/report output, then uses timestamp windows to distinguish direct samples above threshold from at-end samples below threshold.
State and persistence: one temp perf.data file and `.old` file are cleaned.
Dependencies and integration: requires BPF skeletons, dummy event, offcpu-time synthetic event, report/script time filtering, and scheduler blocking workload.
Risks: timestamp constants rely on OFF_CPU_TIMESTAMP encoding; timing thresholds can be sensitive on slow systems.
Test signals: `perf evlist` contains `offcpu-time`, report includes `sleep`, child sample count exceeds expected process count, and direct/at-end sample windows match thresholds.
