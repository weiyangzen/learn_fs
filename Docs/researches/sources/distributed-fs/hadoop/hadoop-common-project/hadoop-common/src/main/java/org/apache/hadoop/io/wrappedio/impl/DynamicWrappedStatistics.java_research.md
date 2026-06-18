# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/impl/DynamicWrappedStatistics.java

## Purpose

`DynamicWrappedStatistics` dynamically binds the static methods in `WrappedStatistics` so libraries can use IO statistics features when present and degrade when absent.

## Important APIs, control flow, and state

The constructor loads `org.apache.hadoop.io.wrappedio.WrappedStatistics` and binds methods for type probes, IOStatisticsContext operations, snapshot creation/aggregation/retrieval/load/save/JSON conversion, metric map extraction, and pretty printing. `ioStatisticsAvailable()` and `ioStatisticsContextAvailable()` check representative bindings. Most public operations either return false when unavailable for probes or call `checkIoStatisticsAvailable()`/`checkIoStatisticsContextAvailable()` before invoking the reflected method.

The object stores only the immutable loaded flag and method handles. It has no singleton; callers instantiate it as needed, including with alternate class names for tests.

## Dependencies and integration points

It depends on `DynMethods`, `BindingUtils`, `IOStatistics`, `IOStatisticsSource`, `FileSystem`, `Path`, and `Serializable`. It is the dynamic counterpart to `WrappedStatistics` and is used heavily by `TestWrappedStatistics`.

## Risks and test signals

Return type and parameter signatures must stay synchronized with `WrappedStatistics`. Some accessors such as `iostatistics_counters()` do not check availability before invocation, so callers should probe before use or expect reflective unavailable failures. Type looseness means errors may appear as `ClassCastException`, `IllegalArgumentException`, `UncheckedIOException`, or `UnsupportedOperationException` depending on the target method. Tests cover loaded and missing classes, missing context methods, snapshot serialization, context aggregation, statistics extraction, and casting.
