## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/GlobFilter.java

Purpose: Public filter that interprets configured include/exclude strings as Hadoop glob patterns.

Important APIs/types/functions: Overrides `compile(String)` to use `GlobPattern.compile`.

Control flow: All accept/reject behavior is inherited from `AbstractPatternFilter`.

State and persistence: Only inherited compiled patterns after initialization.

Dependencies/integration: Useful in metrics configuration where operators prefer glob syntax for source, record, metric, or tag filters.

Risks/test signals: Glob-to-regex conversion should be tested for common wildcard patterns, tag filters, and include-only mode.
