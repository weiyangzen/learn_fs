<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/metric.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/metric.py
Purpose: Provides the Python expression and metric model used to generate perf metric JSON. It validates event names against loaded PMU JSON, builds an expression tree with operator overloading, serializes/deserializes perf metric expressions, and emits `Metric`/`MetricGroup` dictionaries.

Important APIs/types/functions: `LoadEvents`, `CheckPmu`, `CheckEvent`, `CheckEveryEvent`, and `IsExperimentalEvent` maintain global validation sets. `MetricConstraint` mirrors perf grouping constraints. The expression hierarchy is `Expression`, `Operator`, `Select`, `Function`, `Event`, `MetricRef`, `Constant`, and `Literal`, with helpers `min`, `max`, `d_ratio`, `source_count`, `has_event`, and `strcmp_cpuid_str`. `Metric` and `MetricGroup` represent output records and group descriptions. `ParsePerfJson` parses perf metric expressions into the Python AST model, and `RewriteMetricsInTermsOfOthers` substitutes same-PMU metrics to shorten formulas.

Control flow: Generator scripts create `Event` and expression objects through overloaded arithmetic and comparison operators. Each expression can simplify itself, serialize to perf JSON, serialize to Python reconstructors, test equality, and substitute subexpressions. `ParsePerfJson` rewrites token-like strings into `Event(...)` calls, fixes literals/keywords, transforms Python ternary syntax into `Select`, then evaluates the restricted expression using this module's constructors.

State and persistence: Validation state is held in module globals: `all_pmus`, `all_events`, `experimental_events`, and `all_events_all_models`. The module reads JSON files but writes no files. `Metric` construction mutates descriptions to mark experimental-event use and normalizes scale units.

Dependencies and integration points: Used by `intel_metrics.py`, `jevents.py`, and tests. It depends on Python `ast`, `decimal`, `json`, `os`, and `re`. Its serialized dictionaries become the PMU metric JSON that perf's C parser consumes.

Risks: `ParsePerfJson` uses `eval` after regex rewriting; it is intended for trusted repository JSON, not untrusted input. Simplification uses arithmetic on `Constant` string objects in paths that rely on `__str__` coercion, so operator coverage should be tested carefully. Global validation changes behavior depending on whether `LoadEvents` was called. Escaping around commas, equals signs, slashes, and metric literals is delicate.

Test signals: `metric_test.py` covers operator serialization, bracket precedence, JSON parsing, ternary rewriting, Python round-tripping, simplification, and metric-expression substitution. Additional signals are successful PMU event generation and perf metric parsing in compiled perf.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/metric.py -->
