# Research: subset-b-007350

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsContext.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsContext.java

Purpose: public interface for per-thread IOStatistics capture. It gives filesystem and stream code a current-thread context whose aggregator can collect statistics from operations and later return an incremental `IOStatisticsSnapshot`.

Important APIs, types, and functions: extends `IOStatisticsSource`; exposes `getAggregator()`, `snapshot()`, `getID()`, and `reset()`. Static helpers delegate to `IOStatisticsContextIntegration`: `getCurrentIOStatisticsContext()`, `setThreadIOStatisticsContext()`, and `enabled()`.

Control flow: callers fetch the current context through the static accessor, pass `getAggregator()` into statistics-producing code, and call `snapshot()` or `reset()` when work units complete. The accessor wraps the integration result in `requireNonNull()` to catch regression to a null context.

State and persistence: no direct state in the interface. Runtime state lives in implementation instances and in the thread map managed by `IOStatisticsContextIntegration`. Snapshots can be serialized through `IOStatisticsSnapshot`; the live context itself is process/thread scoped.

Dependencies and integration points: depends on `IOStatisticsAggregator`, `IOStatisticsSnapshot`, `IOStatisticsSource`, and the implementation bridge in `statistics.impl`. It is the public entry point used by filesystem clients that want thread-level accounting.

Risks and test signals: behavior depends on the global thread-level statistics configuration. Tests should cover enabled and disabled modes, null reset behavior, unique IDs, snapshot/reset semantics, and the safety check that the current context is never null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsLogging.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsLogging.java

Purpose: utility class for converting IOStatistics sources to robust log strings and logging them at configured levels without forcing expensive evaluation unless needed.

Important APIs, types, and functions: `ioStatisticsSourceToString()`, `ioStatisticsToString()`, `ioStatisticsToPrettyString()`, `demandStringifyIOStatisticsSource()`, `demandStringifyIOStatistics()`, `logIOStatisticsAtDebug()`, and `logIOStatisticsAtLevel()`. Private helpers render maps through `IOStatisticsBinding.entryToString()` and sorted `TreeMap` copies.

Control flow: source objects are converted through `IOStatisticsSupport.retrieveIOStatistics()`. Plain string output iterates all maps in source order; pretty output builds sorted maps and filters zero counters/gauges, unset min/max values, and empty means. Demand stringifiers defer evaluation to `toString()`, making them safe to pass to disabled log statements.

State and persistence: stateless except for a class logger. It reads live statistics maps on demand and does not persist data.

Dependencies and integration points: depends on SLF4J, Hadoop logging level constants, `IOStatisticsSupport`, `MeanStatistic`, and `IOStatisticsBinding`. It integrates with filesystem close/debug paths and optional configured logging of statistics.

Risks and test signals: `logIOStatisticsAtLevel(Logger log, String level, Object source)` accepts a logger but uses the class logger for info/warn/error branches, so tests should detect logger routing expectations. Tests should cover null sources, throwing sources, empty filtering, sorted pretty output, demand stringification, and unknown logging levels falling back to debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsLogging.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSetters.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSetters.java

Purpose: small public interface that adds direct setter methods to the read-only `IOStatistics` contract so mutable stores and snapshots can share a common mutation surface.

Important APIs, types, and functions: declares `setCounter()`, `setGauge()`, `setMaximum()`, `setMinimum()`, and `setMeanStatistic()`.

Control flow: implementations decide whether unknown keys are no-ops or create entries. `IOStatisticsSnapshot` inserts values into maps; `IOStatisticsStoreImpl` only updates predeclared atomic entries.

State and persistence: no state. It defines write access to runtime or snapshot statistics state.

Dependencies and integration points: depends on `IOStatistics` and `MeanStatistic`. It is implemented by `IOStatisticsSnapshot` and `IOStatisticsStore`.

Risks and test signals: callers must understand the implementation-specific unknown-key policy. Tests should cover snapshot insertion, store no-op behavior for missing keys, mean statistic copy/reference expectations, and compatibility with JSON/serialized snapshots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSetters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSnapshot.java

Purpose: serializable, mutable point-in-time copy of an `IOStatistics` source. It also acts as an aggregator and setter target so frameworks can collect, merge, serialize, and transport statistics.

Important APIs, types, and functions: constructors for empty and source-backed snapshots, `snapshot()`, `aggregate()`, map accessors, direct setters, `clear()`, `serializer()`, Java serialization hooks, and `requiredSerializationClasses()`.

Control flow: `snapshot(source)` replaces all internal maps with concurrent snapshot copies, copying `MeanStatistic` values. `aggregate(source)` merges counters by nonnegative addition, gauges by addition, minimum/maximum with unset handling, and means by copied accumulation. Java serialization writes sorted `TreeMap` copies and rebuilds concurrent maps on read.

State and persistence: maintains transient maps for counters, gauges, minimums, maximums, and means. It persists through Java serialization and Jackson JSON annotations; callers must treat untrusted object streams carefully and can use the required class list for filtering.

Dependencies and integration points: depends on Jackson, Hadoop `JsonSerialization`, `IOStatisticsBinding`, `MeanStatistic`, and `IOStatisticsLogging`. It is the transferable representation used by thread contexts and distributed frameworks such as Spark or Flink.

Risks and test signals: aggregate is synchronized but returned maps are mutable and can be externally modified. Tests should cover null aggregation, mean deep-copy behavior, serialization round trip, JSON field names including `meanstatistics`, unset min/max aggregation, and mutation through setters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSource.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSource.java

Purpose: minimal public contract for objects that can expose an `IOStatistics` instance.

Important APIs, types, and functions: declares `getIOStatistics()`, which may return live, dynamic, snapshot, empty, or null statistics depending on the implementation.

Control flow: utility code such as `IOStatisticsSupport.retrieveIOStatistics()` first checks whether a source object is itself an `IOStatistics`, then falls back to this interface and calls `getIOStatistics()`.

