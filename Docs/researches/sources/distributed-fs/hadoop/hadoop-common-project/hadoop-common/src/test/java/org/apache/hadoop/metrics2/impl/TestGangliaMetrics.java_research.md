# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestGangliaMetrics.java

## Purpose

`TestGangliaMetrics` validates metrics2 Ganglia sink prefix tagging and emitted datagram records for Ganglia 3.0 and 3.1 sinks.

## Important APIs, Types, And Functions

The file uses `GangliaSink30`, `GangliaSink31`, `AbstractGangliaSink`, `GangliaMetricsTestHelper.setDatagramSocket()`, `MetricsSystemImpl`, annotated `TestSource`, and a custom `MockDatagramSocket` that captures sent bytes.

## Control Flow

`testTagsForPrefix()` configures `tagsForPrefix` for contexts `all`, `some`, and `none`, builds a `MetricsRecordImpl`, and asserts appended prefixes include all, selected, or no tags. `testGangliaMetrics2()` writes metrics config, starts a metrics system, registers a source and two Ganglia sinks with mock sockets, publishes metrics manually, stops the system, and checks captured datagrams contain expected metric names. Ganglia 3.1 expects twice as many packets because it emits metadata plus value records.

## State And Persistence Behavior

State includes a saved test metrics properties file, metrics system registration, source counter/gauge/rate values, and captured datagram byte arrays. `MockDatagramSocket` copies packet bytes to avoid reuse aliasing.

## Dependencies And Integration Points

This integrates metrics2 core, annotation-based sources, Ganglia sink implementations, UDP datagram sending, and test helper reflection into sink socket state.

## Risks And Test Signals

Risks include UDP packet format changes, prefix tag ordering, datagram buffer reuse, config-file race with other tests, and manual publish timing. Signals are exact prefix strings, expected metric-name coverage, and expected datagram counts for Ganglia 3.0 versus 3.1.
