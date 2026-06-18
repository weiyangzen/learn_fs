# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/StreamStatisticNames.java

Purpose: public constant catalog for stream-level statistics, especially input-stream read, seek, vectored read, policy, and leak metrics.

Important APIs, types, and functions: declares string constants such as stream leaks, aborted/closed reads, bytes read/discarded, read operations, seek counts and bytes, vectored read counters, and stream policy metrics.

Control flow: no executable flow beyond private constructor. Constants are referenced by stream implementations and audit/span code as stable operation names.

State and persistence: no runtime state. Constant string values are part of the public evolving metrics contract.

Dependencies and integration points: depends on Hadoop annotations. Integrates filesystem stream implementations with IOStatistics and monitoring.

Risks and test signals: typo or duplicate names can fragment metrics. Tests should cover literal compatibility, uniqueness, and expected counters being registered by stream stores.