State and persistence: no state. It is a reference contract over state owned by implementors.

Dependencies and integration points: depends on `IOStatistics`. It integrates streams, filesystems, wrappers, and contexts with logging and snapshot utilities.

Risks and test signals: callers must tolerate null or dynamic results. Tests should verify retrieval from both direct `IOStatistics` instances and `IOStatisticsSource` wrappers, including null-returning implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSupport.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSupport.java

Purpose: public support helpers for snapshots, source retrieval, and no-op duration tracking.

Important APIs, types, and functions: `snapshotIOStatistics(IOStatistics)`, `snapshotIOStatistics()`, `retrieveIOStatistics(Object)`, `stubDurationTrackerFactory()`, and `stubDurationTracker()`.

Control flow: snapshot helpers instantiate `IOStatisticsSnapshot`; retrieval casts direct `IOStatistics` instances before asking `IOStatisticsSource` objects for their statistics. Stub helpers return singleton no-op tracker objects.

State and persistence: stateless. Snapshot helpers create serializable state in returned `IOStatisticsSnapshot` objects.

Dependencies and integration points: depends on public statistics interfaces and implementation stubs. It is used by logging, callers that accept optional statistics, and code paths where duration tracking must be optional.

Risks and test signals: retrieval returns null for null or non-statistics objects, so callers must not blindly dereference. Tests should cover direct statistics, source wrappers, null sources, unsupported sources, snapshot copy behavior, and singleton no-op duration trackers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/MeanStatistic.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/MeanStatistic.java

Purpose: serializable value object for a mean statistic represented by sample count and sum, with mean computed on demand.

Important APIs, types, and functions: constructors, `getSum()`, `getSamples()`, `isEmpty()`, `clear()`, `setSamplesAndSum()`, `set()`, `setSum()`, `setSamples()`, `mean()`, `add()`, `addSample()`, `copy()`, `clone()`, equality, hash, and `toString()`.

Control flow: invalid nonpositive sample counts in construction reset to empty; negative sample counts in setters become zero. `add(other)` ignores empty inputs, copies non-empty values into an empty destination, or accumulates samples and sum into a non-empty destination. Equality treats all empty stats as equivalent regardless of sum.

State and persistence: holds two synchronized longs, `samples` and `sum`, and is Java/Jackson serializable. It is mutable and should not be used as a map key while being updated.

Dependencies and integration points: depends on Jackson `JsonIgnore` and Hadoop interface annotations. Used by all IOStatistics mean maps, snapshots, stores, and dynamic statistics.

Risks and test signals: add synchronizes on both objects and can be sensitive to concurrent access patterns if callers create cycles. Tests should cover empty equality, negative sample normalization, copy isolation, concurrent sample addition, JSON round trip, and mean precision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/MeanStatistic.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/StoreStatisticNames.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/StoreStatisticNames.java

Purpose: public constant catalog for object-store and filesystem operation statistics.

Important APIs, types, and functions: declares string constants for filesystem operations (`OP_OPEN`, `OP_CREATE`, `OP_DELETE`, etc.), store IO events, object requests, multipart uploads, HTTP responses, duration suffixes (`.min`, `.max`, `.mean`, `.failures`), and conditional create metrics.

Control flow: no executable flow beyond private constructor. Other classes compose names from these constants, especially duration tracker suffix handling in `IOStatisticsStoreImpl` and `StatisticDurationTracker`.

State and persistence: no runtime state. The string values are persistent compatibility contracts for logs, metrics, and downstream monitoring.

Dependencies and integration points: depends only on Hadoop classification annotations. Integrated across S3A/object-store code, storage statistics publication, audit operation names, and common metrics consumers.

Risks and test signals: renaming or reusing constants breaks metric compatibility. Tests should verify uniqueness, expected literal names, suffix composition, and consumers that aggregate duration metrics by shared prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/StoreStatisticNames.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/StreamStatisticNames.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/StreamStatisticNames.java

Purpose: public constant catalog for stream-level statistics, especially input-stream read, seek, vectored read, policy, and leak metrics.

Important APIs, types, and functions: declares string constants such as stream leaks, aborted/closed reads, bytes read/discarded, read operations, seek counts and bytes, vectored read counters, and stream policy metrics.

Control flow: no executable flow beyond private constructor. Constants are referenced by stream implementations and audit/span code as stable operation names.

State and persistence: no runtime state. Constant string values are part of the public evolving metrics contract.

Dependencies and integration points: depends on Hadoop annotations. Integrates filesystem stream implementations with IOStatistics and monitoring.

Risks and test signals: typo or duplicate names can fragment metrics. Tests should cover literal compatibility, uniqueness, and expected counters being registered by stream stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/StreamStatisticNames.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/AbstractIOStatisticsImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/AbstractIOStatisticsImpl.java

Purpose: tiny base class for IOStatistics implementations that standardizes `toString()` through the logging formatter.

Important APIs, types, and functions: implements `toString()` by calling `IOStatisticsLogging.ioStatisticsToString(this)`.

Control flow: subclasses provide the statistics maps; `toString()` delegates all rendering to the public logging utility.

State and persistence: no state. It only reads subclass state during stringification.

Dependencies and integration points: depends on `IOStatistics` and `IOStatisticsLogging`. Extended by empty and dynamic statistics implementations.

Risks and test signals: stringification can evaluate dynamic maps and may not be cheap. Tests should cover subclass `toString()` output for empty and dynamic implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/AbstractIOStatisticsImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/DynamicIOStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/DynamicIOStatistics.java

Purpose: package-private IOStatistics implementation whose map values are evaluated lazily through registered functions.

Important APIs, types, and functions: map accessors return unmodifiable maps for counters, gauges, minimums, maximums, and means. Package methods add evaluator functions for each category.

Control flow: builder registers key-to-function mappings. When callers access or iterate the returned maps, `EvaluatingStatisticsMap` invokes the functions and returns current values; mean values are copied to avoid exposing mutable internals.

