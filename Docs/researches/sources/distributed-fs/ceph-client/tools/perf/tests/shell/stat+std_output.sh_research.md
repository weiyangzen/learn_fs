## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+std_output.sh

Purpose: lints default human-readable `perf stat` output for known default event names and associated metric names.
Important function: caller-defined `commachecker`, backed by `stat_output.sh` mode runners.
Control flow: after each shared stat invocation, skips comments/headers/elapsed time, strips aggregation prefixes, validates event names against `event_name[]`, and validates metric labels against `event_metric[]` unless ignored topdown metrics match `skip_metric[]`.
State and persistence: temp stat output file is removed.
Dependencies and integration: exercises standard output for default stat modes, topology-driven aggregations, and metric-only mode.
Risks: tight coupling to output text and default event set; metric-only check returns on first nonempty line rather than validating all metrics.
Test signals: all parsed lines have expected event/metric names; topology-restricted modes skip cleanly.
