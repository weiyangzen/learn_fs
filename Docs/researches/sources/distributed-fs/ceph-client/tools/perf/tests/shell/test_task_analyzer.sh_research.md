## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_task_analyzer.sh

Purpose: exercises `perf script report task-analyzer` output modes and CSV exports.
Important functions: `report`, `check_exec_0`, `find_str_or_fail`, `skip_no_probe_record_support`, `prepare_perf_data`, and test cases for basic, namespace/rename, milliseconds/filter/highlight, extended times, summaries, CSV, and CSV summary.
Control flow: records sched_switch system-wide for one second to `perf.data` in CWD, then runs task-analyzer variants and greps required headers/fields.
State and persistence: uses `perf.data` in current directory plus a temp output directory; cleanup removes both.
Dependencies and integration: libtraceevent, Python script report infrastructure, sched tracepoints, and ASAN leak suppression.
Risks: fixed `perf.data` name can collide with user files if run in an unsafe directory; output header strings are format-sensitive.
Test signals: expected labels like `Comm`, `Out-Out`, `Summary`, and CSV semicolon headers.