State and persistence: stores evaluator functions rather than fixed values. It is live and non-serializable; snapshots are needed to persist point-in-time values.

Dependencies and integration points: depends on `AbstractIOStatisticsImpl`, `EvaluatingStatisticsMap`, and `MeanStatistic`. Built by `DynamicIOStatisticsBuilder`, used by stores and adapters over Hadoop `StorageStatistics`.

Risks and test signals: evaluator failures happen during map reads and can surprise logging/snapshot callers. Tests should cover lazy evaluation, unmodifiable maps, mean copy isolation, duplicate key replacement behavior, and snapshot consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/DynamicIOStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/DynamicIOStatisticsBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/DynamicIOStatisticsBuilder.java

Purpose: one-shot builder for dynamic IOStatistics backed by functions, atomics, and metrics counters.

Important APIs, types, and functions: `build()`, `withLongFunctionCounter/Gauge/Minimum/Maximum()`, atomic long/int variants, `withMutableCounter()`, and mean-statistic function registration.

Control flow: the builder maintains a single active `DynamicIOStatistics` instance. Every `with...` method obtains the active instance and registers a function; `build()` returns it and nulls the active reference so future use throws `IllegalStateException`.

State and persistence: builder state is transient and invalid after build. Built statistics retain references to supplied atomics/functions and therefore reflect live external state.

Dependencies and integration points: depends on `AtomicLong`, `AtomicInteger`, Hadoop metrics `MutableCounterLong`, and `MeanStatistic`. Used by `IOStatisticsBinding` and `IOStatisticsStoreImpl` to expose atomic maps dynamically.

Risks and test signals: the one-shot lifecycle must be enforced and external function references must remain valid. Tests should cover all source types, post-build failure, live updates from atomics, and evaluator exception behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/DynamicIOStatisticsBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EmptyIOStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EmptyIOStatistics.java

Purpose: singleton immutable no-data IOStatistics implementation for callers that want to return non-null statistics.

Important APIs, types, and functions: map accessors return `Collections.emptyMap()` for every statistic category; static `getInstance()` returns the singleton.

Control flow: all calls are immediate no-ops/read-only empty map returns.

State and persistence: no mutable state. Singleton lifetime is process-wide.

Dependencies and integration points: extends `AbstractIOStatisticsImpl`; exposed through `IOStatisticsBinding.emptyStatistics()`.

Risks and test signals: returned empty maps are immutable, so mutation attempts should fail. Tests should cover singleton identity, empty string rendering, and safe use where nullable statistics used to be returned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EmptyIOStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EmptyIOStatisticsContextImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EmptyIOStatisticsContextImpl.java

Purpose: singleton disabled-mode IOStatisticsContext used when thread-level IO statistics are not enabled.

Important APIs, types, and functions: `snapshot()`, `getAggregator()`, `getIOStatistics()`, `reset()`, `getID()`, and package-private `getInstance()`.

Control flow: snapshot returns an empty snapshot, aggregator/statistics return empty no-op objects, reset does nothing, and the ID is fixed for the disabled context.

State and persistence: no mutable state beyond shared singleton identity. It avoids creating per-thread state when collection is disabled.

Dependencies and integration points: depends on `IOStatisticsContext`, `IOStatisticsSnapshot`, and `IOStatisticsBinding` empty objects. Returned by `IOStatisticsContextIntegration` in disabled mode.

Risks and test signals: callers should not assume IDs identify real thread contexts when disabled. Tests should cover disabled mode no-op aggregation, non-null returns, reset behavior, and stable singleton access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EmptyIOStatisticsContextImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EmptyIOStatisticsStore.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EmptyIOStatisticsStore.java

Purpose: singleton no-op implementation of the mutable `IOStatisticsStore` contract.

Important APIs, types, and functions: all map accessors return empty maps; setters, increments, samples, reset, and aggregate are no-ops; unknown reference getters return no usable statistic references; duration tracking returns a stub tracker.

Control flow: mutation methods either do nothing or return zero/false. Duration methods avoid allocating real operation trackers.

State and persistence: no mutable state and no persistence. Singleton lifetime is process-wide.

Dependencies and integration points: implements `IOStatisticsStore`; exposed through `IOStatisticsBinding.emptyStatisticsStore()`. Used when code requires a non-null store but statistics are disabled or unavailable.

Risks and test signals: code that expects reference getters to succeed must not be passed the empty store. Tests should cover no-op mutations, empty map immutability, aggregate false, and stub duration tracker behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EmptyIOStatisticsStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EvaluatingStatisticsMap.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EvaluatingStatisticsMap.java

Purpose: map implementation that stores key-to-evaluator functions and evaluates values lazily when map entries are read or iterated.

Important APIs, types, and functions: function registration, `entrySet()`, `containsKey()`, `get()`, iterator-backed entries, and optional value-copy function.

Control flow: callers register evaluator functions by key. Map reads call the function with the key and optionally copy the resulting value before returning it. Iteration evaluates each entry as `next()` is consumed.

State and persistence: stores evaluator functions, not concrete values. It is live runtime state and should be snapshotted for persistence.

Dependencies and integration points: used internally by `DynamicIOStatistics` to expose dynamic maps. Mean-statistic maps use a copy function so mutable means are not directly leaked.

Risks and test signals: map methods can execute arbitrary evaluator code and throw runtime exceptions during logging or iteration. Tests should cover lazy evaluation timing, copy isolation, key lookup, iteration, unmodifiable wrapping at the `DynamicIOStatistics` layer, and duplicate registrations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EvaluatingStatisticsMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/ForwardingIOStatisticsStore.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/ForwardingIOStatisticsStore.java

Purpose: delegating wrapper that implements the full `IOStatisticsStore` interface by forwarding every operation to an inner store.

Important APIs, types, and functions: constructor, protected `getInnerStatistics()`, all map accessors, aggregation, setters/increments, reference getters, mean operations, reset, timed operation updates, and duration tracking.

