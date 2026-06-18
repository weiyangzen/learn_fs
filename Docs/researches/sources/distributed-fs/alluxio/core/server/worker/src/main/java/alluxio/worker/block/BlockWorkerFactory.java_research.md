## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockWorkerFactory.java

### Purpose
`BlockWorkerFactory` creates and registers the concrete block worker for the process. It selects page-store or file-store implementation and wraps it in either default single-primary registration or all-master registration worker mode.

### Important APIs and Types
- Implements `WorkerFactory`.
- `isEnabled()` always returns true.
- `create(WorkerRegistry, UfsManager)` builds `BlockMasterClientPool`, shared worker id reference, block store, file-system master client, worker, and registry entry.

### Control Flow
Factory reads `WORKER_BLOCK_STORE_TYPE`. `PAGE` creates `PagedBlockStore`; `FILE` creates `MonoBlockStore(new TieredBlockStore(), ...)`. It then reads `WORKER_REGISTER_TO_ALL_MASTERS` captured in a field and creates `AllMasterRegistrationBlockWorker` or `DefaultBlockWorker`, registers it under `BlockWorker.class`, and returns it.

### State and Persistence
The factory itself holds only one config-derived boolean. Created workers own runtime state and storage persistence.

### Dependencies and Integration Points
It bridges worker bootstrap (`WorkerRegistry`) with block-store implementations, UFS manager, block master client pool, file-system master client, sessions, and worker id reference.

### Risks
- Unsupported enum values throw `UnsupportedOperationException`, so new block store types require factory edits.
- The all-master config is captured at factory instantiation; late config changes would not be reflected.

### Test Signals
Worker creation paths are covered indirectly by `DefaultBlockWorkerTestBase`, `AllMasterRegistrationBlockWorkerTest`, and page/file store tests.
