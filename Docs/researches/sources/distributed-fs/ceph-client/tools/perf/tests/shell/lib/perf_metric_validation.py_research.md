<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_metric_validation.py -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_metric_validation.py

## Purpose

This Python framework validates perf metrics numerically by collecting `perf stat -j -M` results, generating supported rules, checking positive values, single-metric bounds, and relationships among related metrics.

## Research

`TestError` formats missing, out-of-range, and relationship errors. `Validator` loads base rules, discovers metrics from `perf list -j --details metrics`, filters by CPU type, collects metric values through `_run_perf`, converts JSON stderr records into lowercase metric-name values, and stores per-workload results. `pos_val_test` checks nonnegative metrics and reruns a small failing set on a longer workload. `single_test` applies lower/upper/tolerance bounds per metric, also with rerun. `relationship_test` maps aliases, evaluates simple formulas with `+ - * /`, resolves bounds that may reference other metrics, and records failures. `create_rules` merges JSON relationship rules with an auto-generated percentage rule for metrics whose scale unit is `1%` or `100%`; unsupported/skipped metrics are removed. `test` iterates workloads, collects data, applies all rules, prints counts, optionally writes debug JSON, and exits nonzero when errors exist. State includes collected results, skip/ignore sets, output JSON files, and repeated system-wide perf runs. Dependencies are perf metric names/schema, JSON output on stderr, system-wide stat permission, and rule JSON. Risks include formula parser limitations, likely bug using `alias[ub]` while resolving lower-bound aliases, missing `sys` import in `read_json` error path until main imports it, command splitting of workloads by whitespace, and negative values from short workloads causing false errors. Test signals are total/passed counts and empty `errlist`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_metric_validation.py -->
