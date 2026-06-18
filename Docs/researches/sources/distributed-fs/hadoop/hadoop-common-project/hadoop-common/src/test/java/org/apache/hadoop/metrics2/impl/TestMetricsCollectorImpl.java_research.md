# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsCollectorImpl.java

## Purpose

`TestMetricsCollectorImpl` validates metrics collector filtering at record and per-metric levels.

## Important APIs, Types, And Functions

The tests use `MetricsCollectorImpl`, `MetricsRecordBuilderImpl`, `setRecordFilter()`, `setMetricFilter()`, `ConfigBuilder`, and filter factory helpers from `TestPatternFilter`.

## Control Flow

`recordBuilderShouldNoOpIfFiltered()` configures a record exclude filter for `foo`, adds a record named `foo`, tries to add a tag and gauge, and asserts the builder has no tags, no metrics, no record, and the collector has no records. `testPerMetricFiltering()` sets a metric exclude filter for `foo`, adds a tag, a counter `c0`, and a gauge `foo`, then asserts only the tag and counter remain.

## State And Persistence Behavior

State is in the collector, builder, and filter objects. No persistence is involved.

## Dependencies And Integration Points

It integrates metrics2 collector/builder internals with glob filter semantics. It depends on `TestPatternFilter` helpers for consistent filter initialization.

## Risks And Test Signals

Risks include filtered record builders accidentally retaining data, metric filters applying to tags, or filtered metrics still appearing in records. Signals are exact tag/metric list sizes, null record assertion, and collector record count.