Control flow: every public method directly calls the matching method on the inner store, preserving return values and exceptions. Subclasses can override selected behavior while retaining default forwarding.

State and persistence: holds only a final reference to the inner store. Persistent or live state is owned by the delegate.

Dependencies and integration points: depends on `IOStatisticsStore`, `MeanStatistic`, `AtomicLong`, and `Duration`. It supports decoration of statistics stores without reimplementing the contract.

Risks and test signals: a null inner store would fail later; constructor validation should be checked in use. Tests should verify exact forwarding, exception propagation, and subclass override compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/ForwardingIOStatisticsStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsBinding.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsBinding.java

Purpose: central implementation helper for IOStatistics construction, wrapping, snapshots, aggregation math, atomic min/max updates, duration tracking wrappers, and publication as `StorageStatistics`.

Important APIs, types, and functions: factory methods for dynamic stats, empty stats/store, source wrapping, stores, paired duration factories, storage-stat publication, and storage-stat adaptation. Utility methods include `entryToString()`, `snapshotMap()`, `aggregateMaps()`, counter/gauge/min/max/mean aggregators, CAS-based `maybeUpdateMaximum()` and `maybeUpdateMinimum()`, `createTracker()`, and multiple `track...` wrappers for Java and Hadoop functional interfaces.

Control flow: construction helpers instantiate implementation classes. Aggregation helpers copy or merge map values with supplied functions. Duration wrappers create a tracker before invoking user code, mark failures on `IOException` or `RuntimeException`, and close the tracker in `finally`; null factories produce the stub tracker.

State and persistence: stateless utility class. It creates objects that own state elsewhere and copies maps for snapshots.

Dependencies and integration points: depends on Hadoop `StorageStatistics`, `DurationTrackerFactory`, functional interfaces, atomics, and `MeanStatistic`. It is the main integration point between low-level stores, public statistics interfaces, logging, and filesystem operation wrappers.

Risks and test signals: duration wrappers do not mark checked exceptions other than `IOException` in Java `Callable` variants, and tracker close exceptions would affect wrapped calls. Tests should cover failure marking for IO/runtime exceptions, null factories, aggregation with unset min/max, atomic update races, map copy isolation, and storage statistics publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsBinding.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsContextImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsContextImpl.java

Purpose: concrete per-thread IOStatisticsContext that aggregates into a mutable `IOStatisticsSnapshot`.

Important APIs, types, and functions: constructor taking thread ID and unique ID; `getAggregator()`, `snapshot()`, `reset()`, `getIOStatistics()`, `getID()`, and `toString()`.

Control flow: producers aggregate into the internal snapshot via `getAggregator()`. `snapshot()` returns a new snapshot copy; `reset()` clears internal maps for the next interval.

State and persistence: stores `threadId`, unique `id`, and a live mutable `IOStatisticsSnapshot`. Snapshot copies are serializable; the context itself is runtime state.

Dependencies and integration points: implements `IOStatisticsContext`; created by `IOStatisticsContextIntegration` for threads tracked in the weak thread map.

Risks and test signals: reset clears the shared internal aggregator, so callers must snapshot before reset. Tests should cover aggregate/snapshot isolation, reset, logging output, unique ID assignment, and concurrent access through snapshot synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsContextImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsContextIntegration.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsContextIntegration.java

Purpose: static integration layer that owns thread-level IOStatistics enablement and maps current threads to contexts.

Important APIs, types, and functions: static configuration probe, `isIOStatisticsThreadLevelEnabled()`, `getCurrentIOStatisticsContext()`, `setThreadIOStatisticsContext()`, testing lookup by thread ID, `INSTANCE_ID`, and a `WeakReferenceThreadMap`.

Control flow: static initialization reads `IOSTATISTICS_THREAD_LEVEL_ENABLED` from a new `Configuration`. When enabled, current-thread lookup uses the weak reference thread map and creates `IOStatisticsContextImpl` instances on demand. When disabled, it returns the empty context. Setting null removes the current thread mapping.

State and persistence: process-wide static boolean, atomic ID generator, and weak references to contexts keyed by thread ID. No disk persistence.

Dependencies and integration points: depends on Hadoop configuration constants, `WeakReferenceThreadMap`, and context implementations. It backs the public static methods on `IOStatisticsContext`.

Risks and test signals: enablement is read during class initialization, so tests that change configuration must manage classloading or use test hooks. Weak references can disappear after GC. Tests should cover enabled/disabled modes, mapping replacement/removal, GC loss callbacks, unique IDs, and cross-thread isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsContextIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStore.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStore.java

Purpose: mutable statistics store contract combining IOStatistics, setter, aggregation, and duration tracking capabilities.

Important APIs, types, and functions: counter/gauge/min/max increments, sample methods, `reset()`, atomic reference getters, `getMeanStatistic()`, timed operation helpers, and default `incrementCounter(key)` and `addSample()`.

Control flow: implementations update registered statistic entries, ignore unknown keys where documented, and provide `DurationTrackerFactory.trackDuration()` through the inherited factory interface. `addSample()` updates count, mean, max, and min for a single key.

State and persistence: no state in the interface. Implementations usually hold atomics and mean objects in memory; snapshots are needed for persistence.

Dependencies and integration points: extends `IOStatistics`, `IOStatisticsSetters`, `IOStatisticsAggregator`, and `DurationTrackerFactory`. Used by filesystem and stream implementations as their core mutable metrics sink.

Risks and test signals: updates across count/mean/min/max are explicitly not atomic as a group. Tests should cover unknown key policy, reference getter exceptions, duration tracker integration, reset, aggregation, and concurrent updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStoreBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStoreBuilder.java

Purpose: builder interface for constructing an `IOStatisticsStore` with declared statistic keys.

Important APIs, types, and functions: fluent `withCounters()`, `withGauges()`, `withMinimums()`, `withMaximums()`, `withMeanStatistics()`, duration convenience declarations, and `build()`.

