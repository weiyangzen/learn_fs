<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/MetricsCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/MetricsCache.java

## Purpose
`MetricsCache` stores the latest values for metrics records, mainly for sinks that need dense updates even when the metrics system supplies sparse records.

## Important APIs and Types
The public APIs are constructors, `update(MetricsRecord)`, `update(MetricsRecord, boolean includingTags)`, and `get(name, tags)`. Nested `Record` exposes tag lookup, metric value lookup, metric instance lookup, tag entry sets, deprecated numeric metrics, and current metric entry sets. Nested `RecordCache` is an LRU-like `LinkedHashMap` capped by `maxRecsPerName`.

## Control Flow
`update` looks up a cache by record name, creates it if absent, then looks up a `Record` by the record's tag collection. It stores or overwrites metrics by metric name and optionally copies tags by tag name. `RecordCache.removeEldestEntry` drops the eldest entry once the per-name limit is exceeded and logs the first overflow.

## State and Persistence
All state is in memory. The top-level map grows by record name; each record name is bounded by `maxRecsPerName`, but metric names inside each record are not independently bounded.

## Dependencies and Integration Points
Ganglia dense mode uses this cache. Other sinks can use it when their backend expects full record schemas.

## Risks and Test Signals
The key uses `Collection<MetricsTag>` equality and therefore depends on tag collection equality/order semantics. The class is not synchronized. Tests should cover sparse-to-dense merging, includingTags behavior, per-record eviction, overflow logging, deprecated `metrics()` values, and lookup by equivalent tag collections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/MetricsCache.java -->
