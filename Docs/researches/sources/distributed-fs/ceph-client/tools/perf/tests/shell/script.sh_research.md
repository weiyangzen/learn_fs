## sources/distributed-fs/ceph-client/tools/perf/tests/shell/script.sh

Purpose: tests Python DB-export mode and `parallel-perf.py` integration for `perf script`.
Important functions: `test_db` and `test_parallel_perf`.
Control flow: DB test skips when Python scripting support is off, creates a temporary Python script with `perf_db_export_*` flags and callbacks, records `true`, and runs `perf script -s`. Parallel test records `uname` with sample CPU and runs `scripts/python/parallel-perf.py` in regular and per-CPU modes.
State and persistence: temp directory contains perf.data, generated script, and parallel output directories; cleanup removes it.
Dependencies and integration: depends on perf Python scripting, ASAN leak suppression, source-tree script path, and Python 3 for parallel-perf.
Risks: generated callback has a malformed-looking print string but only command success is checked; parallel-perf path differs between installed and source builds.
Test signals: command completion for script DB export and parallel processing.
