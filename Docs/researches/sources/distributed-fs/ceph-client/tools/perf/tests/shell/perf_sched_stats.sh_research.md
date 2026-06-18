## sources/distributed-fs/ceph-client/tools/perf/tests/shell/perf_sched_stats.sh

Purpose: validates `perf sched stats` record, report, live, and diff subcommands.
Important functions: `test_perf_sched_stats_record`, `test_perf_sched_stats_report`, `test_perf_sched_stats_live`, and `test_perf_sched_stats_diff`.
Control flow: requires root, records scheduler stats to one or two temp files, checks record output, report/live `Description` output, and diff command success.
State and persistence: two temp perf.data paths and `.old` companions are removed on cleanup.
Dependencies and integration: depends on scheduler trace infrastructure and root permissions.
Risks: checks for literal output strings; format changes may require test updates. Live mode depends on available scheduler events.
Test signals: each subtest updates `err`; final exit is accumulated success/failure.
