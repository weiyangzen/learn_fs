# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/wrappedio/impl/TestWrappedStatistics.java

## Purpose
`TestWrappedStatistics` verifies dynamic access to Hadoop IOStatistics, IOStatisticsSnapshot, JSON persistence, and IOStatisticsContext operations through `DynamicWrappedStatistics`.

## Important APIs, Types, and Functions
The suite uses `DynamicWrappedStatistics`, `IOStatisticsContext`, `IOStatisticsSnapshot`, `IOStatisticsStore`, `IOStatisticsBinding.iostatisticsStore()`, `trackDurationOfInvocation()`, `FileSystem.getLocal()`, and local JSON paths. It exercises wrapper methods for availability probes, type predicates, snapshot create/retrieve/aggregate, JSON string conversion, save/load, pretty printing, maps of counters/gauges/minimums/maximums/means, and context set/reset/snapshot/aggregate.

## Control Flow
Setup creates a local filesystem and a `snapshot.json` path. Tests first validate method availability and error handling for null or wrong serializable types. Context tests get the current context, snapshot it, JSON round-trip it, reset and restore thread-local context, and aggregate snapshots. Extraction tests build a statistics store with counters, gauges, and duration tracking, then verify persisted JSON and extracted metric maps. Missing-method tests bind to an empty stub class and assert probes downgrade while operations throw `UnsupportedOperationException`.

## State and Persistence
Temporary JSON snapshots are saved to and loaded from the local filesystem. IOStatisticsContext is thread-local and is reset or replaced in tests. Statistics store state is in-memory until serialized.

## Dependencies and Integration Points
The file integrates dynamic reflection wrappers with Hadoop filesystem statistics APIs, local filesystem persistence, and duration tracking. It protects compatibility for code that optionally uses IOStatistics when present.

## Risks and Edge Cases
Tests intentionally pass wrong types to validate argument checking. Duration minimums and maximums depend on wall-clock sleep timing and may vary, so assertions focus on positive and relational values. Missing-method simulation must not accidentally bind inherited methods.

## Test Signals
Signals include true availability on current runtime, correct type predicates, JSON equality after round trip, expected exceptions for bad inputs and overwrite/load failures, doubled counter aggregation in context, extracted counter/gauge/duration maps, and clean unsupported-operation behavior for missing bindings.
