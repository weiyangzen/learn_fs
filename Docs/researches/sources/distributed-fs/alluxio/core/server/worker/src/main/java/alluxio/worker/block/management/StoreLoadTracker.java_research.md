# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/StoreLoadTracker.java

Purpose: Abstraction for detecting user IO activity on worker storage locations.

Important APIs: `loadDetected(BlockStoreLocation... locations)`.

Control flow: Transfer execution and coordinator loops call this before background work to avoid interfering with user activity.

State and persistence: Interface only.

Dependencies and integration: Implemented by `DefaultStoreLoadTracker`; consumed by `BlockTransferExecutor` and `ManagementTaskCoordinator`.

Risks and test signals: Varargs semantics mean callers can check multiple locations in one decision. Tests should cover implementations with exact, tier, and any-tier location ranges.
