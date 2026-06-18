<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pmu-events.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/pmu-events.c

## Purpose

This large selftest validates generated PMU event and metric tables, alias creation for core and uncore PMUs, and parseability/evaluability of metric expressions and thresholds.

## Research

Static `perf_pmu_test_event` fixtures describe expected core, uncore, and sys events. `compare_pmu_events` and `compare_alias_to_test_event` compare generated table fields and runtime alias fields. `test__pmu_event_table` finds test tables and iterates events with callbacks. Alias tests instantiate fake `perf_pmu` objects, add CPU/sys aliases, and verify event lookup for core PMUs, named uncore PMUs, PMU ids, compat regexes, and hyphenated names. Metric tests use `metricgroup__parse_groups_test`, allocate fake stats, assign values, and evaluate expressions; fake parsing separately extracts ids from metric formulas, parses ids using fake PMUs, and evaluates with synthetic values. Threshold parsing walks all core and sys metrics. State is all heap-local fake PMUs, evlists, stats, expr contexts, and generated tables. Dependencies include `pmu-events`, `metricgroup`, `expr`, `parse-events`, and test architecture tables. Risks include fixture drift after JSON schema changes, special handling for intentionally broken metrics `M1/M2/M3`, divide-by-zero workarounds, and alias matching across heterogeneous PMU names. Test signals are field-for-field event equality, alias counts, and zero metric parse failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pmu-events.c -->
