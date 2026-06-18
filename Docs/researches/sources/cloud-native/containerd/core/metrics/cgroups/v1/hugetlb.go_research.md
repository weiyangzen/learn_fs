# sources/cloud-native/containerd/core/metrics/cgroups/v1/hugetlb.go

Purpose: declares cgroup v1 hugetlb metrics for usage, fail count, and maximum usage per hugepage size.

Important APIs and data: `hugetlbMetrics` produces `hugetlb_usage`, `hugetlb_failcnt`, and `hugetlb_max`, each labeled by `page`.

Control flow: metric functions return nil when `stats.Hugetlb` is absent, otherwise iterate the hugetlb stat slice and emit one value per page size.

State and persistence: no state; descriptor data is consumed by the v1 collector.

Dependencies and integration: depends on v1 metrics aliases, Docker metrics units, and Prometheus gauges.

Risks: page-size labels add cardinality proportional to configured hugepage sizes. Units differ between bytes and total counts and must remain consistent with descriptor names.

Test signals: no direct tests in subset.
