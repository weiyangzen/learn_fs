# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StatisticDurationTracker.java

Purpose: operation duration tracker that updates an `IOStatisticsStore` counter plus min/mean/max duration metrics when closed.

Important APIs, types, and functions: constructors with default and explicit count, `failed()`, `close()`, and `toString()`.

Control flow: constructor increments the base counter when count is positive. `failed()` marks the tracker. `close()` finalizes the inherited `OperationDuration`, switches to `key + ".failures"` when failed, increments the failure counter, and adds a timed operation under the chosen prefix.

State and persistence: stores the target store, key, and failure flag. Duration timing is inherited runtime state. Updates land in the store; snapshots persist them separately.

Dependencies and integration points: extends `OperationDuration` and implements `DurationTracker`. Used by `IOStatisticsStoreImpl.trackDuration()` and duration helpers in `IOStatisticsBinding`.

Risks and test signals: `close()` is not guarded against double close, so repeated close can double count unless `OperationDuration` prevents it. Tests should cover success/failure metrics, count zero behavior, suffix names, duration value updates, and double-close expectations.
