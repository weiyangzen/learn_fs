# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedTempBlockMeta.java

## Purpose
`PagedTempBlockMeta` represents a temporary paged block while it is being written.

## Important APIs, Types, and Functions
It extends `PagedBlockMeta` but overrides `getBlockSize()` to return mutable temp size. `setBlockSize()` only allows growth and rejects shrinking.

## Control Flow, State, and Persistence
The temp size starts at zero and grows as temp pages are added. It is converted to immutable `PagedBlockMeta` during commit. Persistence is in page-store temp pages, not in this object.

## Dependencies and Integration Points
It is used by `PagedBlockMetaStore.addTempBlock`, `addTempPage`, and `commit`, and by `PagedBlockStore.commitBlock`.

## Risks and Test Signals
Risks include size drift if page additions fail after updating metadata or vice versa. Tests should verify monotonic size enforcement, add-page size accumulation, and commit size matching cached temp bytes.
