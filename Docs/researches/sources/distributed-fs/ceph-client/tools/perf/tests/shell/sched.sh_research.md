## sources/distributed-fs/ceph-client/tools/perf/tests/shell/sched.sh

Purpose: tests core `perf sched` record, latency, script, map, and timehist commands.
Important functions: `start_noploops`, `cleanup_noploops`, `test_sched_record`, `test_sched_latency`, `test_sched_script`, `test_sched_map`, and `test_sched_timehist`.
Control flow: requires root, starts two `noploop` workloads pinned to CPU0, records scheduler events for one second, kills workloads, then verifies each report mode mentions `perf-noploop`.
State and persistence: temp perf.data and two background PIDs are managed by cleanup.
Dependencies and integration: requires taskset, scheduler tracepoints, perf workload `noploop`, and root.
Risks: assumes CPU0 affinity can be set; workload cleanup must run to avoid stale processes.
Test signals: `perf-noploop` appears in all sched output modes.
