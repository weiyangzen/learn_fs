# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestMetricsCache.java

## Purpose
Tests `MetricsCache` record update, lookup, tag retention, null-tag handling, metric instance retention, and overflow eviction.

## Important APIs, Types, And Functions
Uses `MetricsCache.update()`, `update(record, true)`, `get()`, `Record.metrics()`, `Record.tags()`, `getMetric()`, `getMetricInstance()`, and `MAX_RECS_PER_NAME_DEFAULT`. Helpers mock `MetricsRecord`, `MetricsTag`, and `AbstractMetric`.

## Control Flow
`testUpdate()` inserts a record, updates same name/tags with new and old metrics, then inserts same name with different tag value and verifies a separate record. `testGet()` checks empty and populated lookup. `testNullTag()` validates hash/key behavior with null tag values. `testOverflow()` inserts one more record than the per-name max and checks the oldest entry is evicted.

## State And Persistence Behavior
Cache state is in-memory and indexed by record name plus tag set. Metrics persist across updates for a record unless overwritten. Tags are only stored in cached records when requested.

## Dependencies And Integration Points
Supports sink implementations that need latest metrics by source/tag identity. Depends on metrics2 interned metadata helpers and Mockito.

## Risks
Incorrect tag equality/hash behavior can merge or lose records. Overflow eviction can silently drop old tag combinations. By default tags are not retained unless `update(..., true)` is used.

## Test Signals
Signals include metric `m` updating from 0 to 2 while `m1` remains, new `m2`, separate record for tag value `tv3`, null tag retrieval, and eviction of the first tag set after max+1 inserts.
