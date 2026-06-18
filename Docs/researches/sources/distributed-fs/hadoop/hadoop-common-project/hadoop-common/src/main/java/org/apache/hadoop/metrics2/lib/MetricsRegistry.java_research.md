## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsRegistry.java

Purpose: Public helper registry for tags and mutable metrics, making metrics source implementations concise.

Important APIs/types/functions: Creates counters, gauges, quantiles, inverse quantiles, stats, rates, aggregated rates, and rolling averages. Supports `add(name,value)` default rate creation, context/tag registration, metric/tag lookup, and `snapshot`.

Control flow: Creation methods validate duplicate and whitespace names, instantiate mutable metric types, and add them to ordered maps. `snapshot` writes tags first then calls each mutable metric snapshot. Tag overrides are explicit.

State and persistence: Synchronized `LinkedHashMap`-style maps preserve insertion order for metrics and tags. Mutable metrics retain their own counters/statistics. In-memory only.

Dependencies/integration: Used by source classes, metrics system self metrics, sink adapter stats, and annotation factory. Uses `Interns`, mutable metric classes, and `MsInfo`.

Risks/test signals: Duplicate name rejection, whitespace validation, dynamic default rates, tag override semantics, and snapshot ordering are important. Quantile metrics schedule background tasks and should be stopped by owners when appropriate.