Control flow: callers declare the keys a store should track, then call `build()` to receive a mutable store implementation.

State and persistence: no state in the interface. Implementations hold declaration lists until build time.

Dependencies and integration points: implemented by `IOStatisticsStoreBuilderImpl`; obtained through `IOStatisticsBinding.iostatisticsStore()`.

Risks and test signals: if callers forget to register a key, later updates become no-ops or reference lookups fail. Tests should cover all declaration methods and duplicate/null key handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStoreBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStoreBuilderImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStoreBuilderImpl.java

Purpose: concrete builder that collects key declarations and creates `IOStatisticsStoreImpl`.

Important APIs, types, and functions: list fields for counters, gauges, minimums, maximums, and means; fluent `with...` methods; duration-stat helper methods that register `.min`, `.max`, and `.mean` names; `build()`.

Control flow: each declaration appends keys to internal lists. `build()` passes those lists to `IOStatisticsStoreImpl`, which creates atomics and dynamic map bindings.

State and persistence: builder maintains mutable declaration lists. The built store owns runtime metric state; the builder has no persistence.

Dependencies and integration points: depends on store implementation and statistic suffix constants. It is the normal construction path for filesystem statistics stores.

Risks and test signals: duplicate declarations can overwrite map entries during store construction and may hide configuration mistakes. Tests should cover duration key expansion, duplicate behavior, null/empty varargs, and correct map registration after build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStoreBuilderImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStoreImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStoreImpl.java

Purpose: concrete thread-safe-ish mutable IOStatistics store backed by concurrent maps of `AtomicLong` values and synchronized `MeanStatistic` instances.

Important APIs, types, and functions: constructor from key lists; setters/increments for counters, gauges, minimums, and maximums; min/max sample update; mean setters/samples; `reset()`, `aggregate()`, atomic reference getters, `addTimedOperation()`, and `trackDuration()`.

Control flow: construction creates atomics for registered keys and builds a dynamic statistics wrapper over those atomics. Updates for unknown keys are no-ops except reference getters, which throw. Counter increments ignore negative values. `aggregate()` folds source values into registered entries only; gauges add positive values; min/max use aggregation helpers; means add samples. `trackDuration()` creates a `StatisticDurationTracker` only if the counter key is registered.

State and persistence: in-memory maps hold mutable atomics and means. Exposed IOStatistics is live via `WrappedIOStatistics`; snapshots are required for durable copies.

Dependencies and integration points: depends on `DynamicIOStatisticsBuilder`, `IOStatisticsBinding`, `StatisticDurationTracker`, `MeanStatistic`, `Duration`, and store suffix constants. Used as the primary mutable metrics store for Hadoop filesystem code.

Risks and test signals: `reset()` sets min/max atomics to zero rather than the unset sentinel used at construction, which can affect later min/max aggregation semantics. The minimum aggregation path calls `aggregateMaximums()` before `aggregateMinimums()`, which is suspicious but usually overwritten by the second set. Tests should cover reset sentinel behavior, negative counters, positive-only gauge aggregation, concurrent min/max CAS updates, unknown key handling, and duration tracker failure metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStoreImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/PairedDurationTrackerFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/PairedDurationTrackerFactory.java

Purpose: duration tracker factory that forwards one operation lifecycle into two underlying factories, typically local and global statistics.

Important APIs, types, and functions: constructor accepts two factories; `trackDuration()` returns a private paired tracker; paired tracker implements `failed()`, `close()`, `asDuration()`, and `toString()`.

Control flow: `trackDuration()` creates trackers from both delegates. Failure and close are invoked on both. Duration and string output come from the first wrapped tracker, which is created from the global factory in this implementation.

State and persistence: stores two factory references; per-operation tracker stores two duration trackers. No persistence.

Dependencies and integration points: depends on `DurationTrackerFactory` and `DurationTracker`; exposed by `IOStatisticsBinding.pairedTrackerFactory()`.

Risks and test signals: if the first delegate throws during close, the second may not close. Tests should cover ordering, failure propagation to both trackers, duration source selection, null delegate behavior, and close exception handling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/PairedDurationTrackerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/SourceWrappedStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/SourceWrappedStatistics.java

Purpose: simple adapter that wraps an `IOStatistics` instance as an `IOStatisticsSource`.

Important APIs, types, and functions: constructor and `getIOStatistics()`.

Control flow: callers pass an existing statistics object; the wrapper returns the same object whenever requested.

State and persistence: stores a final statistics reference. Any persistence or mutability is owned by the wrapped instance.

Dependencies and integration points: implements `IOStatisticsSource`; created by `IOStatisticsBinding.wrap()`.

