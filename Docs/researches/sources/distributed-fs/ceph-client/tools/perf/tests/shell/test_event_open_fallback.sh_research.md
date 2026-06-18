## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_event_open_fallback.sh

Purpose: tests perf's fallback behavior when opening events with high precise-IP requirements.
Important functions: `perf_record`, `test_decrease_precise_ip`, `test_decrease_precise_ip_complicated`, and `count_result`.
Control flow: records `cycles` and then `cycles:P`, expecting precision to decrease if needed; for systems with `mem-loads-aux`, records a grouped precise memory event combination.
State and persistence: no files; records to `/dev/null`.
Dependencies and integration: event parser/open fallback logic and PMU precise event support.
Risks: script calls `cleanup` near the end but no cleanup function is defined in this file, so if execution reaches that line in strict shells it may fail unless provided by environment; this is a maintenance risk.
Test signals: at least one subtest passes, otherwise all skip; any fallback failure exits `1`.
