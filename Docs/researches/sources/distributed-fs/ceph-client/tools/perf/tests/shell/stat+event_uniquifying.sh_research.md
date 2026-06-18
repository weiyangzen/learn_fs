## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+event_uniquifying.sh

Purpose: checks that deduplicated PMU event names are uniquified in `perf stat` output when duplicate PMU instances exist.
Important function: `test_event_uniquifying`.
Control flow: compares `perf list --raw pmu` with verbose raw PMU listing, strips numeric PMU suffixes from verbose-only events, runs `perf stat -e "$event" -A`, and requires output to mention the non-deduplicated PMU event name.
State and persistence: temp stat output file is removed.
Dependencies and integration: relies on PMU sysfs metadata and perf list/stat behavior.
Risks: no duplicate PMUs means no assertions; command failures are converted to skip if no prior hard failure occurred.
Test signals: uniquified verbose PMU event appears in stat output.
