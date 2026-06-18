# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/package-info.java

Purpose: package documentation for Hadoop IOStatistics, explaining the statistics model, naming rules, aggregation behavior, and thread-level context support.

Important APIs, types, and functions: documents statistic categories (counters, gauges, minimums, maximums, means), naming restrictions, serializable snapshots, aggregators, and thread-level collection concepts.

Control flow: no executable flow. It guides how package APIs should be used and extended.

State and persistence: no runtime state. Documentation describes which objects are serializable and how snapshots should be treated as persisted values.

Dependencies and integration points: applies Hadoop public/evolving annotations to `org.apache.hadoop.fs.statistics`. It is the high-level contract for filesystem authors and metrics consumers.

Risks and test signals: documentation drift can cause incompatible metrics additions or misunderstanding of aggregation semantics. Test signals include API docs generation and tests that enforce documented naming/aggregation expectations.
