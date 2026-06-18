# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsSystemImpl.java

## Purpose

`TestMetricsSystemImpl` is the main metrics2 system integration test. It covers startup/shutdown, source and sink registration, filters, concurrent publishing, hanging sinks, queue sizing, unregister/restart behavior, JMX cache TTL, multiple sink periods, and metrics-system restart.

## Important APIs, Types, And Functions

The class uses `MetricsSystemImpl`, `DefaultMetricsSystem`, `MetricsSink`, `MetricsSource`, `MetricsRegistry`, mutable metrics annotations, `ConfigBuilder`, `MetricsConfig`, sink/source adapters, and Mockito captors. Helper classes include `TestSink`, `CollectingSink`, `HangingSink`, `TestClosableSink`, `TestSource`, and `TestSource2`.

## Control Flow

Initialization tests write metrics config with source/metric filters, start a metrics system, register sources/sinks, publish, stop/shutdown, and assert captured records match expected filtered metrics. The multithreaded test registers ten sources and uses barriers so all threads set gauges and publish simultaneously, then asserts every source's metric is collected and no dropped publications occur. Hanging/closeable sink tests verify dropped publish counters, interruption on stop, later sink calls, and stop behavior when `putMetrics()` loops until closed. Other tests validate duplicate registration semantics before/after start, unregistering sources, default names for unnamed source registration, queue size metrics for slow sinks, JMX cache TTL defaults, multiple sink periods on timer events, and sink adapter preservation after restart.

## State And Persistence Behavior

The file writes test metrics config files, mutates the singleton default metrics system into mini-cluster mode, maintains source/sink registries, sink queues, dropped-publish counters, MBean names, and background sink threads. Tests usually stop and shutdown systems in `finally` blocks, but global metrics system state is a cross-test concern.

## Dependencies And Integration Points

It integrates metrics2 core implementation, annotations, mutable metric classes, source/sink adapters, filters, config parsing, JMX registration, concurrency primitives, Mockito, and Hadoop test utilities. It is the broadest signal for metrics system behavior across source collection and sink publication.

## Risks And Test Signals

Risks include timing flakes in async sink delivery, leaked threads or MBeans, global default metrics contamination, queue capacity/dropped counter regressions, and race conditions during concurrent publish. Signals include captured record equality, expected context/hostname tags, expected metric lists, dropped counter assertions, sink call timeouts, queue size metric extraction, source adapter lookup after restart, and wait-for checks for multiple sink periods.
