<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_report/test_basic.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_report/test_basic.sh

## Purpose

This perf-report test validates help text, basic stdio report output, sample-count and CPU-utilization columns, header metadata, filtering, latency report layout, and parallelism sorting.

## Research

The script sources common init and consumes `perf.data` plus `perf.data.1` produced by setup. Optional help validation checks major manual sections and option names. Basic report checks total lost samples, sample header, table header, and kernel symbol rows while whitelisting stderr. Further cases validate `--show-nr-samples`, `--header-only` fields, header timestamp stability after tar/xz round-trip, `--showcpuutilization`, `--pid=1`, empty output for a nonexistent symbol, substring symbol filtering, context-switch flag in latency profile headers, default versus `--latency` column ordering, and `--hierarchy --sort latency,parallelism,comm,symbol --parallelism=1,2`. State is report logs, tarred perf.data copy, and header extraction dir. Dependencies are kernel symbols, environment variables from common settings, xz/tar, and regex helpers. Risks include distro init naming, kernel symbol availability, host CPU count differences, and output format churn. Test signal is strict pattern acceptance for each report mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_report/test_basic.sh -->
