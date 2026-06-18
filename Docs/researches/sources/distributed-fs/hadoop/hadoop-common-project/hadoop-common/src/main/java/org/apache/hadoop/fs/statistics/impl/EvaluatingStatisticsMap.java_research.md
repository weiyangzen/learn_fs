# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EvaluatingStatisticsMap.java

Purpose: map implementation that stores key-to-evaluator functions and evaluates values lazily when map entries are read or iterated.

Important APIs, types, and functions: function registration, `entrySet()`, `containsKey()`, `get()`, iterator-backed entries, and optional value-copy function.

Control flow: callers register evaluator functions by key. Map reads call the function with the key and optionally copy the resulting value before returning it. Iteration evaluates each entry as `next()` is consumed.

State and persistence: stores evaluator functions, not concrete values. It is live runtime state and should be snapshotted for persistence.

Dependencies and integration points: used internally by `DynamicIOStatistics` to expose dynamic maps. Mean-statistic maps use a copy function so mutable means are not directly leaked.

Risks and test signals: map methods can execute arbitrary evaluator code and throw runtime exceptions during logging or iteration. Tests should cover lazy evaluation timing, copy isolation, key lookup, iteration, unmodifiable wrapping at the `DynamicIOStatistics` layer, and duplicate registrations.
