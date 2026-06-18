# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/MeanStatistic.java

Purpose: serializable value object for a mean statistic represented by sample count and sum, with mean computed on demand.

Important APIs, types, and functions: constructors, `getSum()`, `getSamples()`, `isEmpty()`, `clear()`, `setSamplesAndSum()`, `set()`, `setSum()`, `setSamples()`, `mean()`, `add()`, `addSample()`, `copy()`, `clone()`, equality, hash, and `toString()`.

Control flow: invalid nonpositive sample counts in construction reset to empty; negative sample counts in setters become zero. `add(other)` ignores empty inputs, copies non-empty values into an empty destination, or accumulates samples and sum into a non-empty destination. Equality treats all empty stats as equivalent regardless of sum.

State and persistence: holds two synchronized longs, `samples` and `sum`, and is Java/Jackson serializable. It is mutable and should not be used as a map key while being updated.

Dependencies and integration points: depends on Jackson `JsonIgnore` and Hadoop interface annotations. Used by all IOStatistics mean maps, snapshots, stores, and dynamic statistics.

Risks and test signals: add synchronizes on both objects and can be sensitive to concurrent access patterns if callers create cycles. Tests should cover empty equality, negative sample normalization, copy isolation, concurrent sample addition, JSON round trip, and mean precision.
