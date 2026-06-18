# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/MetricsLists.java

## Purpose

`MetricsLists` is a tiny package-private helper that creates metrics lists for tests through the real `MetricsCollectorImpl`/`MetricsRecordBuilderImpl` path.

## Important APIs, Types, And Functions

It exposes `static MetricsRecordBuilderImpl builder(String name)`, which returns `new MetricsCollectorImpl().addRecord(name)`.

## Control Flow

Callers obtain a record builder, add counters/gauges through normal builder APIs, and then read `.metrics()` from the builder. This avoids hand-constructing metric implementation lists.

## State And Persistence Behavior

All state is in the newly allocated collector and builder. There is no persistence or static cache.

## Dependencies And Integration Points

The helper is used by tests such as `TestMetricsSystemImpl` and `TestMetricsVisitor` to construct expected metric lists with the same concrete metric classes as production code.

## Risks And Test Signals

The risk is small but important: if builder behavior changes, expected metric construction changes with it and may hide some regressions. Its signal value is consistency with production builder output for equality/visitor tests.
