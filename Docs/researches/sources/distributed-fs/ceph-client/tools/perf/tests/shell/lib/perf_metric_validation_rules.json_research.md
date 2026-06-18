<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_metric_validation_rules.json -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_metric_validation_rules.json

## Purpose

This JSON file provides base skip lists and metric validation rules consumed by `perf_metric_validation.py`.

## Research

Top-level `SkipList` names metrics excluded from validation, including TSX cycle metrics, package/core residency metrics, and selected TMA false-sharing/remote-cache/contention metrics. `RelationshipRules` define indexed rules with `Formula`, `TestType`, lower/upper ranges, error thresholds, descriptions, and metric/alias lists. Rules validate PMEM and DDR read+write bandwidth totals, NUMA local+remote read percentages, CPI lower bound, ratio metrics in `[0,1]`, TMA level 1 summing to 100%, TMA level 2 children equaling parents, memory page request percentages summing to 100%, CPU utilization relationships, L2/LLC miss-per-instruction relationships, and broad frequency ranges for uncore and CPU operating frequency. State is static validation policy only. Dependencies are exact lowercase metric names emitted by perf metric catalogs and the validator's simple alias/formula grammar. Risks include stale metric names, hardware-specific metrics absent on many systems, tolerance too tight for noisy counters, and rule descriptions carrying product-specific assumptions. Test signal is that supported rules generated from this file pass on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/perf_metric_validation_rules.json -->
