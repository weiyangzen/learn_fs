# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/wrappedio/WrappedStatistics.java

## Purpose

`WrappedStatistics` is the reflection-friendly facade over Hadoop `IOStatistics`, `IOStatisticsSnapshot`, and `IOStatisticsContext` APIs. It exposes only static methods and uses broad `Object`/`Serializable` signatures so callers can use reflection without linking directly to every statistics type.

## Important APIs, control flow, and state

The class provides type probes, snapshot creation and retrieval, JSON and filesystem load/save, map extraction for counters/gauges/minimums/maximums/means, thread context get/set/reset/snapshot/aggregate, and pretty string conversion. Most snapshot operations validate with private `requireIOStatisticsSnapshot()` and then invoke `applyToIOStatisticsSnapshot()`. `iostatisticsSnapshot_retrieve()` delegates to `IOStatisticsSupport.retrieveIOStatistics()` and returns null when no statistics are available. Context operations use `IOStatisticsContext.getCurrentIOStatisticsContext()` and `setThreadIOStatisticsContext()`.

The class has no local state. Persistence is explicit when snapshot JSON is saved through `IOStatisticsSnapshot.serializer().save()` or loaded back from a filesystem/path.

## Dependencies and integration points

`DynamicWrappedStatistics` loads this class reflectively. The facade depends on Hadoop filesystem statistics classes, `FunctionRaisingIOE`, `Tuples`, preconditions, and IO statistics logging/support helpers.

## Risks and test signals

Because arguments are intentionally loose, wrong types raise `IllegalArgumentException` or `ClassCastException` depending on the method. Null snapshot handling is not uniform: retrieval can return null, while many snapshot accessors require a real `IOStatisticsSnapshot`. Thread context APIs affect thread-local or inherited execution behavior, so tests must isolate contexts. `TestWrappedStatistics` covers snapshot creation, null and wrong-type inputs, JSON and local save/load, context interaction, metric extraction, missing reflected methods, and casting.
