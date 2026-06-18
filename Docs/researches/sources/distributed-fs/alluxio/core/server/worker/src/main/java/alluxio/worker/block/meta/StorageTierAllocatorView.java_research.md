# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageTierAllocatorView.java

Purpose: Allocator-facing tier view that wraps each underlying storage directory with an allocator view.

Important APIs: Constructor taking `StorageTier` and `useReservedSpace`.

Control flow: Construction iterates the tier's storage dirs, creates `StorageDirAllocatorView` for each, and stores them by directory index.

State and persistence: View over live tier state; no persistence.

Dependencies and integration: Used by block metadata allocator views passed to `Allocator` implementations.

Risks and test signals: The view captures the directory set at construction and may not reflect later lost-storage changes. Tests should cover reserved-space flag propagation and directory indexing.
