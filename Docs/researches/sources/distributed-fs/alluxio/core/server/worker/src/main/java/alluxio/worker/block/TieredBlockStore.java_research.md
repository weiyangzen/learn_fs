## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/TieredBlockStore.java

### Purpose
`TieredBlockStore` is the thread-safe local block-store implementation for file-backed tiered worker storage. It coordinates metadata, file operations, block locks, allocation, eviction, management tasks, pin protection, event listeners, storage health removal, and session temp-block cleanup.

### Important APIs and Types
- Constructors create `BlockMetadataManager`, `BlockLockManager`, configured `Allocator`, block iterator listeners, and `ManagementTaskCoordinator`.
- Read/write lifecycle: `createBlock`, `createBlockWriter`, `requestSpace`, `commitBlock`, `commitBlockLocked`, `abortBlock`, `createBlockReader`.
- Mutation: `moveBlock`, `removeBlock`, `removeBlockInternal`, `freeSpace`, `removeDir`, `removeInaccessibleStorage`.
- Metadata: `getVolatileBlockMeta`, `getTempBlockMeta`, `getBlockStoreMeta`, `getBlockStoreMetaFull`, `hasBlockMeta`, `hasTempBlockMeta`.
- Helpers: `validateBlockIntegrityForRead`, `allocateSpace`, `createBlockMetaInternal`, `moveBlockInternal`, `getUpdatedView`.

### Control Flow
Reads acquire a read block lock, read metadata under the metadata read lock, validate the physical file, and wrap `StoreBlockReader` with metrics and a lock-closing delegating reader. Corrupt/missing zero-length files are removed before throwing block-not-exist. Creates allocate space under metadata write lock, create temp metadata, and create the temp file. Commits acquire a write block lock, convert temp metadata to committed metadata, optionally pin the parent file id, and notify listeners. Allocation first tries requested/any locations, then may call synchronized `freeSpace` to evict blocks using the block iterator and a fresh `BlockMetadataEvictorView`. Moves allocate a destination temp placeholder, physically move the file, then update metadata. Storage checker removes inaccessible dirs and reports block/storage loss.

### State and Persistence
Persistent state is local block/temp files under worker tier directories plus in-memory metadata mirroring those files. Runtime state includes metadata and block lock managers, allocator, listener list, pinned inode set, metadata read/write lock, and management task coordinator.

### Dependencies and Integration Points
It is the main `LocalBlockStore` used by `MonoBlockStore`. It integrates with metadata classes, allocators, block iterators/annotators, file utilities, event listeners (`BlockHeartbeatReporter`, `BlockMetricsReporter`), management tasks, and session cleaner.

### Risks
- The lock hierarchy is subtle: block locks protect per-block IO/metadata while metadata locks protect global structures. New code must avoid inversion and long metadata-lock IO.
- `moveBlockInternal` has a TODO for rollback after IO/metadata failures; partial physical moves can be hard to recover.
- `freeSpace` is synchronized and can delete many blocks while allocation waits.
- `createBlockFile` grants full permissions based on configured worker data permissions; security posture depends on sticky dirs and config.
- Integrity validation only fails size mismatch when actual length is zero; nonzero mismatches are logged but tolerated.

### Test Signals
`TieredBlockStore` is exercised broadly by block read/write grpc tests, `ShortCircuitBlockReadHandlerTest`, management tier task tests, `MonoBlockStoreCommitBlockTest`, `UnderFileSystemBlockReaderTest`, and metadata/allocator tests.
