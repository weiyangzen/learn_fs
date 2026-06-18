# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMetricsRegistry.java

## Purpose

`TestMetricsRegistry` validates `MetricsRegistry` factory methods, duplicate metric rejection, illegal metric-name validation, add-by-name stat behavior, and invalid quantile interval handling.

## Important APIs, Types, And Functions

The tests use `MetricsRegistry`, `newCounter()`, `newGauge()`, `newStat()`, `newQuantiles()`, `get()`, `metrics()`, `add(name,value)`, `MutableCounter*`, `MutableGauge*`, `MutableStat`, `MetricsException`, and mocked `MetricsRecordBuilder`.

## Control Flow

`testNewMetrics()` creates counters, gauges, and a stat, checks registry size and concrete metric classes, then expects duplicate counter creation to fail. `testMetricsRegistryIllegalMetricNames()` seeds valid metrics and tries names with spaces, trailing spaces, leading spaces, tab, and newline, asserting they fail and do not grow the registry. `testAddByName()` auto-creates a stat via `add("s1",42)`, snapshots it, and verifies num-ops/average metrics, then asserts `add()` is unsupported for existing counter/gauge names. `testAddIllegalParameters()` asserts negative quantile intervals are rejected.

## State And Persistence Behavior

State is the in-memory registry map and mutable metric contents. There is no persistence. The helper `expectMetricsException()` is annotated `@Disabled` despite being private, but it is directly invoked by tests and still runs as a helper.

## Dependencies And Integration Points

It integrates metrics registry internals, mutable metric implementations, quantile validation, interned metadata, and metrics assertion utilities. Registry behavior is foundational for annotation and source tests.

## Risks And Test Signals

Risks include allowing duplicate names, accepting whitespace names that break sinks, unsupported `add()` paths mutating wrong metric types, and accepting invalid quantile intervals. Signals are registry size/class assertions, exception message prefixes, and builder verifications for generated stat metrics.