Risks and test signals: the wrapper does not snapshot, so consumers see live changes. Tests should cover identity preservation, null input policy, and interaction with `IOStatisticsSupport.retrieveIOStatistics()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/SourceWrappedStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StatisticDurationTracker.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StatisticDurationTracker.java

Purpose: operation duration tracker that updates an `IOStatisticsStore` counter plus min/mean/max duration metrics when closed.

Important APIs, types, and functions: constructors with default and explicit count, `failed()`, `close()`, and `toString()`.

Control flow: constructor increments the base counter when count is positive. `failed()` marks the tracker. `close()` finalizes the inherited `OperationDuration`, switches to `key + ".failures"` when failed, increments the failure counter, and adds a timed operation under the chosen prefix.

State and persistence: stores the target store, key, and failure flag. Duration timing is inherited runtime state. Updates land in the store; snapshots persist them separately.

Dependencies and integration points: extends `OperationDuration` and implements `DurationTracker`. Used by `IOStatisticsStoreImpl.trackDuration()` and duration helpers in `IOStatisticsBinding`.

Risks and test signals: `close()` is not guarded against double close, so repeated close can double count unless `OperationDuration` prevents it. Tests should cover success/failure metrics, count zero behavior, suffix names, duration value updates, and double-close expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StatisticDurationTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StorageStatisticsFromIOStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StorageStatisticsFromIOStatistics.java

Purpose: adapter that publishes IOStatistics counters through Hadoop's older `StorageStatistics` API.

Important APIs, types, and functions: constructor with name, scheme, and IOStatistics; overrides for `getScheme()`, `getLong()`, `isTracked()`, `reset()`, and `getLongStatistics()`.

Control flow: `getLong()` reads from the source counter map. Iteration over long statistics converts current IOStatistics counter entries into `StorageStatistics.LongStatistic` objects. Reset is a no-op because the adapter does not own mutable state.

State and persistence: stores name/scheme via superclass and a source IOStatistics reference. It is a live adapter, not a snapshot.

Dependencies and integration points: depends on `StorageStatistics` and `IOStatistics`; created by `IOStatisticsBinding.publishAsStorageStatistics()`. It bridges newer IOStatistics into existing Hadoop metrics consumers.

Risks and test signals: only counters are published, not gauges/min/max/means. Tests should cover missing keys, live counter updates, iterator contents, scheme propagation, and reset no-op behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StorageStatisticsFromIOStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StubDurationTracker.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StubDurationTracker.java

Purpose: singleton no-op `DurationTracker` for disabled or absent duration statistics.

Important APIs, types, and functions: static `STUB_DURATION_TRACKER`, `failed()`, `close()`, and `asDuration()`.

Control flow: failure and close do nothing; duration returns a neutral value.

State and persistence: no mutable state and no persistence.

Dependencies and integration points: used by `IOStatisticsSupport.stubDurationTracker()` and `IOStatisticsBinding.createTracker()` when no factory is supplied.

Risks and test signals: callers must not expect failure or close side effects. Tests should cover singleton identity, no-op methods, and duration value contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StubDurationTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StubDurationTrackerFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StubDurationTrackerFactory.java

Purpose: singleton no-op factory that always returns the stub duration tracker.

Important APIs, types, and functions: static `STUB_DURATION_TRACKER_FACTORY` and `trackDuration()`.

Control flow: any key/count request returns `StubDurationTracker.STUB_DURATION_TRACKER`.

State and persistence: no mutable state and no persistence.

Dependencies and integration points: implements `DurationTrackerFactory`; returned by `IOStatisticsSupport.stubDurationTrackerFactory()`.

Risks and test signals: key and count are intentionally ignored. Tests should cover singleton identity and repeated calls returning the same no-op tracker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StubDurationTrackerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/WrappedIOStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/WrappedIOStatistics.java

Purpose: base class that delegates `IOStatistics` map accessors to a wrapped statistics instance and allows the wrapped instance to be installed later.

Important APIs, types, and functions: constructor, protected `setWrapped()`, protected `getWrapped()`, and map accessors for all statistic categories.

Control flow: subclasses either pass the wrapped instance at construction or call `setWrapped()` after building it. Accessor methods delegate to the current wrapped object.

State and persistence: stores one mutable reference to wrapped statistics. It does not own metric values directly.

Dependencies and integration points: implements `IOStatistics`; used by `IOStatisticsStoreImpl` so the store can initialize maps before exposing a dynamic view.

Risks and test signals: access before a wrapped instance is set can fail. Tests should cover late binding, delegation, replacement behavior, and null wrapped safeguards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/WrappedIOStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/package-info.java

Purpose: package-level metadata for implementation classes behind Hadoop IOStatistics.

Important APIs, types, and functions: declares package `org.apache.hadoop.fs.statistics.impl` with `@InterfaceAudience.LimitedPrivate("Filesystems")` and `@InterfaceStability.Unstable`.

Control flow: no executable flow.

State and persistence: no runtime state.

Dependencies and integration points: depends on Hadoop classification annotations. It communicates intended visibility: filesystem implementations may use these classes, but they are not a stable public API.

Risks and test signals: changing annotations affects downstream compatibility expectations rather than runtime behavior. Test signal is source/javadoc generation retaining the package annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/package-info.java

Purpose: package documentation for Hadoop IOStatistics, explaining the statistics model, naming rules, aggregation behavior, and thread-level context support.

Important APIs, types, and functions: documents statistic categories (counters, gauges, minimums, maximums, means), naming restrictions, serializable snapshots, aggregators, and thread-level collection concepts.

Control flow: no executable flow. It guides how package APIs should be used and extended.

State and persistence: no runtime state. Documentation describes which objects are serializable and how snapshots should be treated as persisted values.

Dependencies and integration points: applies Hadoop public/evolving annotations to `org.apache.hadoop.fs.statistics`. It is the high-level contract for filesystem authors and metrics consumers.

Risks and test signals: documentation drift can cause incompatible metrics additions or misunderstanding of aggregation semantics. Test signals include API docs generation and tests that enforce documented naming/aggregation expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/BlockUploadStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/BlockUploadStatistics.java

Purpose: small callback interface for tracking allocation and release of upload data blocks.

Important APIs, types, and functions: `blockAllocated()` and `blockReleased()`.

Control flow: `DataBlocks.DataBlock` subclasses call `blockAllocated()` during construction and `blockReleased()` during close/cleanup.

State and persistence: no state in the interface. Implementations usually update runtime counters or gauges.

Dependencies and integration points: used by `DataBlocks` factories and block implementations to integrate upload buffering with statistics.

Risks and test signals: missed release calls can leak active-block metrics. Tests should cover allocation/release balance for array, bytebuffer, and disk blocks, including close-before-upload and upload-close paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/BlockUploadStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/ByteBufferInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/ByteBufferInputStream.java

Purpose: `InputStream` wrapper over a `ByteBuffer` with synchronized reads, mark/reset support, close-state enforcement, and bounded seeking through `skip()`.

Important APIs, types, and functions: constructor, `close()`, `isOpen()`, `read()`, `read(byte[],int,int)`, `skip()`, `available()`, `position()`, `hasRemaining()`, `mark()`, `reset()`, `markSupported()`, and `toString()`.

Control flow: read methods verify open state, return `-1` at EOF, and advance the underlying buffer position. `skip()` treats its argument as an absolute offset from current position and rejects negative or beyond-EOF positions. `close()` nulls the buffer reference so later operations fail.

State and persistence: stores declared size and mutable buffer reference/position. No persistence; it is used as an upload stream over off-heap or pooled buffers.

Dependencies and integration points: depends on `ByteBuffer`, Hadoop `FSExceptionMessages`, preconditions, and SLF4J. Created by `DataBlocks.ByteBufferBlock.startUpload()`.

Risks and test signals: `read(byte[], offset, length)` does not explicitly reject negative offset before calculating destination capacity; ByteBuffer will still enforce bounds but error shape may vary. Tests should cover close behavior, mark/reset, EOF, zero-length reads, invalid offsets/lengths, skip boundaries, and buffer release lifecycle in `DataBlocks`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/ByteBufferInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/DataBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/DataBlocks.java

Purpose: upload-buffer abstraction for filesystem output streams, supporting heap byte arrays, direct byte buffers, and temporary disk files as multipart/block upload staging backends.

Important APIs, types, and functions: constants for backend names, `validateWriteArgs()`, `createFactory()`, `BlockUploadData`, abstract `BlockFactory`, abstract `DataBlock`, and concrete array, byte-buffer, and disk factories/blocks.

Control flow: callers choose a factory by configuration name. A `DataBlock` starts in `Writing`, accepts bounded writes until full, transitions through `startUpload()` into `Upload`, and later closes into `Closed`. Array blocks hand off a `ByteArrayInputStream`; byte-buffer blocks flip a direct buffer into a `ByteBufferInputStream`; disk blocks flush/close a temp file and return it as upload data. `BlockUploadData.close()` closes streams, clears cached arrays, and deletes file-backed buffers.

State and persistence: each block tracks state, index, size/capacity, and optional allocation statistics. Disk blocks create local temporary files and delete them during cleanup. ByteBuffer blocks borrow from `DirectBufferPool` and must return buffers on close.

Dependencies and integration points: depends on Hadoop configuration, `LocalDirAllocator`, `DirectBufferPool`, commons IO, Hadoop IO cleanup, and `BlockUploadStatistics`. Used by object-store output stream implementations such as S3A multipart upload buffering.

Risks and test signals: resource cleanup is the main risk: disk temp files and direct buffers must be released exactly once across success and failure paths. Tests should cover state transitions, write bounds, close-before-upload, close-after-upload, byte-array caching, disk file deletion, direct-buffer outstanding count, and invalid backend names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/DataBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/EtagChecksum.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/EtagChecksum.java

Purpose: Hadoop `FileChecksum` implementation that represents an object-store ETag as checksum bytes.

Important APIs, types, and functions: constructors, `getAlgorithmName()`, `getLength()`, `getBytes()`, `write()`, `readFields()`, `equals()`, `hashCode()`, and `toString()` methods.

Control flow: the ETag string is encoded as UTF-8 bytes for checksum APIs and serialized through Hadoop writable methods. It is intended for change detection rather than cross-store content equivalence.

State and persistence: stores a mutable ETag string, defaulting to empty. Persists through Hadoop `Writable` serialization.

Dependencies and integration points: extends `FileChecksum`; uses `DataInput`, `DataOutput`, and UTF-8. Used by object-store filesystems that expose remote ETag metadata through Hadoop checksum APIs.

Risks and test signals: ETags are not cryptographic content checksums and multipart/object-store semantics vary. Tests should cover empty/default values, serialization round trip, UTF-8 bytes, equality/hash, and algorithm name compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/EtagChecksum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/LogExactlyOnce.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/LogExactlyOnce.java

Purpose: helper that logs a warning message only once per helper instance, suppressing repeated noisy warnings.

Important APIs, types, and functions: constructor accepting an SLF4J `Logger`, `warn(String, Object...)`, and reset/testing support if present.

Control flow: first warning call logs through the wrapped logger; later calls are suppressed by an atomic flag.

State and persistence: holds logger reference and in-memory boolean/atomic logged state. No persistence.

Dependencies and integration points: used by `HttpReferrerAuditHeader` to avoid flooding logs when URI/header construction repeatedly fails.

Risks and test signals: suppressing repeated messages can hide recurring failures after the first occurrence. Tests should cover first-call logging, later suppression, thread safety under concurrent warnings, and reset/test hooks if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/LogExactlyOnce.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/ActiveThreadSpanSource.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/ActiveThreadSpanSource.java

Purpose: generic interface for filesystem implementations that can expose the currently active audit span for the calling thread.

Important APIs, types, and functions: `getActiveAuditSpan()` returning a non-null span of type `T extends AuditSpan`.

Control flow: callers can capture the active span and propagate it into other threads or asynchronous work; the returned span may be invalid but must not be null.

State and persistence: no state in the interface. Implementations usually read thread-local or filesystem-specific active span state.

Dependencies and integration points: depends on `AuditSpan`. Used by audited filesystems to bridge thread-local span context into async operations.

Risks and test signals: returning null violates the contract and can break propagation code. Tests should cover inactive-span behavior, non-null guarantee, and cross-thread propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/ActiveThreadSpanSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditEntryPoint.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditEntryPoint.java

Purpose: source-retention marker annotation identifying filesystem methods that create and activate audit spans.

Important APIs, types, and functions: annotation type with `@Documented` and `@Retention(RetentionPolicy.SOURCE)`.

Control flow: no runtime flow because retention is source-only. It documents method-level audit boundaries and discourages nested entry-point calls.

State and persistence: no runtime state. It persists only in source and generated documentation.

Dependencies and integration points: used by filesystem source code and reviewers/static checks to identify audit entry points.

Risks and test signals: because retention is source-only, runtime reflection cannot enforce it. Test signals are source-level checks, code review, and documentation generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditEntryPoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditSpan.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditSpan.java

Purpose: private unstable interface representing an audit span that can be activated/deactivated in a thread and carry operation metadata.

Important APIs, types, and functions: `getSpanId()`, `getOperationName()`, `getTimestamp()`, `activate()`, `deactivate()`, default `close()`, default `isValidSpan()`, and default `set()`.

Control flow: spans are activated for filesystem operations and remain active until deactivated/closed. `close()` delegates to `deactivate()` for try-with-resources use; implementations may expose invalid fallback spans.

State and persistence: no state in the interface. Implementations carry span IDs, operation names, timestamps, attributes, and thread activation state.

Dependencies and integration points: extends `Closeable` and is used by `AuditSpanSource`, `ActiveThreadSpanSource`, `AuditingFunctions`, and object-store auditors.

Risks and test signals: there is no span stack, so activating a span replaces previous active context in implementations. Tests should cover close/deactivate semantics, invalid spans, attribute setting, unique IDs, and multi-thread activation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditSpan.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditSpanSource.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditSpanSource.java

Purpose: factory interface for creating audit spans for filesystem operations.

Important APIs, types, and functions: `createSpan(String operation, @Nullable String path1, @Nullable String path2)`.

Control flow: filesystem entry points call `createSpan()` with operation name and relevant paths, then activate the returned span around work.

State and persistence: no state in the interface. Implementations may allocate span IDs, timestamps, and attach context for audit logs.

Dependencies and integration points: depends on `AuditSpan`, nullable annotations, and `IOException`. Operation names should come from `StoreStatisticNames` or `StreamStatisticNames`.

Risks and test signals: failures can throw `IOException` before an operation runs. Tests should cover path nullability, operation-name propagation, error handling, and returned span validity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditSpanSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditingFunctions.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditingFunctions.java

Purpose: static helpers that wrap callables/functions/invocations so a supplied audit span is active when the wrapped work executes.

Important APIs, types, and functions: overloaded `withinAuditSpan()` methods for `CallableRaisingIOE`, `InvocationRaisingIOE`, `FunctionRaisingIOE`, and Java `Callable`.

Control flow: if the span is null, the original operation is returned. Otherwise, the wrapper calls `auditSpan.activate()` immediately before invoking the operation. It intentionally does not deactivate afterward so chained operations in the same thread keep the span active.

State and persistence: stateless utility class. Span state is managed by the supplied `AuditSpan` implementation.

Dependencies and integration points: depends on Hadoop functional interfaces and Java callable. Used when dispatching filesystem work across asynchronous or callback boundaries while preserving audit context.

Risks and test signals: comments mention deactivate around invocation, but implementation does not deactivate; tests should lock in the intended active-span propagation semantics. Also test null span passthrough, exception propagation, and activation on every invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/AuditingFunctions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/HttpReferrerAuditHeader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/HttpReferrerAuditHeader.java

Purpose: builder and runtime generator for Hadoop audit data encoded as an HTTP Referer header, including static attributes, dynamic per-request attributes, global audit context, filtering, escaping, and parsing helpers.

Important APIs, types, and functions: `REFERRER_PATH_FORMAT`, `buildHttpReferrer()`, `set()`, getters, `escapeToPathElement()`, `maybeStripWrappedQuotes()`, `extractQueryParameters()`, static `builder()`, and builder methods for context ID, operation name, span ID, paths, attributes, evaluated suppliers, global context values, and filters.

Control flow: construction copies builder maps into thread-safe structures, adds operation/path/span query attributes, overlays global context values with `putIfAbsent()`, and eagerly builds an initial header for validation. `buildHttpReferrer()` copies attributes, evaluates suppliers in the current thread, filters keys, joins query pairs, and constructs a URI with origin host and audit path. URI syntax failures and supplier/runtime failures are logged at most once and return an empty header. Parsing strips wrapping quotes and uses Apache HTTP client URL utilities.

State and persistence: stores immutable identity fields plus concurrent maps for static attributes and evaluated suppliers. `set()` can mutate attributes after construction. The generated header is a string emitted to HTTP requests and external logs.

Dependencies and integration points: depends on `CommonAuditContext`, audit constants, Apache HTTP `URLEncodedUtils`, Guava `ImmutableSet`, commons-lang `StringUtils`, and `LogExactlyOnce`. Tests are noted in S3A audit test classes because S3 logs consume the header.

Risks and test signals: query strings are built as raw `key=value` pairs before `URI` encoding, so special characters, null supplier values, and duplicate keys need coverage. Tests should cover dynamic evaluation per thread, filtering, global context precedence, parse round trip, quote stripping, escape rules for `/` and `@`, malformed attributes returning empty header, and once-only warning behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/HttpReferrerAuditHeader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/package-info.java

Purpose: package metadata for unstable private store audit support APIs.

Important APIs, types, and functions: applies Hadoop private/unstable annotations to `org.apache.hadoop.fs.store.audit`.

Control flow: no executable flow.

State and persistence: no runtime state.

Dependencies and integration points: depends on Hadoop classification annotations. It frames the audit API as internal support for filesystem/store implementations.

Risks and test signals: compatibility expectations are lower than public APIs, but downstream stores may still depend on them. Test signal is javadoc/source generation with the intended annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/package-info.java

Purpose: package metadata for private/unstable filesystem store support classes.

Important APIs, types, and functions: applies Hadoop private/unstable annotations to `org.apache.hadoop.fs.store`.

Control flow: no executable flow.

State and persistence: no runtime state.

Dependencies and integration points: depends on Hadoop classification annotations. It covers helpers such as upload data blocks, ETag checksums, and logging utilities used by object-store filesystems.

Risks and test signals: package annotation changes affect API compatibility expectations. Test signal is documentation/source generation preserving private unstable classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/package-info.java -->
