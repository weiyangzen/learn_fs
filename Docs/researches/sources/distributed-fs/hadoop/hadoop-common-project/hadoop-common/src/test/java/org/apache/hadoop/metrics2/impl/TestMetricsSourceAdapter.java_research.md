# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/impl/TestMetricsSourceAdapter.java

## Purpose

`TestMetricsSourceAdapter` validates metrics source adaptation for metrics collection and JMX exposure, including stale metric purging and a race around JMX cache refresh.

## Important APIs, Types, And Functions

The tests construct `MetricsSourceAdapter`, annotation-backed `MetricsSource`s via `MetricsAnnotations.newSourceBuilder()`, inspect `MBeanInfo`/`MBeanAttributeInfo`, call `getMetrics()`, `getAttribute()`, and use scheduled `SourceUpdater` and `SourceReader` helpers. `PurgableSource`, `TestSource`, and `TestMetricsSource` provide controlled metric changes.

## Control Flow

`testPurgeOldMetrics()` uses a source that emits a new key name each collection and asserts the latest key remains exported after the JMX cache TTL. `testGetMetricsAndJmx()` verifies initial metric value zero through collector and JMX, increments the counter, then verifies both paths see the update. `testMetricCacheUpdateRace()` runs one scheduled task that resets adapter records and another that reads JMX attributes and mutates the source key every two TTLs for ten seconds, asserting no missing-key error occurs.

## State And Persistence Behavior

State includes adapter JMX cache (`lastRecs` behavior), source counters/key-value pairs, scheduled executor tasks, and an `AtomicBoolean` error flag. There is no durable persistence. Threads are shut down after the race test.

## Dependencies And Integration Points

This integrates metrics annotations, metrics source builder, JMX MBean exposure, metrics collector implementation, Guava thread factory, Java scheduled executors, and log4j. It directly guards Hadoop JMX metrics visibility.

## Risks And Test Signals

Risks include timing flakiness from sleeps and ten-second race window, stale JMX attributes, dropped dynamic metrics, and executor cleanup issues. Signals are MBean attribute-name presence, exact JMX attribute values before/after increment, and the race test's `hasError` flag staying false.
