## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/MonoBlockStore.java

### Purpose
`MonoBlockStore` implements the higher-level `BlockStore` contract for whole-block storage. It composes a `LocalBlockStore` with `UnderFileSystemBlockStore`, forwards local operations, reports committed blocks to the master, handles local-cache-first reads with UFS fallback, and supports asynchronous bulk UFS loading.

### Important APIs and Types
- Constructor wires local store, block master client pool, UFS manager, and worker id.
- Local delegation: create/write/read/abort/move/remove/requestSpace/metadata/pin/updatePinnedInodes.
- `commitBlock` commits locally under a returned lock, then calls `BlockMasterClient.commitBlock` and notifies listeners.
- `createUfsBlockReader` delegates to `UnderFileSystemBlockStore` and wraps close to close/release UFS access.
- `load(List<Block>, UfsReadOptions)` bulk reads through `UfsIOManager` into local blocks.
- `closeUfsBlock`, `handleException`, and `timeoutAfter` handle UFS lifecycle/load errors.

### Control Flow
Reads first try `mLocalBlockStore.createBlockReader`. If the block is absent and UFS options include a path or UFS-tier flag, it opens a UFS block reader. UFS reader close triggers `closeBlock` and `releaseAccess`; no-cache reads decrement active-client metrics when no temp block exists. Commits acquire a master client, call `commitBlockLocked`, fetch committed local metadata, report used bytes/tier/medium/block size to master, notify listeners, release client, and decrement active clients. Bulk load creates local temp blocks in top tier, reads from UFS into direct buffers with timeout/retry, appends to writers, commits, releases buffers, and records block-level errors.

### State and Persistence
State includes composed local/UFS stores, listener list, block master client pool, worker id, and a scheduled delayer for load timeouts. Persistent effects include local block files, local metadata, master block metadata commits, and UFS read stream lifecycle.

### Dependencies and Integration Points
Used by `BlockWorkerFactory` for file block store mode and by `DefaultBlockWorker`. Integrates with `UnderFileSystemBlockStore`, `UfsIOManager`, `BlockMasterClient`, `BlockStoreEventListener`, `GrpcExecutors`, direct buffer pools, and worker metrics.

### Risks
- Commit notifies master while holding the local block lock returned by `commitBlockLocked`; slow master RPC can prolong block write locking.
- Bulk `load` uses full block-size direct buffers and may stress memory.
- `mBlockStoreEventListeners` is maintained separately while listener registration also forwards to local store; listener ordering and duplicate notification semantics need care.
- `closeUfsBlock` metric decrement depends on temp metadata/no-cache state and can drift if exception paths change.

### Test Signals
`MonoBlockStoreCommitBlockTest` focuses commit/listener/master behavior. `UfsFallbackBlockWriteHandlerTest`, `ShortCircuitBlockReadHandlerTest`, and stream reader tests cover construction and read/write integration.
