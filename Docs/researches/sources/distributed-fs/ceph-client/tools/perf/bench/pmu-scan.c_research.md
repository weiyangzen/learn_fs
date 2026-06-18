# Research: sources/distributed-fs/ceph-client/tools/perf/bench/pmu-scan.c

Purpose: benchmarks perf PMU sysfs scanning for core-only and all-PMU scans while verifying consistency of discovered PMU metadata.

Important APIs/types/functions: `bench_pmu_scan()` parses options. `save_result()` performs a baseline `perf_pmus__scan()` and stores PMU name, alias count, format count, caps count, and core flag. `check_result()` rescans and compares current data to baseline. `run_pmu_scan()` times repeated `perf_pmus__scan_core()` and `perf_pmus__scan()` calls.

Control flow: save baseline, then run two phases: core-only and all PMUs. Each iteration times scan, checks results, destroys PMU cache, and updates stats. Finally prints average scan time and frees baseline.

State and persistence: static `results` array and `nr_pmus` hold baseline metadata. No persistent files; reads sysfs PMU hierarchy.

Dependencies and integration: depends on perf PMU cache/scanning APIs, list traversal of PMU format entries, stats, parse-options, and debug output.

Risks: baseline can become stale if PMU sysfs changes during the run. The same stats object is reused across core/all phases without reinitialization between phases, so second reported average includes prior samples. Allocation failure in `strdup()` is not explicitly checked.

Test signals: systems with only core PMUs and with uncore/software PMUs, varied iteration counts, hotplug/sysfs changes, and intentional PMU cache destroy/rebuild correctness.
