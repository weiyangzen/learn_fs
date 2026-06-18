# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobalStorageStatistics.java

Purpose: `GlobalStorageStatistics` is a singleton registry of named `StorageStatistics` instances.

Important APIs: enum singleton `INSTANCE`, provider interface `StorageStatisticsProvider`, synchronized `get`, `put`, `reset`, and `iterator`.

Control flow and state: a `TreeMap` stores statistics by name. `put` returns an existing instance or calls the provider, rejecting null providers/results and name mismatches. `reset` calls reset on every registered statistic. Iteration snapshots the current first value then advances by `higherEntry` under synchronization, so it observes map order while tolerating concurrent synchronized modifications.

Dependencies and integration: used by filesystem implementations to publish global counters and by diagnostics/tools that enumerate or reset statistics.

Risks: provider errors are runtime failures. Iterator does not support remove. Because iteration advances by names, concurrent additions/removals may affect what is observed, though map access is synchronized.

Test signals: get null behavior, put idempotence, provider null/wrong-name failures, reset propagation, sorted iteration, no remove support, and synchronized concurrent access.
