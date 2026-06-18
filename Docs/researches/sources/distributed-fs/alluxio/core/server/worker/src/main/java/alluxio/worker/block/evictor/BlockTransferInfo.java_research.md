# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/BlockTransferInfo.java

Purpose: Immutable transfer-order value object describing a block move or a two-block swap.

Important APIs: `createMove`, `createSwap`, getters for source/destination locations and block IDs, `isSwap`, and `toString`.

Control flow: Move instances set destination block ID to an invalid sentinel; swap instances include both IDs. `BlockTransferExecutor` branches on `isSwap` to perform one or two moves and enable reserved space for swaps.

State and persistence: Thread-safe immutable fields only. No persistence.

Dependencies and integration: Used by eviction plans and tier-management tasks as the common transfer command structure.

Risks and test signals: The sentinel value is `-1`, so negative real block IDs would be invalid elsewhere. Tests should verify move versus swap classification, location preservation, and executor behavior for each type.
