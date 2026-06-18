## sources/distributed-fs/ceph-client/tools/perf/tests/shell/timechart.sh

Purpose: smoke test for `perf timechart record` and SVG generation.
Important function: `test_timechart`.
Control flow: skips if libtraceevent is missing, tries `perf timechart record -o perfdata true`, then runs `perf timechart -i perfdata -o output.svg` and checks the file is non-empty and contains `svg`.
State and persistence: temp perf.data and SVG output are cleaned.
Dependencies and integration: timechart tracepoints, libtraceevent, SVG output path.
Risks: record failures are treated as skipped inside the test function without setting `err`; permissions and tracepoint availability dominate.
Test signals: generated non-empty SVG-looking file.
