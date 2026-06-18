## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/AbstractPatternFilter.java

Purpose: Shared base for include/exclude metrics filters backed by compiled name and tag patterns.

Important APIs/types/functions: Config keys are `include`, `exclude`, `include.tags`, and `exclude.tags`. `init` compiles patterns; `accepts(MetricsTag)`, `accepts(Iterable<MetricsTag>)`, and `accepts(String)` implement whitelist/blacklist logic. Subclasses provide `compile(String)`.

Control flow: Includes win first, excludes reject next, and include-only mode rejects nonmatching inputs. Tag pattern entries must match `name:pattern`.

State and persistence: Stores compiled RE2/J `Pattern` objects in maps and fields; in-memory only.

Dependencies/integration: Loaded from `MetricsConfig` as source, record, and metric filters. `GlobFilter` and `RegexFilter` only differ in pattern compilation.

Risks/test signals: Tag syntax errors throw `MetricsException`; include-only semantics are easy to regress. Tests should cover single-tag and iterable-tag paths.
