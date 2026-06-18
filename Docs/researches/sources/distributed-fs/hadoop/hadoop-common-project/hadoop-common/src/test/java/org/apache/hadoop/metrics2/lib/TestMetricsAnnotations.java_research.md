# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMetricsAnnotations.java

## Purpose

`TestMetricsAnnotations` validates annotation-driven metrics source construction for fields, methods, class-level metadata, hybrid `MetricsSource` implementations, and invalid annotated shapes.

## Important APIs, Types, And Functions

The file uses `MetricsAnnotations.makeSource()`, `@Metrics`, `@Metric`, mutable metric types (`MutableCounterInt`, `MutableGaugeLong`, `MutableRate`, etc.), `MetricsSource`, `MetricsCollector`, `MetricsRecordBuilder`, `MetricsException`, and `MetricsAsserts.getMetrics()`.

## Control Flow

Field tests create a class with annotated mutable counters/gauges/rates/stats, mutate values, snapshot through the generated source, and verify builder calls. Method tests expose numeric gauges, counters, and tags through annotated getters. Class tests verify `@Metrics(about,context)` controls record info/context. Hybrid tests wrap a class that already implements `MetricsSource` plus annotated registry fields, asserting both manual records and annotation-derived metrics appear. Negative tests assert bad field types, methods with arguments, unsupported return types, bad hybrid definitions, and empty metrics classes throw exceptions.

## State And Persistence Behavior

State is held in mutable metric fields and generated source wrappers. There is no persistence. Hybrid sources may write multiple records per snapshot and use an embedded `MetricsRegistry`.

## Dependencies And Integration Points

This is a central integration test for metrics annotations, mutable metric classes, interned metadata, collector/builder interactions, and error validation. Many Hadoop components depend on annotation-based metrics source creation.

## Risks And Test Signals

Risks include incorrect metric name derivation, wrong counter/gauge type mapping, accepting invalid annotations, duplicate record creation in hybrids, or losing class context. Signals are Mockito verifications of exact builder calls, `assertSame` for hybrid source identity, and exception assertions for invalid definitions.
