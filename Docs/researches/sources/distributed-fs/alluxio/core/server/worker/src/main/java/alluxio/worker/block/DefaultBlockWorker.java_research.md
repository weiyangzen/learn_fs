## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/DefaultBlockWorker.java

### Purpose
`DefaultBlockWorker` is the top-level block worker service implementation. It owns block-store access, master clients, heartbeat reporting, session cleanup, pin-list sync, optional storage health checks, optional internal FUSE mount, cache request handling, configuration reporting, metrics registration, and checksum calculation.

### Important APIs and Types
- Constructor wires `BlockMasterClientPool`, `FileSystemMasterClient`, `Sessions`, `BlockStore`, worker id reference, event listeners, cache manager, fuse manager, and checksum resources.
- Lifecycle: `start(WorkerNetAddress)`, `setupBlockMasterSync`, `askForWorkerId`, `stop`.
- Block operations: `createBlock`, `createBlockWriter`, `createBlockReader`, `createUfsBlockReader`, `commitBlock`, `abortBlock`, `removeBlock`, `requestSpace`, `commitBlockInUfs`.
- Metadata/reporting: `getReport`, `getStoreMeta`, `getStoreMetaFull`, `getConfiguration`, `getWhiteList`, `updatePinList`, `getFileInfo`.
- Cache/load: deprecated `asyncCache`, `cache(CacheRequest)`, `load(List<Block>, UfsReadOptions)`.
- Admin/metrics: `freeWorker`, `clearMetrics`, nested `Metrics.registerGauges`, nested `StorageChecker`, `calculateBlockChecksum`.

### Control Flow
Startup obtains a worker id from the block master with retry, starts block-master sync, starts pin-list heartbeat, starts session cleaner, optionally starts storage checker and internal FUSE. Most public block APIs delegate to `mBlockStore`, translating resource-exhausted create failures into messages with debug URLs when the worker address is known. `cache` is skipped for `PagedBlockStore`; file store cache is delegated to `CacheRequestManager`. `load` creates temp blocks in the top tier, schedules UFS reads through `UfsIOManager`, appends direct buffers to block writers, commits, and returns accumulated per-block `BlockStatus` errors. Checksum calculation reads blocks in parallel, computes CRC64 in 8 MiB chunks, optionally rate-limits, and returns a map of checksums.

### State and Persistence
Worker state includes master clients, sessions, event reporters, worker id/address, block store, cache manager, FUSE manager, checksum executor, and metric gauges. Persistent effects are through the block store and UFS/master RPCs: block files, metadata, master commit notifications, UFS commit notifications, and storage cleanup in `freeWorker`.

### Dependencies and Integration Points
It sits at the center of worker integration: `BlockMasterSync`, `PinListSync`, `SessionCleaner`, `BlockStore`, `FileSystemMasterClient`, `FileSystemContext`, gRPC executors, `MetricsSystem`, optional `FuseManager`, and client/server block IO handlers.

### Risks
- `Metrics.WORKER_ACTIVE_CLIENTS` is incremented/decremented across several paths; mismatches can occur on exceptional close/abort paths.
- `freeWorker` recursively deletes all entries in configured worker storage dirs and must only be called for administrative cleanup.
- `load` allocates a direct buffer of full block size per block, so large or many blocks can exhaust direct memory despite retry.
- Checksum results are written into a plain `HashMap` from multiple futures, which is not thread-safe.
- `getConfiguration` explicitly does not guarantee a single consistent cluster/path snapshot.

### Test Signals
`DefaultBlockWorkerTestBase`, `DefaultBlockWorkerExceptionTest`, `BlockWorkerMetricsTest`, block grpc handler tests, and stream reader tests cover worker construction, exception handling, metrics, cache/read/write paths, and UFS fallback behavior.
