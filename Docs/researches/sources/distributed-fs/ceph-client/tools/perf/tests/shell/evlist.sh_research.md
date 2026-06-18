<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/evlist.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/evlist.sh

## Purpose

This shell test validates `perf evlist` for simple events, grouped events, and verbose event configuration.

## Research

`test_evlist_simple` records `cpu-clock` for `true` and checks `perf evlist -i` lists it. `test_evlist_group` records `{cpu-clock,task-clock}` against `perf test -w noploop`, skips on record failure, and requires `perf evlist -g` to show both events in group braces. `test_evlist_verbose` records `cycles` and checks `perf evlist -v` contains `config:`. State is one temporary perf.data file reused across cases. Dependencies are perf record/evlist, software and hardware event availability, grouping support, and the `noploop` workload. Risks include hardware `cycles` permission failure, group record skipped silently, and regex assumptions around grouping output. Passing signal is all non-skipped checks finding expected text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/evlist.sh -->
