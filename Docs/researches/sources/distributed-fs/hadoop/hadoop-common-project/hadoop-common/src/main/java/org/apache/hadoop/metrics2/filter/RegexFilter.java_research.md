## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/filter/RegexFilter.java

Purpose: Public filter that interprets include/exclude configuration strings as regular expressions.

Important APIs/types/functions: Overrides `compile(String)` using RE2/J `Pattern.compile`.

Control flow: Inherits pattern acceptance ordering from `AbstractPatternFilter`.

State and persistence: Inherited compiled pattern fields and tag-pattern maps.

Dependencies/integration: Instantiated by `MetricsConfig.getFilter` for regex filter class names.

Risks/test signals: Invalid regex syntax fails during initialization. Tests should cover full-match behavior because `matcher(...).matches()` is used rather than find/contains.
