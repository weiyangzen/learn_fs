# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/MetricsRecords.java

## Purpose

`MetricsRecords` is a public test utility for asserting tags and metric values in a `MetricsRecord` by name.

## Important APIs, Types, And Functions

It provides `assertTag(record, tagName, expectedValue)`, `assertMetric(record, metricName, expectedValue)`, `getMetricValueByName(record, metricName)`, and `assertMetricNotNull(record, metricName)`. Private predicates match `MetricsTag.name()` and `AbstractMetric.name()`.

## Control Flow

Each assertion method searches the record's tags or metrics for the first matching name, asserts it is not null, and compares or returns the value. Metrics are streamed from the iterable with `StreamSupport`.

## State And Persistence Behavior

The utility is stateless and reads only supplied records. It handles null tag/metric iterables by returning null from the private lookup, causing the public assertion to fail.

## Dependencies And Integration Points

It integrates with metrics2 `MetricsRecord`, `MetricsTag`, `AbstractMetric`, and JUnit assertions. It is designed for tests outside the `impl` package that need concise metric lookups.

## Risks And Test Signals

Risks include first-match ambiguity when duplicate names exist and strict numeric type equality. Test signals are targeted assertion failures that name missing metrics and exact expected values.
