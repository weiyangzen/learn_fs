## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat.sh

Purpose: broad functional suite for `perf stat` command behavior beyond output-format linting.
Important functions: `test_default_stat`, `test_null_stat`, `find_offline_cpu`, `test_offline_cpu_stat`, `test_stat_record_report`, `test_stat_record_script`, `test_stat_repeat_weak_groups`, `test_topdown_groups`, `test_topdown_weak_groups`, `test_cputype`, `test_hybrid`, `test_stat_cpu`, `test_stat_no_aggr`, `test_stat_detailed`, `test_stat_repeat`, and `test_stat_pid`.
Control flow: runs stat subcommands and parser scenarios, checks output strings, exercises offline CPU handling, stat record/report/script pipes, topdown event reordering, CPU type filtering, hybrid default cycles, CPU list/range handling, detailed output, repeats, and PID attach.
State and persistence: one temp output file and a short-lived `sleep` PID are managed.
Dependencies and integration: reads CPU sysfs online/topology and PMU devices; uses perf stat/report/script and parser behavior.
Risks: hardware event availability and permission settings can make some checks fail rather than skip; topdown/raw encodings are platform-sensitive.
Test signals: expected stat headers, parser diagnostics, CPU columns, variance output, and event names.
