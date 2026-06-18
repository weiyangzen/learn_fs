## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataManager.java

### Purpose
`BlockMetadataManager` is the central non-thread-safe owner of local tiered-storage metadata. It constructs configured storage tiers, locates block and temp block metadata, mutates directory accounting on create/commit/abort/move/remove/resize, and supplies `BlockStoreMeta` snapshots for worker registration and heartbeats.

### Important APIs and Types
- `WORKER_STORAGE_TIER_ASSOC` maps configured worker tier ordinals to aliases.
- `createBlockMetadataManager()` constructs a configured manager.
- `getBlockIterator()` exposes the configured block iteration/annotation provider for eviction and management tasks.
- Temp-block lifecycle: `addTempBlockMeta`, `abortTempBlockMeta`, `commitTempBlockMeta`, `cleanupSessionTempBlocks`, `resizeTempBlockMeta`.
- Lookup and snapshots: `getAvailableBytes`, `getBlockMeta`, `getTempBlockMeta`, `getSessionTempBlocks`, `getBlockStoreMeta`, `getBlockStoreMetaFull`.
- Topology: `getTier`, `getDir`, `getTiers`, `getTiersBelow`, `getStorageTierAssoc`.
- Mutations: `moveBlockMeta` and `removeBlockMeta`.

### Control Flow
The private constructor builds each `DefaultStorageTier` from tier configuration, indexes tiers by alias, then chooses a block iterator. Deprecated evictor class settings are translated to `LRUAnnotator` or `LRFUAnnotator`; custom legacy evictors are wrapped by `EmulatingBlockIterator`; otherwise `DefaultBlockIterator` is used. Commit converts a `TempBlockMeta` into `DefaultBlockMeta`, removes it from the temp map, and adds it to the committed block map in the same `StorageDir`. Move removes the source block metadata, removes the destination temp placeholder, and creates a new committed metadata entry in the destination dir.

### State and Persistence
State is in-memory metadata for configured tiers and directories. The underlying `StorageDir` implementations reflect worker storage directories and block files, but this class itself only maintains metadata accounting. It must be guarded by `TieredBlockStore` metadata locks for thread safety.

### Dependencies and Integration Points
It integrates with `TieredBlockStore` for all local metadata operations, `DefaultBlockStoreMeta` for snapshots, block annotators/iterators for eviction order, allocators/evictors through `BlockMetadataView`, and configuration keys for tier layout and deprecated eviction behavior.

### Risks
- Linear scans over all tiers/dirs for block lookup and existence checks can be expensive with many directories or blocks.
- The constructor mutates global configuration when translating deprecated evictors, which can surprise later components.
- `moveBlockMeta` assumes physical file movement has already succeeded; rollback is handled by the caller, and `TieredBlockStore` currently documents limited rollback.
- No internal locking; accidental direct concurrent use would corrupt metadata/accounting.

### Test Signals
`BlockMetadataManagerTest` covers tier/dir lookup, available bytes, missing tier errors, block/temp lookup, moving metadata, and resizing temp blocks. Management-tier tests use it through `TieredBlockStoreTestUtils`.
