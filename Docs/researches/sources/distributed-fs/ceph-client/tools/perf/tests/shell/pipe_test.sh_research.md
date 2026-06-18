## sources/distributed-fs/ceph-client/tools/perf/tests/shell/pipe_test.sh

Purpose: validates perf.data pipe mode across `perf record`, `perf report`, and `perf inject` build-id paths.
Important functions: `test_record_report` and `test_inject_bids`.
Control flow: requires `noploop` symbol, records `perf test -w noploop` to stdout and files, reports from `-` and temp files, and repeats inject tests for `-B`, `-b`, `--buildid-all`, and `--mmap2-buildid-all`.
State and persistence: two temp perf.data files plus `.old` companions are removed.
Dependencies and integration: uses `lib/perf_has_symbol.sh`, task-clock user event, report symbol resolution, and build-id injection.
Risks: symbol visibility and architecture-specific workload arguments affect reliability; pipe failures may be hard to diagnose because most commands are pipelines.
Test signals: report output must include `perf` in task view and `noploop` after inject/report paths.
