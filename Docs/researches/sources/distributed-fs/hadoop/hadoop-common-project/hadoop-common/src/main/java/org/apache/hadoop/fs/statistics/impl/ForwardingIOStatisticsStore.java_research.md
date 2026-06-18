# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/ForwardingIOStatisticsStore.java

Purpose: delegating wrapper that implements the full `IOStatisticsStore` interface by forwarding every operation to an inner store.

Important APIs, types, and functions: constructor, protected `getInnerStatistics()`, all map accessors, aggregation, setters/increments, reference getters, mean operations, reset, timed operation updates, and duration tracking.

Control flow: every public method directly calls the matching method on the inner store, preserving return values and exceptions. Subclasses can override selected behavior while retaining default forwarding.

State and persistence: holds only a final reference to the inner store. Persistent or live state is owned by the delegate.

Dependencies and integration points: depends on `IOStatisticsStore`, `MeanStatistic`, `AtomicLong`, and `Duration`. It supports decoration of statistics stores without reimplementing the contract.

Risks and test signals: a null inner store would fail later; constructor validation should be checked in use. Tests should verify exact forwarding, exception propagation, and subclass override compatibility.
