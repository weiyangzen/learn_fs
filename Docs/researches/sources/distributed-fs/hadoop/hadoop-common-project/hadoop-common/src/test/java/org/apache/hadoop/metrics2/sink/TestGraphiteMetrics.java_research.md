# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestGraphiteMetrics.java

## Purpose
Unit coverage for `GraphiteSink` line formatting, timestamp conversion, write failure handling, reconnect behavior, and close delegation.

## Important APIs, Types, And Functions
Uses `GraphiteSink`, nested `GraphiteSink.Graphite`, `setGraphite()`, `putMetrics()`, `flush()`, and `close()`. Helpers create mocked `AbstractMetric` and `Graphite` objects. Test records use `MetricsRecordImpl`, `MetricsTag`, and `MsInfo`.

## Control Flow
Tests build records with context/hostname tags and unordered metric sets, inject a mock Graphite connection, call `putMetrics()`, capture written strings, and compare against both possible set iteration orders. Failure testing makes the first write throw `IOException`, verifies close, resets the mock to disconnected, and confirms a later put writes expected lines.

## State And Persistence Behavior
No durable state is created. Sink state is its injected Graphite object and connection flag. Timestamps are converted from milliseconds to seconds in emitted lines.

## Dependencies And Integration Points
Integrates with metrics2 record/tag/metric abstractions and Graphite's plaintext protocol shape: path, value, epoch seconds.

## Risks
Metrics are stored in `HashSet`, so output order is nondeterministic. The expected path includes default/null prefixes and tag names, making tests sensitive to path-building changes. Error handling must close broken connections without losing future writes.

## Test Signals
Expected lines include `null.all.Context.Context=all.Hostname=host.foo1 1.25 10` and one-second timestamp differences for records 1000 ms apart.
