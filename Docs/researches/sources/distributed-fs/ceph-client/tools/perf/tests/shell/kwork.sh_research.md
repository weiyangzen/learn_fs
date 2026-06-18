<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/kwork.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/kwork.sh

## Purpose

This root-only shell test validates `perf kwork` record, report, latency, timehist, and top modes.

## Research

The script skips without root because tracing events are required. `test_kwork_record` records one second of kernel work data to a temp file. `test_kwork_report` requires `Kwork Name`; `test_kwork_latency` requires `Avg delay`; `test_kwork_timehist` requires `Kwork name`; and `test_kwork_top` requires `COMMAND`. State is temporary perf data and `.old` cleanup. Dependencies are tracing permissions, kwork command support, tracepoints for workqueue/irq/softirq style events, and sufficient kernel activity during `sleep 1`. Risks include root-only execution, low activity causing sparse output, output header wording changes, and tracefs conflicts. Passing signal is each subcommand producing its expected header text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/kwork.sh -->
