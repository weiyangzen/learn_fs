# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/DefaultStoreLoadTracker.java

Purpose: Detects active worker load by tracking open block reader and writer clients per precise storage location.

Important APIs: Constructor registers with `BlockStreamTracker`; `loadDetected`; `clientOpened`; `clientClosed`; private `locationValid`.

Control flow: Opens add clients to a concurrent set by location. Closes schedule delayed removal after `WORKER_MANAGEMENT_LOAD_DETECTION_COOL_DOWN_TIME`, leaving a cool-down window. `loadDetected` checks tracked locations that belong to any queried location range.

State and persistence: Maintains a concurrent map from exact `BlockStoreLocation` to client sets and a single-thread scheduled executor. State is in memory and can be stale if close events are lost.

Dependencies and integration: Implements `StoreLoadTracker` and `BlockClientListener`; receives events from `BlockStreamTracker`; used by `ManagementTaskCoordinator` and `BlockTransferExecutor`.

Risks and test signals: No unregister/close method appears here for the listener or scheduler. Tests should cover precise-location validation, delayed close removal, any-tier queries, concurrent clients, and stale close error handling.
