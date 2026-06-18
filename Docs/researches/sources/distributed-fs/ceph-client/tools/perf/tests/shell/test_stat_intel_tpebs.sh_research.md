## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_stat_intel_tpebs.sh

Purpose: tests Intel TPEBS counting mode through `perf stat --record-tpebs`.
Important functions: `ParanoidAndNotRoot` and `test_with_record_tpebs`.
Control flow: skips non-Intel, non-root with paranoid restrictions, and missing precise `cache-misses` support; then runs `perf stat -e cache-misses:R --record-tpebs -a sleep 0.01` and checks output for embedded perf record messages and event name.
State and persistence: temp stat output is removed.
Dependencies and integration: Intel precise event support, system-wide stat, and TPEBS record integration.
Risks: event name may print as either `cache-misses:R` or PMU slash form; permissions heavily gate coverage.
Test signals: output contains `perf record` and the requested retired precise event.
