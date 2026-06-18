<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/metric_test.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/metric_test.py
Purpose: Unit tests for `metric.py` expression behavior. It documents the expected string forms and rewrite semantics that PMU metric generators rely on.

Important APIs/types/functions: `TestMetricExpressions` tests `Event`, `MetricRef`, `Constant`, `Select`, `d_ratio`, `min`, `max`, `source_count`, `has_event`, `JsonEncodeMetric`, `ParsePerfJson`, `ToPython`, `Simplify`, and `RewriteMetricsInTermsOfOthers`.

Control flow: Each test builds expressions, compares `str()`/`ToPerfJson()` output, parses perf JSON strings back into expression objects, and validates simplified or substituted expressions. The substitution test creates same-PMU metric tuples and checks that expressions can be shortened using earlier metric definitions.

State and persistence: Tests run in process and depend on `metric` globals being permissive when no event JSON was loaded. No files are read or written by the tests themselves.

Dependencies and integration points: Uses Python `unittest` and the local `metric` module. It is a guard for `intel_metrics.py` and `jevents.py` because both depend on expression serialization and parsing.

Risks: Coverage is focused on expression mechanics, not full PMU model JSON. It does not exercise every escaping corner or event validation path with loaded event files.

Test signals: Passing this test suite is a direct signal that metric AST precedence, ternary conversion, Python reconstruction, constant simplification, and cross-metric rewrite behavior remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/metric_test.py -->
